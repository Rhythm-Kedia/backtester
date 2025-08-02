#!/usr/bin/python
# -*- coding: utf-8 -*-

# sharpe.py

from __future__ import print_function

import datetime
import numpy as np
import pandas as pd
import yfinance as yf

def annualised_sharpe(returns, N=252):
    """
    Calculate the annualised Sharpe ratio of a returns stream
    based on a number of trading periods, N. N defaults to 252,
    which then assumes a stream of daily returns.

    The function assumes that the returns are the excess of
    those compared to a benchmark.
    """
    return np.sqrt(N) * returns.mean() / returns.std()

def equity_sharpe(ticker):
    """
    Calculates the annualised Sharpe ratio based on the daily
    returns of an equity ticker symbol.

    The dates have been hardcoded here for brevity.
    """
    start = datetime.datetime(2000,1,1)
    end = datetime.datetime(2013,1,1)

    df = yf.download(ticker, start=start, end=end, auto_adjust=False)
    df['daily_ret'] = df['Close'].pct_change()
    df['excess_daily_ret'] = df['daily_ret'] - 0.05/252

    return annualised_sharpe(df['excess_daily_ret'])

def market_neutral_sharpe(ticker, benchmark):
    """
    Calculates the annualised Sharpe ratio of a market
    neutral long/short strategy involving a long of 'ticker'
    with a corresponding short of the 'benchmark'.
    """
    start = datetime.datetime(2000, 1, 1)
    end = datetime.datetime(2013, 1, 1)

    tick = yf.download(ticker, start=start, end=end, auto_adjust=False)
    bench = yf.download(benchmark, start=start, end=end, auto_adjust=False)

    tick['daily_ret'] = tick['Close'].pct_change()
    bench['daily_ret'] = bench['Close'].pct_change()

    strat = pd.DataFrame(index=tick.index)
    strat['net_ret'] = (tick['daily_ret'] - bench['daily_ret']) / 2.0

    return annualised_sharpe(strat['net_ret'])

if __name__ == "__main__":
    print("Google Sharpe Ratio: %s" % equity_sharpe('GOOG'))
    print("Google Market Neutral Sharpe Ratio: %s" % market_neutral_sharpe('GOOG', 'SPY'))

