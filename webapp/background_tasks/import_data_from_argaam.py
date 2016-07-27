import pymssql
from webapp.config import _ARGAAM_MSSQL_SERVER_IP, _ARGAAM_MSSQL_DB_USER_NAME, _ARGAAM_MSSQL_DB_PWD, _ARGAAM_MSSQL_DB_NAME
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func, and_, select
from webapp.sqlalchemy_models import DbSession, Market, Sector, Company, Commodity, StockPrice
from datetime import datetime

def _get_connection(as_dict=False):
    return pymssql.connect(_ARGAAM_MSSQL_SERVER_IP, _ARGAAM_MSSQL_DB_USER_NAME,\
                           _ARGAAM_MSSQL_DB_PWD, _ARGAAM_MSSQL_DB_NAME,\
                           as_dict=as_dict)

def fetch_and_add_markets():
    conn = _get_connection(True)
    cur = conn.cursor()

    cur.execute("select marketid, marketnameen, marketnamear, generalindexsymbol from markets where IsActive = 1 and IsTrading = 1 and DisplayInPP = 1")

    session = DbSession()

    for r in cur.fetchall():
        argaam_market_id = r["marketid"]

        if session.query(Market).filter(Market.argaam_id == argaam_market_id).count() == 0:
            market = Market()
            market.argaam_id = r["marketid"]
            market.name_en = r["marketnameen"]
            market.name_ar = r["marketnamear"]
            market.symbol = r["generalindexsymbol"]
            session.add(market)

    session.commit()

    cur.close()
    conn.close()

def fetch_and_add_sectors():
    conn = _get_connection(True)
    cur = conn.cursor()

    cur.execute("select s.sectorid, s.sectornameen, s.sectornamear from MarketSectors ms\
                  inner join sectors s on ms.SectorID = s.sectorid\
                  where ms.MarketID = 3 and s.IsPublished = 1")

    session = DbSession()

    for r in cur.fetchall():
        argaam_sector_id = r["sectorid"]

        if session.query(Sector).filter(Sector.argaam_id == argaam_sector_id).count() == 0:
            sector = Sector()
            sector.argaam_id = r["sectorid"]
            sector.name_en = r["sectornameen"]
            sector.name_ar = r["sectornamear"]
            session.add(sector)

    session.commit()

    cur.close()
    conn.close()

def fetch_and_add_companies():
    conn = _get_connection(True)
    cur = conn.cursor()

    cur.execute("""select msc.marketid, msc.companyid, msc.companynameen, msc.companynamear, msc.shortnameen, msc.shortnamear,
                c.stocksymbol, c.logourl
                from pub.MarketSectorCompanies msc
                inner join dbo.Companies c on c.CompanyID = msc.CompanyID
                where msc.MarketStatusID = 3 and msc.marketid = 3 and msc.RecordStatus = 1 and msc.IsActive = 1 and msc.IsSuspended = 0""")

    session = DbSession()

    for r in cur.fetchall():
        argaam_company_id = r["companyid"]

        if session.query(Company).filter(Company.argaam_id == argaam_company_id).count() == 0:
            company = Company()
            company.argaam_id = r["companyid"]
            company.name_en = r["companynameen"]
            company.name_ar = r["companynamear"]
            company.short_name_en = r["shortnameen"]
            company.short_name_ar = r["shortnamear"]
            company.market_id = session.query(Market).filter(Market.argaam_id == r["marketid"]).one().id
            company.stock_symbol = r["stocksymbol"]
            company.logo_url = r["logourl"]
            session.add(company)

    session.commit()

    cur.close()
    conn.close()

def fetch_and_add_commodities():
    conn = _get_connection(True)
    cur = conn.cursor()

    cur.execute("select commodityid, commoditynameen, commoditynamear from CommodityStockPrices where IsVisible = 1")

    session = DbSession()

    for r in cur.fetchall():
        argaam_commodity_id = r["commodityid"]

        if session.query(Commodity).filter(Commodity.argaam_id == argaam_commodity_id).count() == 0:
            commodity = Commodity()
            commodity.argaam_id = argaam_commodity_id
            commodity.name_en = r["commoditynameen"]
            commodity.name_ar = r["commoditynamear"]
            session.add(commodity)

    session.commit()

    cur.close()
    conn.close()

