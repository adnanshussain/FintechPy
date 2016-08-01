import pymssql
from datetime import datetime
import os

from sqlalchemy.sql import func, select
from webapp.app import db
from webapp.config import configs, ENVAR_FINTECH_CONFIG
from webapp.data_access.sqlalchemy_models import Market, Sector, Company, Commodity, StockPrice

def _get_mssql_connection(as_dict=False):
    config = configs[os.getenv(ENVAR_FINTECH_CONFIG)]
    return pymssql.connect(config.ARGAAM_MSSQL_SERVER_IP, config.ARGAAM_MSSQL_DB_USER_NAME,
                           config.ARGAAM_MSSQL_DB_PWD, config.ARGAAM_MSSQL_DB_NAME,
                           as_dict=as_dict)

def fetch_and_add_markets():
    conn = _get_mssql_connection(True)
    cur = conn.cursor()

    cur.execute(
        "SELECT marketid, marketnameen, marketnamear, generalindexsymbol FROM markets WHERE IsActive = 1 AND IsTrading = 1 AND DisplayInPP = 1")

    for r in cur.fetchall():
        argaam_market_id = r["marketid"]

        if db.session.query(Market).filter(Market.argaam_id == argaam_market_id).count() == 0:
            market = Market()
            market.argaam_id = r["marketid"]
            market.name_en = r["marketnameen"]
            market.name_ar = r["marketnamear"]
            market.symbol = r["generalindexsymbol"]
            db.session.add(market)

    db.session.commit()

    cur.close()
    conn.close()


def fetch_and_add_sectors():
    conn = _get_mssql_connection(True)
    cur = conn.cursor()

    cur.execute("SELECT s.sectorid, s.sectornameen, s.sectornamear FROM MarketSectors ms\
                  INNER JOIN sectors s ON ms.SectorID = s.sectorid\
                  WHERE ms.MarketID = 3 AND s.IsPublished = 1")

    for r in cur.fetchall():
        argaam_sector_id = r["sectorid"]

        if db.session.query(Sector).filter(Sector.argaam_id == argaam_sector_id).count() == 0:
            sector = Sector()
            sector.argaam_id = r["sectorid"]
            sector.name_en = r["sectornameen"]
            sector.name_ar = r["sectornamear"]
            db.session.add(sector)

    db.session.commit()

    cur.close()
    conn.close()


def fetch_and_add_companies():
    conn = _get_mssql_connection(True)
    cur = conn.cursor()

    cur.execute("""SELECT msc.marketid, msc.companyid, msc.companynameen, msc.companynamear, msc.shortnameen, msc.shortnamear,
                c.stocksymbol, c.logourl
                FROM pub.MarketSectorCompanies msc
                INNER JOIN dbo.Companies c ON c.CompanyID = msc.CompanyID
                WHERE msc.MarketStatusID = 3 AND msc.marketid = 3 AND msc.RecordStatus = 1 AND msc.IsActive = 1 AND msc.IsSuspended = 0""")

    for r in cur.fetchall():
        argaam_company_id = r["companyid"]

        if db.session.query(Company).filter(Company.argaam_id == argaam_company_id).count() == 0:
            company = Company()
            company.argaam_id = r["companyid"]
            company.name_en = r["companynameen"]
            company.name_ar = r["companynamear"]
            company.short_name_en = r["shortnameen"]
            company.short_name_ar = r["shortnamear"]
            company.market_id = db.session.query(Market).filter(Market.argaam_id == r["marketid"]).one().id
            company.stock_symbol = r["stocksymbol"]
            company.logo_url = r["logourl"]
            db.session.add(company)

    db.session.commit()

    cur.close()
    conn.close()


def fetch_and_add_commodities():
    conn = _get_mssql_connection(True)
    cur = conn.cursor()

    cur.execute("SELECT commodityid, commoditynameen, commoditynamear FROM CommodityStockPrices WHERE IsVisible = 1")

    for r in cur.fetchall():
        argaam_commodity_id = r["commodityid"]

        if db.session.query(Commodity).filter(Commodity.argaam_id == argaam_commodity_id).count() == 0:
            commodity = Commodity()
            commodity.argaam_id = argaam_commodity_id
            commodity.name_en = r["commoditynameen"]
            commodity.name_ar = r["commoditynamear"]
            db.session.add(commodity)

    db.session.commit()

    cur.close()
    conn.close()


