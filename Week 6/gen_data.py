import numpy as np
import pandas as pd
import argparse
from datetime import datetime, timedelta

def generate_synthetic_csv(filename, num_rows, start_date="1990-01-01"):
    # Generate date range
    start = datetime.strptime(start_date, "%Y-%m-%d")
    dates = [start + timedelta(days=i) for i in range(num_rows)]
    
    # Generate synthetic OHLCV data
    open_prices = np.cumsum(np.random.randn(num_rows)) + 100
    high_prices = open_prices + np.abs(np.random.randn(num_rows))
    low_prices = open_prices - np.abs(np.random.randn(num_rows))
    close_prices = open_prices + np.random.randn(num_rows) * 0.5
    volume = np.random.randint(1e5, 1e6, size=num_rows)
    adj_close = close_prices + np.random.randn(num_rows) * 0.1

    df = pd.DataFrame({
        "datetime": dates,
        "open": open_prices,
        "high": high_prices,
        "low": low_prices,
        "close": close_prices,
        "volume": volume,
        "adj_close": adj_close
    })
    df.set_index("datetime", inplace=True)
    df.to_csv(filename)
    print(f"Generated {num_rows} rows in {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic OHLCV CSV data.")
    parser.add_argument("--filename", type=str, default="BIG_AAPL.csv", help="Output CSV filename")
    parser.add_argument("--rows", type=int, default=100000, help="Number of rows to generate")
    parser.add_argument("--start-date", type=str, default="1990-01-01", help="Start date (YYYY-MM-DD)")
    args = parser.parse_args()
    generate_synthetic_csv(args.filename, args.rows, args.start_date)