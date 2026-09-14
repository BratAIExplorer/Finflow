import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from mstock_sync import (
    Holding,
    Trade,
    FIFOLotMatcher,
    export_maybe_csv,
    export_json,
    get_mock_data,
)


class TestFIFOLotMatcher(unittest.TestCase):

    def test_single_buy_exact_match(self):
        """Holding matches a single buy order exactly."""
        holdings = [Holding(symbol="MAHABANK", name="Bank of Maharashtra", quantity=10, average_price=30.0)]
        trades = [
            Trade(symbol="MAHABANK", transaction_type="BUY", quantity=10, price=30.0, timestamp="2024-01-10 11:05:30", order_id="TR1")
        ]
        matcher = FIFOLotMatcher()
        lots = matcher.match(holdings, trades)

        self.assertEqual(len(lots), 1)
        self.assertEqual(lots[0].symbol, "MAHABANK")
        self.assertEqual(lots[0].quantity, 10)
        self.assertEqual(lots[0].purchase_price, 30.0)
        self.assertEqual(lots[0].purchase_date, "2024-01-10 11:05:30")
        self.assertFalse(lots[0].is_estimated)

    def test_multi_tranche_buys(self):
        """Holding consists of multiple separate buys (e.g. Apollo 50 + 51 = 101 shares)."""
        holdings = [Holding(symbol="APOLLO", name="Apollo Micro Systems", quantity=101, average_price=120.5)]
        trades = [
            Trade(symbol="APOLLO", transaction_type="BUY", quantity=50, price=112.50, timestamp="2024-03-15 10:14:22", order_id="ORD1"),
            Trade(symbol="APOLLO", transaction_type="BUY", quantity=51, price=128.34, timestamp="2024-08-20 14:25:10", order_id="ORD2"),
        ]
        matcher = FIFOLotMatcher()
        lots = matcher.match(holdings, trades)

        self.assertEqual(len(lots), 2)
        # Lot 1: 50 shares on March 15
        self.assertEqual(lots[0].quantity, 50)
        self.assertEqual(lots[0].purchase_price, 112.50)
        self.assertEqual(lots[0].purchase_date, "2024-03-15 10:14:22")

        # Lot 2: 51 shares on August 20
        self.assertEqual(lots[1].quantity, 51)
        self.assertEqual(lots[1].purchase_price, 128.34)
        self.assertEqual(lots[1].purchase_date, "2024-08-20 14:25:10")

        # Total quantity matches 101
        self.assertEqual(sum(lot.quantity for lot in lots), 101)

    def test_buy_and_partial_sell_fifo(self):
        """Oldest buy lot should be consumed first when a sell occurs."""
        holdings = [Holding(symbol="IDEA", name="Vodafone Idea", quantity=4, average_price=7.0)]
        trades = [
            # Buy 2 on Jan 1
            Trade(symbol="IDEA", transaction_type="BUY", quantity=2, price=6.50, timestamp="2024-01-01 10:00:00"),
            # Buy 3 on Jan 10
            Trade(symbol="IDEA", transaction_type="BUY", quantity=3, price=7.50, timestamp="2024-01-10 10:00:00"),
            # Sell 1 on Jan 15 (should consume 1 from the Jan 1 lot of 2, leaving 1)
            Trade(symbol="IDEA", transaction_type="SELL", quantity=1, price=8.00, timestamp="2024-01-15 10:00:00"),
        ]
        matcher = FIFOLotMatcher()
        lots = matcher.match(holdings, trades)

        # Remaining should be 1 share from Jan 1 (price 6.50) and 3 shares from Jan 10 (price 7.50) = total 4
        self.assertEqual(len(lots), 2)
        self.assertEqual(lots[0].quantity, 1)
        self.assertEqual(lots[0].purchase_price, 6.50)
        self.assertEqual(lots[0].purchase_date, "2024-01-01 10:00:00")

        self.assertEqual(lots[1].quantity, 3)
        self.assertEqual(lots[1].purchase_price, 7.50)
        self.assertEqual(lots[1].purchase_date, "2024-01-10 10:00:00")

        self.assertEqual(sum(lot.quantity for lot in lots), 4)

    def test_legacy_acquisition_fallback(self):
        """When trades cover only a partial amount, the remainder is marked as estimated."""
        holdings = [Holding(symbol="TCS", name="Tata Consultancy Services", quantity=100, average_price=3500.0)]
        trades = [
            # Only 40 shares found in the query window
            Trade(symbol="TCS", transaction_type="BUY", quantity=40, price=3600.0, timestamp="2024-06-01 11:00:00")
        ]
        matcher = FIFOLotMatcher()
        lots = matcher.match(holdings, trades, default_date="2023-01-01 09:15:00")

        self.assertEqual(len(lots), 2)
        # Lot 1: 40 shares verified
        self.assertEqual(lots[0].quantity, 40)
        self.assertFalse(lots[0].is_estimated)

        # Lot 2: 60 shares estimated
        self.assertEqual(lots[1].quantity, 60)
        self.assertTrue(lots[1].is_estimated)
        self.assertEqual(lots[1].purchase_price, 3500.0)
        self.assertEqual(lots[1].purchase_date, "2023-01-01 09:15:00")

    def test_maybe_csv_export_format(self):
        """CSV export should contain the exact headers and rows expected by Maybe Finance."""
        holdings, trades = get_mock_data()
        lots = FIFOLotMatcher.match(holdings, trades)
        csv_str = export_maybe_csv(lots, account_name="Kiran", currency="INR")

        lines = [line.strip() for line in csv_str.strip().split("\n") if line.strip()]
        self.assertGreater(len(lines), 1)

        # Header check
        headers = lines[0].split(",")
        self.assertIn("Date", headers)
        self.assertIn("Account", headers)
        self.assertIn("Symbol", headers)
        self.assertIn("Quantity", headers)
        self.assertIn("Price", headers)

        # Row check: Apollo should appear with Account "Kiran" and valid dates
        apollo_rows = [line for line in lines if "APOLLO" in line]
        self.assertEqual(len(apollo_rows), 2)
        for row in apollo_rows:
            self.assertIn("Kiran", row)
            self.assertIn("INR", row)
            self.assertIn("Buy", row)


if __name__ == "__main__":
    unittest.main()
