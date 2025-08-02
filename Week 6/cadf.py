#!/usr/bin/python
# -*- coding: utf-8 -*-

# cadf.py

import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import yfinance as yf
import pprint
import statsmodels.api as sm
import statsmodels.tsa.stattools as ts

def plot_price_series(df, ts1, ts2):
    months = mdates.MonthLocator()
    fig, ax = plt.subplots()
    ax.plot(df.index, df[ts1], label=ts1)
    ax.plot(df.index, df[ts2], label=ts2)
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(datetime.datetime(2012, 1, 1), datetime.datetime(2013, 1, 1))
    ax.grid(True)
    fig.autofmt_xdate()
    plt.xlabel('Month/Year')
    plt.ylabel('Price ($)')
    plt.title('%s and %s Daily Prices' % (ts1, ts2))
    plt.legend()
    plt.show()

def plot_scatter_series(df, ts1, ts2):
    plt.xlabel('%s Price ($)' % ts1)
    plt.ylabel('%s Price ($)' % ts2)
    plt.title('%s and %s Price Scatterplot' % (ts1, ts2))
    plt.scatter(df[ts1], df[ts2])
    plt.show()

def plot_residuals(df):
    months = mdates.MonthLocator()
    fig, ax = plt.subplots()
    ax.plot(df.index, df["res"], label="Residuals")
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_xlim(datetime.datetime(2012, 1, 1), datetime.datetime(2013, 1, 1))
    ax.grid(True)
    fig.autofmt_xdate()
    plt.xlabel('Month/Year')
    plt.ylabel('Price ($)')
    plt.title('Residual Plot')
    plt.legend()
    plt.show()

if __name__ == "__main__":
    start = datetime.datetime(2012, 1, 1)
    end = datetime.datetime(2013, 1, 1)

    arex = yf.download("AAPL", start=start, end=end, auto_adjust=False)
    wll = yf.download("MSFT", start=start, end=end, auto_adjust=False)

    df = pd.DataFrame(index=arex.index)
    df["AAPL"] = arex["Adj Close"]
    df["MSFT"] = wll["Adj Close"]

    # Plot the two time series
    plot_price_series(df, "AAPL", "MSFT")

    # Scatter plot
    plot_scatter_series(df, "AAPL", "MSFT")

    # OLS regression using statsmodels
    X = sm.add_constant(df["AAPL"])
    model = sm.OLS(df["MSFT"], X).fit()
    beta_hr = model.params["AAPL"]

    # Residuals
    df["res"] = df["MSFT"] - beta_hr * df["AAPL"]
    plot_residuals(df)

    # CADF test
    cadf = ts.adfuller(df["res"])
    pprint.pprint(cadf)