def fetch_and_add_commodity_prices():
    conn = _get_mssql_connection()
    cur = conn.cursor()

    # get all commodities registered with fintech db, along with their last (most recent) archive date
    subquery = select(
        [StockPrice.stock_entity_id, StockPrice.stock_entity_argaam_id, func.max(StockPrice.for_date).label('for_date'),
         StockPrice.close]) \
        .where(StockPrice.stock_entity_type_id == 2) \
        .group_by(StockPrice.stock_entity_id).alias("sp")

    # http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
    commodities_with_last_entry = db.session.query(Commodity.id, Commodity.argaam_id, subquery.c.for_date,
                                                   subquery.c.close) \
        .outerjoin(subquery, Commodity.id == subquery.c.stock_entity_id).all()

    # foreach commodity get the stock price archive from Argaam DB
    for index, (commodity_id, argaam_id, last_entry, close) in enumerate(commodities_with_last_entry):
        print("Processing commodity #%s" % (index + 1,),
              db.session.query(Commodity.name_en).filter(Commodity.id == commodity_id).first())
        sql = """
              SELECT cspa.ForDate, cspa.[Open], cspa.[Close], cspa.[Min], cspa.[Max]
              FROM CommodityStockPricesArchive cspa INNER JOIN
              (SELECT max(CommodityStockPriceArchiveID) CommodityStockPriceArchiveID FROM CommodityStockPricesArchive
              WHERE CommodityID = %d GROUP BY ForDate, CommodityID) cspa2 ON cspa.CommodityStockPriceArchiveID = cspa2.CommodityStockPriceArchiveID
              WHERE cspa.[Close] <> 0
        """
        if last_entry is not None:
            sql += " and fordate > %s "
            params = (argaam_id, last_entry)
        else:
            params = (argaam_id,)

        sql += " order by fordate asc;"

        # print(sql)
        cur.execute(sql, params)

        commodity_prices = cur.fetchall()

        for index in range(0, len(commodity_prices)):
            for_date = datetime.strptime(commodity_prices[index][0], "%Y-%m-%d")
            sp = StockPrice()
            sp.stock_entity_type_id = 2  # commodity
            sp.stock_entity_id = commodity_id
            sp.stock_entity_argaam_id = argaam_id
            sp.for_date = for_date
            sp.year = for_date.year
            sp.month = for_date.month
            sp.open = commodity_prices[index][1]
            sp.close = commodity_prices[index][2]
            sp.min = commodity_prices[index][3]
            sp.max = commodity_prices[index][4]

            if index == 0 and close is None:
                sp.change = sp.change_percent = 0
            else:
                sp.change = sp.close - close
                sp.change_percent = ((sp.close - close) / close) * 100

            # use for next iteration
            close = sp.close

            db.session.add(sp)

        db.session.commit()

    cur.close()
    conn.close()


def fetch_and_add_company_prices():
    conn = _get_mssql_connection()
    cur = conn.cursor()

    # get all companies registered with fintech db, along with their last (most recent) archive date
    subquery = select([StockPrice.stock_entity_id, StockPrice.stock_entity_argaam_id,
                       func.max(StockPrice.for_date).label('for_date'), StockPrice.close]) \
        .where(StockPrice.stock_entity_type_id == 1) \
        .group_by(StockPrice.stock_entity_id).alias("sp")

    # http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
    companies_with_last_entry = db.session.query(Company.id, Company.argaam_id, subquery.c.for_date,
                                              subquery.c.close) \
        .outerjoin(subquery, Company.id == subquery.c.stock_entity_id).all()

    # foreach company get the stock price archive from Argaam DB
    for index, (company_id, argaam_id, last_entry, close) in enumerate(companies_with_last_entry):
        print("Processing company #%s" % (index + 1,),
              db.session.query(Company.name_en).filter(Company.id == company_id).first())
        sql = """
                SELECT cspa.ForDate, cspa.[Open], cspa.[Close], cspa.[Min], cspa.[Max], cspa.[Volume], cspa.[Amount]
                FROM CompanyStockPricesArchive cspa
                WHERE cspa.companyid = %d
              """
        if last_entry is not None:
            sql += " and fordate > %s "
            params = (argaam_id, last_entry)
        else:
            params = (argaam_id,)

        sql += " order by fordate asc;"

        cur.execute(sql, params)

        company_prices = cur.fetchall()

        for index in range(0, len(company_prices)):
            for_date = datetime.strptime(company_prices[index][0], "%Y-%m-%d")
            sp = StockPrice()
            sp.stock_entity_type_id = 1  # company
            sp.stock_entity_id = company_id
            sp.stock_entity_argaam_id = argaam_id
            sp.for_date = for_date
            sp.year = for_date.year
            sp.month = for_date.month
            sp.open = company_prices[index][1]
            sp.close = company_prices[index][2]
            sp.min = company_prices[index][3]
            sp.max = company_prices[index][4]
            sp.volume = company_prices[index][5]
            sp.amount = company_prices[index][6]

            if index == 0 and close is None:
                sp.change = sp.change_percent = 0
            else:
                sp.change = sp.close - close
                sp.change_percent = ((sp.close - close) / close) * 100

            # use for next iteration
            close = sp.close

            db.session.add(sp)

        db.session.commit()

    cur.close()
    conn.close()


