# stockscreener

This repository provides a simple Python script that screens stocks by
market capitalisation and price action. The script fetches historical
prices with [yfinance](https://pypi.org/project/yfinance/) and stores
them locally so repeated runs do not re-download old data.

## Requirements

- Python 3.8+
- `pandas`
- `yfinance`

Install dependencies with:

```bash
pip install pandas yfinance
```

## Usage

1. Create a `tickers.txt` file with a list of tickers to evaluate
   (one per line or comma separated). A sample file is included.
2. Run the screener:

```bash
python stock_screener.py --tickers tickers.txt
```

The script checks for companies with a market cap greater than $10B and
whose price has recently broken an all‑time high and held above 95% of
that high for at least three months. The output is sorted by market cap
and limited to the top 20 matches.

Historical price data is stored in the `data/` directory for future runs.
