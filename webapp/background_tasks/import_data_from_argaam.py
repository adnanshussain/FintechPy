import pypyodbc
from webapp.config import ARGAAM_MSSQL_CONN_STR
from sqlalchemy.orm import sessionmaker
from webapp.sqlalchemy_models as sam

DbSession = sessionmaker(bind=sam.sql_engine)

def _get_connection():
    return pypyodbc.connect(ARGAAM_MSSQL_CONN_STR)

def fetch_and_add_markets():
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute("select * from markets where IsActive = 1 and IsTrading = 1 and DisplayInPP = 1")

    # for d in cur.description:
    #     print(d)

    session = DbSession()

    for r in cur.fetchall():
        argaam_market_id = r["marketid"]

        if session.query(sam.Market).filter(sam.Market.argaam_id == argaam_market_id).count() == 0:
            market = sam.Market()
            market.argaam_id = r["marketid"]
            market.name_en = r["marketnameen"]
            market.name_ar = r["marketnamear"]
            market.symbol = r["generalindexsymbol"]
            session.add(market)

    session.commit()

    cur.close()
    conn.close()

def fetch_and_add_sectors():
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute("select * from MarketSectors ms inner join sectors s on ms.SectorID= s.sectorid where ms.MarketID = 3 and s.IsPublished = 1")

    session = DbSession()

    for r in cur.fetchall():
        argaam_sector_id = r["sectorid"]

        if session.query(sam.Sector).filter(sam.Sector.argaam_id == argaam_sector_id).count() == 0:
            sector = sam.Sector()
            sector.argaam_id = r["sectorid"]
            sector.name_en = r["sectornameen"]
            sector.name_ar = r["sectornamear"]
            session.add(sector)

    session.commit()

    cur.close()
    conn.close()

def fetch_and_add_companies():
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute("""select msc.MarketID, msc.CompanyID, msc.CompanyNameEn, msc.CompanyNameAr, msc.ShortNameEn, msc.ShortNameAr,
                c.StockSymbol, c.LogoURL
                from pub.MarketSectorCompanies msc
                inner join dbo.Companies c on c.CompanyID = msc.CompanyID
                where msc.MarketStatusID = 3 and msc.marketid = 3 and msc.RecordStatus = 1 and msc.IsActive = 1 and msc.IsSuspended = 0""")

    session = DbSession()

    for r in cur.fetchall():
        argaam_company_id = r["companyid"]

        if session.query(sam.Company).filter(sam.Company.argaam_id == argaam_company_id).count() == 0:
            company = sam.Company()
            company.argaam_id = r["companyid"]
            company.full_name_en = r["companynameen"]
            company.full_name_ar = r["companynamear"]
            company.short_name_en = r["shortnameen"]
            company.short_name_ar = r["shortnamear"]
            company.market_id = session.query(sam.Market).filter(sam.Market.argaam_id == r["marketid"]).one().id
            company.stock_symbol = r["stocksymbol"]
            company.logo_url = r["logourl"]
            session.add(company)

    session.commit()

    cur.close()
    conn.close()

def fetch_and_add_commodities():
    conn = _get_connection()
    cur = conn.cursor()

    cur.execute("select * from CommodityStockPrices where IsVisible = 1")

    session = DbSession()

    for r in cur.fetchall():
        argaam_commodity_id = r["commodityid"]

        if session.query(sam.Commodity).filter(sam.Commodity.argaam_id == argaam_commodity_id).count() == 0:
            commodity = sam.Commodity()
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

    # pseudo code here

    session = DbSession()

    session.commit()

    cur.close()
    conn.close()


fetch_and_add_markets()
fetch_and_add_sectors()
fetch_and_add_companies()
fetch_and_add_commodities()