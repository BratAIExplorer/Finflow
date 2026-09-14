# mStock Trade-Matching Sync Engine

This engine reconciles mStock delivery holdings with executed trade logs to solve the missing acquisition date issue (`held — set date`) in portfolio trackers like **Maybe Finance** and **Finflow**.

---

## The Problem

mStock's `/portfolio/holdings` API returns aggregate delivery positions:
* Quantity (e.g. 101 shares of APOLLO)
* Average price
* Current market price & P&L

It **omits** purchase timestamps. When imported into portfolio trackers (like Maybe Finance), the holding has no acquisition date and prompts the user with `held — set date`.

---

## How This Engine Solves It

1. **Fetches Holdings**: Calls `GET /openapi/typea/portfolio/holdings` to retrieve open positions.
2. **Fetches Historical Trades**: Calls `GET /openapi/typea/trades` across a specified date window to retrieve executed BUY and SELL orders.
3. **Applies FIFO Reconciliation**:
   * Sorts orders chronologically.
   * Buys add open lots. Sells deplete the oldest open lots first (FIFO).
   * Reconstructs the exact lots making up the active holding quantity, preserving broker timestamps (`order_timestamp` / `exchange_timestamp`).
4. **Handles Legacy/Pre-API Holdings**:
   * If a holding predates the API's historical trade window, the engine tags those shares as `[ESTIMATED]` at the holding's average price so the portfolio balance remains 100% accurate.
5. **Exports Ready-to-Use Formats**:
   * **Maybe Finance CSV**: `Date,Account,Symbol,Name,Type,Quantity,Price,Currency,Notes`
   * **Finflow JSON**: Structured format with lot breakdown.

---

## Usage

### 1. Test in Mock Mode (No credentials required)
Simulates a real-world mStock portfolio including 101 shares of Apollo Micro Systems:

```bash
# Print summary to console
python scripts/mstock_sync.py --mock --format summary

# Export Maybe Finance CSV for account "Kiran"
python scripts/mstock_sync.py --mock --format maybe-csv --account "Kiran" --out scripts/kiran_mstock_holdings.csv

# Export Finflow JSON
python scripts/mstock_sync.py --mock --format json
```

### 2. Live API Execution
Pass your mStock API Key and Access Token (or set them as environment variables):

```bash
python scripts/mstock_sync.py \
  --api-key "YOUR_API_KEY" \
  --access-token "YOUR_ACCESS_TOKEN" \
  --from-date "2024-01-01" \
  --to-date "2025-01-01" \
  --account "Kiran" \
  --out mstock_reconciled.csv
```

Or using environment variables:
```bash
set MSTOCK_API_KEY=your_key
set MSTOCK_ACCESS_TOKEN=your_token
python scripts/mstock_sync.py --account "Kiran" --out mstock_reconciled.csv
```

---

## Running Unit Tests

Run the test suite covering FIFO allocation, partial sells, legacy holdings fallback, and CSV formatting:

```bash
python -m unittest scripts/test_mstock_sync.py
```
