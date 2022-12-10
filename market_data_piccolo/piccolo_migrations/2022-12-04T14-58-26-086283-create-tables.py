from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table


ID = "2022-12-04T14:58:26:086283"
VERSION = "0.99.0"
DESCRIPTION = "Create tables"

stock_price_precision = (12, 5)
option_price_precision = (6, 3)
option_aggregate_stat_precision = (10, 8)
option_greek_precision = (9, 8)

# dummy table to execute raw SQL
class RawTable(Table):
    pass

async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="market_data_piccolo", description=DESCRIPTION
    )
    async def create_stock_ticker():
        script = '''
        CREATE TABLE IF NOT EXISTS stock_ticker
        (
            symbol character varying(10) NOT NULL DEFAULT '',
            name character varying(255) NOT NULL DEFAULT '',
            CONSTRAINT stock_ticker_pkey PRIMARY KEY (symbol)
        );
        '''
        await RawTable.raw(script)

    async def create_stock_ticker_price():
        script = '''
        CREATE TABLE IF NOT EXISTS stock_ticker_price
        (
            symbol character varying(255) NOT NULL DEFAULT '',
            date date NOT NULL DEFAULT CURRENT_DATE,
            open_price numeric(12,5) NOT NULL DEFAULT 0,
            high_price numeric(12,5) NOT NULL DEFAULT 0,
            low_price numeric(12,5) NOT NULL DEFAULT 0,
            close_price numeric(12,5) NOT NULL DEFAULT 0,
            volume integer NOT NULL DEFAULT 0,
            open_interest integer NOT NULL DEFAULT 0,
            CONSTRAINT symbol_date_uq UNIQUE (symbol, date),
            CONSTRAINT symbol_fk FOREIGN KEY (symbol) REFERENCES stock_ticker(symbol) ON UPDATE CASCADE ON DELETE NO ACTION
        );
        '''
        await RawTable.raw(script)
        await RawTable.raw("SELECT create_hypertable('stock_ticker_price', 'date')")

    async def create_option_price():
        script = '''
        CREATE TABLE IF NOT EXISTS option_price
        (
            symbol character varying(100) NOT NULL,
            base_symbol character varying(255) NOT NULL,
            trade_time timestamp with time zone NOT NULL,
            option_type character varying(4) NOT NULL,
            strike_price numeric(12,5) NOT NULL,
            open_price numeric(6,3) NOT NULL,
            high_price numeric(6,3) NOT NULL,
            low_price numeric(6,3) NOT NULL,
            last_price numeric(6,3) NOT NULL,
            moneyness numeric(10,8) NOT NULL,
            bid_price numeric(6,3) NOT NULL,
            ask_price numeric(6,3) NOT NULL,
            mid_price numeric(6,3) NOT NULL,
            volatility numeric(10,8) NOT NULL,
            expiration_date date NOT NULL,
            expiration_type character varying(6) NOT NULL,
            average_volatility numeric(10,8) NOT NULL,
            delta numeric(9,8) NOT NULL,
            theta numeric(9,8) NOT NULL,
            gamma numeric(9,8) NOT NULL,
            vega numeric(9,8) NOT NULL,
            rho numeric(9,8) NOT NULL,
            CONSTRAINT symbol_trade_time_expiration_date_strike_price_option_type_uq UNIQUE (symbol, trade_time, expiration_date, strike_price, option_type),
            CONSTRAINT base_symbol_fk FOREIGN KEY (base_symbol) REFERENCES stock_ticker(symbol) ON UPDATE CASCADE ON DELETE NO ACTION
        );
        '''
        await RawTable.raw(script)
        await RawTable.raw("SELECT create_hypertable('option_price', 'trade_time')")

    async def run():
        await create_stock_ticker()
        await create_stock_ticker_price()
        await create_option_price()

    async def run_backwards():
        await RawTable.raw('DROP TABLE option_price')
        await RawTable.raw('DROP TABLE stock_ticker_price')
        await RawTable.raw('DROP TABLE stock_ticker')

    manager.add_raw(run)
    manager.add_raw_backwards(run_backwards)

    return manager
