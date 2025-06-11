import os
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf

DATA_DIR = "data"


def load_or_download(ticker: str, period_years: int = 10) -> pd.DataFrame:
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"{ticker}.csv")
    start_date = datetime.today() - timedelta(days=period_years * 365)
    if os.path.exists(path):
        df = pd.read_csv(path, index_col=0, parse_dates=True)
        last_date = df.index[-1]
        if last_date.date() < datetime.today().date():
            new_df = yf.download(ticker, start=last_date + timedelta(days=1), progress=False)
            df = pd.concat([df, new_df])
            df = df[~df.index.duplicated(keep='last')]
            df.to_csv(path)
    else:
        df = yf.download(ticker, start=start_date, progress=False)
        df.to_csv(path)
    return df


def check_all_time_high_holding(df: pd.DataFrame, months: int = 3, threshold: float = 0.95) -> bool:
    if df.empty:
        return False
    latest = df.index[-1]
    window_start = latest - timedelta(days=30 * months)
    recent = df[df.index >= window_start]
    if recent.empty:
        return False
    all_time_high = df['Close'].max()
    all_time_high_date = df['Close'].idxmax()
    if all_time_high_date < window_start:
        return False
    return recent['Close'].min() >= threshold * all_time_high


def screen(tickers):
    results = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            market_cap = info.get('marketCap', 0) or 0
            if market_cap < 10_000_000_000:
                continue
            df = load_or_download(ticker)
            if check_all_time_high_holding(df):
                results.append((ticker, market_cap))
        except Exception as exc:
            print(f"Error processing {ticker}: {exc}")
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:20]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Stock screener")
    parser.add_argument('--tickers', default='tickers.txt', help='Path to tickers list file (comma or newline separated)')
    args = parser.parse_args()

    if os.path.exists(args.tickers):
        with open(args.tickers) as f:
            tickers = [t.strip() for t in f.read().replace(',', '\n').split() if t.strip()]
    else:
        print(f"Tickers file {args.tickers} not found")
        return

    results = screen(tickers)
    for ticker, cap in results:
        print(f"{ticker}: market cap {cap/1e9:.2f}B")


if __name__ == "__main__":
    main()