def fetch_and_add_commodity_prices():
    conn = _get_connection()
    cur = conn.cursor()

    session = DbSession()

    # get all commodities registered with fintech db, along with their last (most recent) archive date
    subquery = select([StockPrice.stock_entity_id, StockPrice.stock_entity_argaam_id, func.max(StockPrice.for_date).label('for_date'), StockPrice.close])\
        .where(StockPrice.stock_entity_type_id == 2)\
        .group_by(StockPrice.stock_entity_id).alias("sp")

    # http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
    commodities_with_last_entry = session.query(Commodity.id, Commodity.argaam_id, subquery.c.for_date, subquery.c.close)\
        .outerjoin(subquery, Commodity.id == subquery.c.stock_entity_id).all()

    # foreach commodity get the stock price archive from Argaam DB
    for index, (commodity_id, argaam_id, last_entry, close) in enumerate(commodities_with_last_entry):
        print("Processing commodity #%s" % (index + 1,), session.query(Commodity.name_en).filter(Commodity.id == commodity_id).first())
        sql = """
              select cspa.ForDate, cspa.[Open], cspa.[Close], cspa.[Min], cspa.[Max]
              from CommodityStockPricesArchive cspa inner join
              (select max(CommodityStockPriceArchiveID) CommodityStockPriceArchiveID from CommodityStockPricesArchive
              where CommodityID = %d group by ForDate, CommodityID) cspa2 on cspa.CommodityStockPriceArchiveID = cspa2.CommodityStockPriceArchiveID
              where cspa.[Close] <> 0
        """
        if last_entry is not None:
            sql += " and fordate > %s "
            params = (argaam_id, last_entry)
        else:
            params = (argaam_id, )

        sql += " order by fordate asc;"

        # print(sql)
        cur.execute(sql, params)

        commodity_prices = cur.fetchall()

        for index in range(0, len(commodity_prices)):
            for_date = datetime.strptime(commodity_prices[index][0], "%Y-%m-%d")
            sp = StockPrice()
            sp.stock_entity_type_id = 2 # commodity
            sp.stock_entity_id = commodity_id
            sp.stock_entity_argaam_id = argaam_id
            sp.for_date = for_date
            sp.year = for_date.year
            sp.month = for_date.month
            sp.open = commodity_prices[index][1]
            sp.close = commodity_prices[index][2]
            sp.min  = commodity_prices[index][3]
            sp.max = commodity_prices[index][4]

            if index == 0 and close is None:
                sp.change = sp.change_percent = 0
            else:
                sp.change = sp.close - close
                sp.change_percent = ((sp.close - close) / close) * 100

            # use for next iteration
            close = sp.close

            session.add(sp)

        session.commit()

    cur.close()
    conn.close()

