#!/usr/bin/python
# -*- coding: utf-8 -*-

# create_lagged_series.py

import datetime
import numpy as np
import pandas as pd
import yfinance as yf


def create_lagged_series(symbol, start_date, end_date, lags=5):
    """
    This creates a pandas DataFrame that stores the 
    percentage returns of the adjusted closing value of 
    a stock obtained from Yahoo Finance, along with a 
    number of lagged returns from the prior trading days 
    (lags defaults to 5 days). Trading volume, as well as 
    the Direction from the previous day, are also included.
    """

    # Download data from Yahoo Finance
    ts = yf.download(
        symbol,
        start=start_date - datetime.timedelta(days=365),
        end=end_date,
        auto_adjust=False
    )

    if 'Adj Close' not in ts.columns:
        raise KeyError(f"'Adj Close' column not found for symbol: {symbol}")

    # Create the new lagged DataFrame
    tslag = pd.DataFrame(index=ts.index)
    tslag["Today"] = ts["Adj Close"]
    tslag["Volume"] = ts["Volume"]

    # Create lagged series
    for i in range(0, lags):
        tslag[f"Lag{i+1}"] = ts["Adj Close"].shift(i+1)

    # Create percentage returns
    tsret = pd.DataFrame(index=tslag.index)
    tsret["Volume"] = tslag["Volume"]
    tsret["Today"] = tslag["Today"].pct_change() * 100.0

    # Replace very small returns with 0.0001
    tsret["Today"] = tsret["Today"].apply(lambda x: 0.0001 if abs(x) < 0.0001 else x)

    # Create lagged percentage returns
    for i in range(0, lags):
        tsret[f"Lag{i+1}"] = tslag[f"Lag{i+1}"].pct_change() * 100.0

    # Direction: +1 or -1
    tsret["Direction"] = np.sign(tsret["Today"])
    tsret = tsret[tsret.index >= start_date]

    return tsret

