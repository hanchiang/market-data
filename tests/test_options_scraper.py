import datetime
import unittest
from unittest.mock import AsyncMock, patch

from zoneinfo import ZoneInfo

from src.job.options.scrape_helper_class import Result
from src.job.options.scraper import Scraper, get_default_trade_time

NY_TZ = ZoneInfo("America/New_York")


class OptionsScraperTest(unittest.TestCase):
    def test_get_default_trade_time_uses_previous_trading_day_before_open(self) -> None:
        trade_time = get_default_trade_time(
            datetime.datetime(2025, 4, 8, 9, 29, tzinfo=NY_TZ)
        )

        self.assertEqual(
            trade_time,
            datetime.datetime(2025, 4, 7, 9, 30, tzinfo=NY_TZ),
        )

    def test_get_default_trade_time_uses_same_day_after_open(self) -> None:
        trade_time = get_default_trade_time(
            datetime.datetime(2025, 4, 8, 9, 30, tzinfo=NY_TZ)
        )

        self.assertEqual(
            trade_time,
            datetime.datetime(2025, 4, 8, 9, 30, tzinfo=NY_TZ),
        )

    def test_get_default_trade_time_skips_weekend(self) -> None:
        trade_time = get_default_trade_time(
            datetime.datetime(2025, 4, 12, 12, 0, tzinfo=NY_TZ)
        )

        self.assertEqual(
            trade_time,
            datetime.datetime(2025, 4, 11, 9, 30, tzinfo=NY_TZ),
        )

    def test_get_default_trade_time_skips_holiday_before_open(self) -> None:
        trade_time = get_default_trade_time(
            datetime.datetime(2025, 1, 21, 9, 29, tzinfo=NY_TZ)
        )

        self.assertEqual(
            trade_time,
            datetime.datetime(2025, 1, 17, 9, 30, tzinfo=NY_TZ),
        )

    def test_get_default_trade_time_accepts_non_ny_reference(self) -> None:
        trade_time = get_default_trade_time(
            datetime.datetime(2025, 1, 21, 14, 29, tzinfo=datetime.timezone.utc)
        )

        self.assertEqual(
            trade_time,
            datetime.datetime(2025, 1, 17, 9, 30, tzinfo=NY_TZ),
        )


class OptionsScraperRunTest(unittest.IsolatedAsyncioTestCase):
    async def test_run_passes_single_default_trade_time_to_all_tickers(self) -> None:
        expected_default_trade_time = datetime.datetime(
            2025,
            4,
            7,
            9,
            30,
            tzinfo=NY_TZ,
        )
        scraper = Scraper(result=Result())
        passed_trade_times: list[tuple[str, datetime.datetime]] = []

        async def fake_init_symbols_to_scrape() -> None:
            scraper.symbols_to_scrape = ["SPY", "AAPL"]

        async def fake_scrape_ticker(
            symbol: str,
            tz: ZoneInfo,
            default_trade_time: datetime.datetime,
        ) -> bool:
            passed_trade_times.append((symbol, default_trade_time))
            return True

        scraper.init_symbols_to_scrape = fake_init_symbols_to_scrape
        scraper.scrape_ticker = fake_scrape_ticker
        scraper.cleanup_options_api = AsyncMock()

        with (
            patch(
                "src.job.options.scraper.get_default_trade_time",
                return_value=expected_default_trade_time,
            ),
            patch(
                "src.job.options.scraper.start_postgres_connection_pool",
                new=AsyncMock(),
            ),
            patch(
                "src.job.options.scraper.stop_postgres_connection_pool",
                new=AsyncMock(),
            ),
        ):
            await scraper.run()

        self.assertEqual(
            passed_trade_times,
            [
                ("SPY", expected_default_trade_time),
                ("AAPL", expected_default_trade_time),
            ],
        )


if __name__ == "__main__":
    unittest.main()