def fetch_and_add_company_prices():
    conn = _get_connection()
    cur = conn.cursor()

    session = DbSession()

    # get all companies registered with fintech db, along with their last (most recent) archive date
    subquery = select([StockPrice.stock_entity_id, StockPrice.stock_entity_argaam_id,
                       func.max(StockPrice.for_date).label('for_date'), StockPrice.close]) \
        .where(StockPrice.stock_entity_type_id == 1) \
        .group_by(StockPrice.stock_entity_id).alias("sp")

    # http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
    companies_with_last_entry = session.query(Company.id, Company.argaam_id, subquery.c.for_date,
                                                subquery.c.close) \
        .outerjoin(subquery, Company.id == subquery.c.stock_entity_id).all()

    # foreach company get the stock price archive from Argaam DB
    for index, (company_id, argaam_id, last_entry, close) in enumerate(companies_with_last_entry):
        print("Processing company #%s" % (index + 1,), session.query(Company.name_en).filter(Company.id == company_id).first())
        sql = """
                select cspa.ForDate, cspa.[Open], cspa.[Close], cspa.[Min], cspa.[Max], cspa.[Volume], cspa.[Amount]
                from CompanyStockPricesArchive cspa
                where cspa.companyid = %d
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

            session.add(sp)

        session.commit()

    cur.close()
    conn.close()

def fetch_and_add_market_prices():
    conn = _get_connection()
    cur = conn.cursor()

    session = DbSession()

    # get all markets registered with fintech db, along with their last (most recent) archive date
    subquery = select([StockPrice.stock_entity_id, StockPrice.stock_entity_argaam_id,
                       func.max(StockPrice.for_date).label('for_date'), StockPrice.close]) \
        .where(StockPrice.stock_entity_type_id == 3) \
        .group_by(StockPrice.stock_entity_id).alias("sp")

    # http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
    markets_with_last_entry = session.query(Market.id, Market.argaam_id, subquery.c.for_date,
                                                subquery.c.close) \
        .outerjoin(subquery, Market.id == subquery.c.stock_entity_id).all()

    # foreach market get the stock price archive from Argaam DB
    for index, (market_id, argaam_id, last_entry, close) in enumerate(markets_with_last_entry):
        print("Processing market #%s" % (index + 1,), session.query(Market.name_en).filter(Market.id == market_id).first())
        sql = """
                select spa.ForDate, spa.[Open], spa.[Close], spa.[Min], spa.[Max], spa.[Volume], spa.[Amount]
                from MarketStockPricesArchive spa
                where spa.MarketID = %d
                and spa.[close] <> 0
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

            session.add(sp)

        session.commit()

    cur.close()
    conn.close()

def fetch_and_add_sector_prices():
    conn = _get_connection()
    cur = conn.cursor()

    session = DbSession()

    # get all sectors registered with fintech db, along with their last (most recent) archive date
    subquery = select([StockPrice.stock_entity_id, StockPrice.stock_entity_argaam_id, func.max(StockPrice.for_date).label('for_date'), StockPrice.close])\
        .where(StockPrice.stock_entity_type_id == 4)\
        .group_by(StockPrice.stock_entity_id).alias("sp")

    # http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
    sectors_with_last_entry = session.query(Sector.id, Sector.argaam_id, subquery.c.for_date, subquery.c.close)\
        .outerjoin(subquery, Sector.id == subquery.c.stock_entity_id).all()

    # foreach commodity get the stock price archive from Argaam DB
    for index, (sector_id, argaam_id, last_entry, close) in enumerate(sectors_with_last_entry):
        print("Processing sector #%s" % (index + 1,), session.query(Sector.name_en).filter(Sector.id == sector_id).first())
        sql = """
                select spa.ForDate, spa.[Open], spa.[Close], spa.[Min], spa.[Max], spa.[Volume], spa.[Amount]
                from SectorStockPricesArchive spa inner join
                (select max(SectorStockPriceArchiveID) SectorStockPriceArchiveID from SectorStockPricesArchive where SectorID = %d group by ForDate, SectorID) spa2
                on spa.SectorStockPriceArchiveID = spa2.SectorStockPriceArchiveID
                where spa.[Close] <> 0
              """
        if last_entry is not None:
            sql += " and fordate > %s "
            params = (argaam_id, last_entry)
        else:
            params = (argaam_id, )

        sql += " order by fordate asc;"

        # print(sql)
        cur.execute(sql, params)

        sector_prices = cur.fetchall()

        for index in range(0, len(sector_prices)):
            for_date = datetime.strptime(sector_prices[index][0], "%Y-%m-%d")
            sp = StockPrice()
            sp.stock_entity_type_id = 4 # sector
            sp.stock_entity_id = sector_id
            sp.stock_entity_argaam_id = argaam_id
            sp.for_date = for_date
            sp.year = for_date.year
            sp.month = for_date.month
            sp.open = sector_prices[index][1]
            sp.close = sector_prices[index][2]
            sp.min  = sector_prices[index][3]
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

            session.add(sp)

        session.commit()

    cur.close()
    conn.close()

pass

fetch_and_add_markets()
fetch_and_add_sectors()
fetch_and_add_companies()
fetch_and_add_commodities()

fetch_and_add_sector_prices()
fetch_and_add_market_prices()
fetch_and_add_company_prices()
fetch_and_add_commodity_prices()
