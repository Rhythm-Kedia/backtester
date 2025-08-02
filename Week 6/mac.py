#!/usr/bin/python
# -*- coding: utf-8 -*-

# mac.py

from __future__ import print_function

import datetime
from unittest.mock import call

import numpy as np
import pandas as pd

from strategy import Strategy
from event import SignalEvent
from backtest import Backtest
from data import HistoricCSVDataHandler
from execution import SimulatedExecutionHandler
from portfolio import Portfolio
from numba import njit

@njit(cache=True)
def calculate_sma_batch(prices, short_window, long_window):
    """Calculate both SMAs in one pass"""
    if len(prices) < long_window:
        return 0.0, 0.0
    # Numba is very efficient with explicit loops
    short_sum = 0.0
    for i in range(1, short_window + 1):
        short_sum += prices[-i]
    
    long_sum = short_sum # Start with short_sum to avoid re-calculating
    for i in range(short_window + 1, long_window + 1):
        long_sum += prices[-i]
        
    return short_sum / short_window, long_sum / long_window


class MovingAverageCrossStrategy(Strategy):
    """
    Carries out a basic Moving Average Crossover strategy with a
    short/long simple weighted moving average. Default short/long
    windows are 100/400 periods respectively.
    """

    def __init__(
        self, bars, events, short_window=100, long_window=400
    ):
        """
        Initialises the Moving Average Cross Strategy.

        Parameters:
        bars - The DataHandler object that provides bar information
        events - The Event Queue object.
        short_window - The short moving average lookback.
        long_window - The long moving average lookback.
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.short_window = short_window
        self.long_window = long_window

        # Set to True if a symbol is in the market
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        """
        Adds keys to the bought dictionary for all symbols
        and sets them to 'OUT'.
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = 'OUT'
        return bought

    def calculate_signals(self, event):
        """
        Generates a new set of signals based on the MAC
        SMA with the short window crossing the long window
        meaning a long entry and vice versa for a short entry.    

        Parameters
        event - A MarketEvent object. 
        """
        if event.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars_values(
                    s, "adj_close", N=self.long_window
                )
                bar_date = self.bars.get_latest_bar_datetime(s)
                if bars is not None and len(bars) >= self.long_window:
                    short_sma, long_sma = calculate_sma_batch(
                        bars, self.short_window, self.long_window
                    )

                    symbol = s
                    dt = datetime.datetime.now(datetime.UTC)
                    sig_dir = ""

                    if short_sma > long_sma and self.bought[s] == "OUT":
                        print("LONG: %s" % bar_date)
                        sig_dir = 'LONG'
                        signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'LONG'
                    elif short_sma < long_sma and self.bought[s] == "LONG":
                        print("EXIT: %s" % bar_date)
                        sig_dir = 'EXIT'
                        signal = SignalEvent(1, symbol, dt, sig_dir, 1.0)
                        self.events.put(signal)
                        self.bought[s] = 'OUT'


import time
if __name__ == "__main__":
    csv_dir = '.'
    # BIG_AAPL is a generated data using gen_data.py
    # to check the speed up obtained by Numba
    symbol_list = ['BIG_AAPL']
    initial_capital = 100000.0
    heartbeat = 0.0
    start_date = datetime.datetime(1990, 1, 1, 0, 0, 0)
    start_time = time.time()
    backtest = Backtest(
        csv_dir, symbol_list, initial_capital, heartbeat, 
        start_date, HistoricCSVDataHandler, SimulatedExecutionHandler, 
        Portfolio, MovingAverageCrossStrategy
    )
    backtest.simulate_trading()
    end_time  = time.time()
    print("Total time taken: %s seconds" % (end_time - start_time))
