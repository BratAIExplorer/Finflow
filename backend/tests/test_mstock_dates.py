"""Unit tests for mStock trade date auto-population in Finflow."""

from datetime import date
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure httpx is mocked if not installed in environment
if "httpx" not in sys.modules:
    sys.modules["httpx"] = MagicMock()

from backend.brokers.mstock import MStockConnector
from backend.brokers.base import RawHolding


class TestMStockTradeDates(unittest.TestCase):

    def test_calculate_first_buy_dates_single(self):
        trades = [
            {
                "tradingsymbol": "BANKBARODA",
                "transaction_type": "BUY",
                "quantity": 100,
                "order_timestamp": "2024-01-15 11:30:00",
            }
        ]
        res = MStockConnector._calculate_first_buy_dates(trades)
        self.assertEqual(res.get("BANKBARODA"), date(2024, 1, 15))

    def test_calculate_first_buy_dates_multiple_buys_apollo(self):
        """Apollo bought on two separate dates — earliest active lot is selected."""
        trades = [
            {
                "tradingsymbol": "APOLLO",
                "transaction_type": "BUY",
                "quantity": 50,
                "order_timestamp": "2024-03-15 10:14:22",
            },
            {
                "tradingsymbol": "APOLLO",
                "transaction_type": "BUY",
                "quantity": 51,
                "order_timestamp": "2024-08-20 14:25:10",
            },
        ]
        res = MStockConnector._calculate_first_buy_dates(trades)
        # Earliest active lot date is 2024-03-15
        self.assertEqual(res.get("APOLLO"), date(2024, 3, 15))

    def test_calculate_first_buy_dates_fifo_depletion(self):
        """FIFO depletion when an earlier lot was completely sold out."""
        trades = [
            # Buy 50 on Jan 1
            {
                "tradingsymbol": "TATAMOTORS",
                "transaction_type": "BUY",
                "quantity": 50,
                "order_timestamp": "2024-01-01 10:00:00",
            },
            # Sell 50 on Jan 20 (completely exhausts the Jan 1 lot)
            {
                "tradingsymbol": "TATAMOTORS",
                "transaction_type": "SELL",
                "quantity": 50,
                "order_timestamp": "2024-01-20 10:00:00",
            },
            # Buy 100 on Feb 10 (this is the only remaining active lot)
            {
                "tradingsymbol": "TATAMOTORS",
                "transaction_type": "BUY",
                "quantity": 100,
                "order_timestamp": "2024-02-10 10:00:00",
            },
        ]
        res = MStockConnector._calculate_first_buy_dates(trades)
        # Jan 1 lot was fully sold; active lot starts on Feb 10
        self.assertEqual(res.get("TATAMOTORS"), date(2024, 2, 10))

    def test_fetch_holdings_populates_dates(self):
        """Verifies that fetch_holdings assigns the auto-calculated trade date."""
        connector = MStockConnector(
            {"api_key": "dummy_key", "username": "u", "password": "p", "totp_secret": "s"},
            session_state={"access_token": "dummy_tok", "access_token_date": date.today().isoformat()},
        )

        mock_holdings_data = {
            "data": [
                {
                    "tradingsymbol": "APOLLO",
                    "exchange": "NSE",
                    "quantity": 101,
                    "averageprice": 120.5,
                    "isin": "INE713T01028",
                }
            ]
        }
        mock_trades_data = {
            "data": [
                {
                    "tradingsymbol": "APOLLO",
                    "transaction_type": "BUY",
                    "quantity": 101,
                    "order_timestamp": "2024-03-15 10:14:22",
                }
            ]
        }

        # Mock httpx responses
        def mock_get(url, **kwargs):
            resp = MagicMock()
            resp.status_code = 200
            if "trades" in url:
                resp.json.return_value = mock_trades_data
            else:
                resp.json.return_value = mock_holdings_data
            resp.raise_for_status = MagicMock()
            return resp

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.get.side_effect = mock_get
            mock_client_cls.return_value.__enter__.return_value = mock_client

            holdings = connector.fetch_holdings()

            self.assertEqual(len(holdings), 1)
            self.assertEqual(holdings[0].symbol, "APOLLO")
            self.assertEqual(holdings[0].quantity, 101.0)
            self.assertEqual(holdings[0].first_buy_date, date(2024, 3, 15))


if __name__ == "__main__":
    unittest.main()