def fetch_and_add_market_prices():
    conn = _get_mssql_connection()
    cur = conn.cursor()

    # get all markets registered with fintech db, along with their last (most recent) archive date
    subquery = select([StockPrice.stock_entity_id, StockPrice.stock_entity_argaam_id,
                       func.max(StockPrice.for_date).label('for_date'), StockPrice.close]) \
        .where(StockPrice.stock_entity_type_id == 3) \
        .group_by(StockPrice.stock_entity_id).alias("sp")

    # http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
    markets_with_last_entry = db.session.query(Market.id, Market.argaam_id, subquery.c.for_date,
                                            subquery.c.close) \
        .outerjoin(subquery, Market.id == subquery.c.stock_entity_id).all()

    # foreach market get the stock price archive from Argaam DB
    for index, (market_id, argaam_id, last_entry, close) in enumerate(markets_with_last_entry):
        print("Processing market #%s" % (index + 1,),
              db.session.query(Market.name_en).filter(Market.id == market_id).first())
        sql = """
                SELECT spa.ForDate, spa.[Open], spa.[Close], spa.[Min], spa.[Max], spa.[Volume], spa.[Amount]
                FROM MarketStockPricesArchive spa
                WHERE spa.MarketID = %d
                AND spa.[close] <> 0
              """
        if last_entry is not None:
            sql += " and fordate > %s "
            params = (argaam_id, last_entry)
        else:
            params = (argaam_id,)

        sql += " order by fordate asc;"

        cur.execute(sql, params)

        market_prices = cur.fetchall()

        for index in range(0, len(market_prices)):
            for_date = datetime.strptime(market_prices[index][0], "%Y-%m-%d")
            sp = StockPrice()
            sp.stock_entity_type_id = 3  # market
            sp.stock_entity_id = market_id
            sp.stock_entity_argaam_id = argaam_id
            sp.for_date = for_date
            sp.year = for_date.year
            sp.month = for_date.month
            sp.open = market_prices[index][1]
            sp.close = market_prices[index][2]
            sp.min = market_prices[index][3]
            sp.max = market_prices[index][4]
            sp.volume = market_prices[index][5]
            sp.amount = market_prices[index][6]

            if index == 0 and close is None:
                sp.change = sp.change_percent = 0
            else:
                sp.change = sp.close - close
                sp.change_percent = ((sp.close - close) / close) * 100

            # use for next iteration
            close = sp.close

            db.session.add(sp)

        db.session.commit()

    cur.close()
    conn.close()


def fetch_and_add_sector_prices():
    conn = _get_mssql_connection()
    cur = conn.cursor()

    # get all sectors registered with fintech db, along with their last (most recent) archive date
    subquery = select(
        [StockPrice.stock_entity_id, StockPrice.stock_entity_argaam_id, func.max(StockPrice.for_date).label('for_date'),
         StockPrice.close]) \
        .where(StockPrice.stock_entity_type_id == 4) \
        .group_by(StockPrice.stock_entity_id).alias("sp")

    # http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
    sectors_with_last_entry = db.session.query(Sector.id, Sector.argaam_id, subquery.c.for_date, subquery.c.close) \
        .outerjoin(subquery, Sector.id == subquery.c.stock_entity_id).all()

    # foreach commodity get the stock price archive from Argaam DB
    for index, (sector_id, argaam_id, last_entry, close) in enumerate(sectors_with_last_entry):
        print("Processing sector #%s" % (index + 1,),
              db.session.query(Sector.name_en).filter(Sector.id == sector_id).first())
        sql = """
                SELECT spa.ForDate, spa.[Open], spa.[Close], spa.[Min], spa.[Max], spa.[Volume], spa.[Amount]
                FROM SectorStockPricesArchive spa INNER JOIN
                (SELECT max(SectorStockPriceArchiveID) SectorStockPriceArchiveID FROM SectorStockPricesArchive WHERE SectorID = %d GROUP BY ForDate, SectorID) spa2
                ON spa.SectorStockPriceArchiveID = spa2.SectorStockPriceArchiveID
                WHERE spa.[Close] <> 0
              """
        if last_entry is not None:
            sql += " and fordate > %s "
            params = (argaam_id, last_entry)
        else:
            params = (argaam_id,)

        sql += " order by fordate asc;"

        # print(sql)
        cur.execute(sql, params)

        sector_prices = cur.fetchall()

        for index in range(0, len(sector_prices)):
            for_date = datetime.strptime(sector_prices[index][0], "%Y-%m-%d")
            sp = StockPrice()
            sp.stock_entity_type_id = 4  # sector
            sp.stock_entity_id = sector_id
            sp.stock_entity_argaam_id = argaam_id
            sp.for_date = for_date
            sp.year = for_date.year
            sp.month = for_date.month
            sp.open = sector_prices[index][1]
            sp.close = sector_prices[index][2]
            sp.min = sector_prices[index][3]
            sp.max = sector_prices[index][4]
            sp.volume = sector_prices[index][5]
            sp.amount = sector_prices[index][6]

            if index == 0 and close is None:
                sp.change = sp.change_percent = 0
            else:
                sp.change = sp.close - close
                sp.change_percent = ((sp.close - close) / close) * 100

            # use for next iteration
            close = sp.close

            db.session.add(sp)

        db.session.commit()

    cur.close()
    conn.close()


print(__name__, ' got executed')

fetch_and_add_markets()
fetch_and_add_sectors()
fetch_and_add_companies()
fetch_and_add_commodities()

fetch_and_add_sector_prices()
fetch_and_add_market_prices()
fetch_and_add_company_prices()
fetch_and_add_commodity_prices()
