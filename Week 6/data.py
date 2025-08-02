#!/usr/bin/python
# -*- coding: utf-8 -*-

# data.py

from __future__ import print_function

from abc import ABCMeta, abstractmethod
import datetime
import os, os.path

import numpy as np
import pandas as pd
from numba import njit

from event import MarketEvent


class DataHandler(object):
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) DataHandler object is to output a generated
    set of bars (OHLCVI) for each symbol requested. 

    This will replicate how a live strategy would function as current
    market data would be sent "down the pipe". Thus a historic and live
    system will be treated identically by the rest of the backtesting suite.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bar(self, symbol):
        """
        Returns the last bar updated.
        """
        raise NotImplementedError("Should implement get_latest_bar()")

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars updated.
        """
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_datetime()")

    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        from the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_value()")

    @abstractmethod
    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the 
        latest_symbol list, or N-k if less available.
        """
        raise NotImplementedError("Should implement get_latest_bars_values()")

    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bars to the bars_queue for each symbol
        in a tuple OHLCVI format: (datetime, open, high, low, 
        close, volume, open interest).
        """
        raise NotImplementedError("Should implement update_bars()")


class HistoricCSVDataHandler(DataHandler):
    """
    HistoricCSVDataHandler is designed to read CSV files for
    each requested symbol from disk and provide an interface
    to obtain the "latest" bar in a manner identical to a live
    trading interface. 
    """

    def __init__(self, events, csv_dir, symbol_list):
        """
        Initialises the historic data handler by requesting
        the location of the CSV files and a list of symbols.

        It will be assumed that all files are of the form
        'symbol.csv', where symbol is a string in the list.

        Parameters:
        events - The Event Queue.
        csv_dir - Absolute directory path to the CSV files.
        symbol_list - A list of symbol strings.
        """
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list

        # Optimization: Use only array-based storage
        self._data_arrays = {}
        self._current_index = {s: -1 for s in symbol_list}  # Current bar index for each symbol
        self.continue_backtest = True
        
        # Cache for windowed values
        self._value_cache = {}

        # Load all data as optimized arrays
        self._load_data_arrays()

    def _load_data_arrays(self):
        """
        Load all CSV data directly into NumPy arrays for maximum performance.
        """
        # Find common date index across all symbols
        comb_index = None
        symbol_dfs = {}
        
        for s in self.symbol_list:
            # Load CSV file
            df = pd.read_csv(
                os.path.join(self.csv_dir, '%s.csv' % s),
                header=0, index_col=0, parse_dates=True,
                names=['datetime', 'open', 'high', 'low', 'close', 'volume', 'adj_close']
            ).sort_index()
            
            symbol_dfs[s] = df
            
            # Combine indexes
            if comb_index is None:
                comb_index = df.index
            else:
                comb_index = comb_index.union(df.index)
        
        # Reindex all dataframes and convert to arrays
        for s in self.symbol_list:
            df = symbol_dfs[s].reindex(index=comb_index, method='pad')
            df["returns"] = df["close"].pct_change()
            
            # Store as NumPy arrays for fast access
            self._data_arrays[s] = {
                'datetime': df.index.values,
                'open': df['open'].values,
                'high': df['high'].values,
                'low': df['low'].values,
                'close': df['close'].values,
                'volume': df['volume'].values,
                'adj_close': df['adj_close'].values,
                'returns': df['returns'].values
            }

    def update_bars(self):
        """
        Optimized bar update using direct index manipulation.
        Advances current index for each symbol instead of using generators.
        """
        all_stopped = True
        for s in self.symbol_list:
            max_idx = len(self._data_arrays[s]['close']) - 1
            if self._current_index[s] < max_idx:
                self._current_index[s] += 1
                all_stopped = False
            
        if all_stopped:
            self.continue_backtest = False
        else:
            self.events.put(MarketEvent())

    def get_latest_bar(self, symbol):
        """
        Returns the last bar from the latest_symbol list.
        Optimized to use array access.
        """
        idx = self._current_index[symbol]
        if idx < 0:
            raise Exception(f"No bars available for {symbol}")
        
        # Return in same format as before for compatibility
        dt = self._data_arrays[symbol]['datetime'][idx]
        
        # Create a pandas Series-like object for compatibility
        class BarData:
            def __init__(self, data_dict):
                for k, v in data_dict.items():
                    setattr(self, k, v)
        
        bar_data = BarData({
            'open': self._data_arrays[symbol]['open'][idx],
            'high': self._data_arrays[symbol]['high'][idx],
            'low': self._data_arrays[symbol]['low'][idx],
            'close': self._data_arrays[symbol]['close'][idx],
            'volume': self._data_arrays[symbol]['volume'][idx],
            'adj_close': self._data_arrays[symbol]['adj_close'][idx],
            'returns': self._data_arrays[symbol]['returns'][idx]
        })
        
        return (dt, bar_data)

    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or N-k if less available. Optimized array access.
        """
        idx = self._current_index[symbol]
        if idx < 0:
            return []
            
        start_idx = max(0, idx - N + 1)
        bars = []
        
        for i in range(start_idx, idx + 1):
            dt = self._data_arrays[symbol]['datetime'][i]
            
            class BarData:
                def __init__(self, data_dict):
                    for k, v in data_dict.items():
                        setattr(self, k, v)
            
            bar_data = BarData({
                'open': self._data_arrays[symbol]['open'][i],
                'high': self._data_arrays[symbol]['high'][i],
                'low': self._data_arrays[symbol]['low'][i],
                'close': self._data_arrays[symbol]['close'][i],
                'volume': self._data_arrays[symbol]['volume'][i],
                'adj_close': self._data_arrays[symbol]['adj_close'][i],
                'returns': self._data_arrays[symbol]['returns'][i]
            })
            
            bars.append((dt, bar_data))
        
        return bars

    def get_latest_bar_datetime(self, symbol):
        """
        Returns a Python datetime object for the last bar.
        """
        idx = self._current_index[symbol]
        if idx < 0:
            raise Exception(f"No bars available for {symbol}")
        return self._data_arrays[symbol]['datetime'][idx]

    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        values from the pandas Bar series object.
        """
        idx = self._current_index[symbol]
        if idx < 0:
            raise Exception(f"No bars available for {symbol}")
        return self._data_arrays[symbol][val_type][idx]

    @staticmethod
    @njit(cache=True)
    def _get_latest_values_numba(array, current_idx, N):
        """Numba-optimized function to get N latest values from array."""
        start_idx = max(0, current_idx - N + 1)
        return array[start_idx:current_idx + 1]

    def get_latest_bars_values(self, symbol, val_type, N=1):
        """
        Returns the last N bar values from the latest_symbol list, or N-k if less available.
        Uses optimized NumPy arrays with Numba acceleration and caching.
        """
        cache_key = f"{symbol}_{val_type}_{N}_{self._current_index[symbol]}"
        if cache_key in self._value_cache:
            return self._value_cache[cache_key]

        idx = self._current_index[symbol]
        if idx < 0:
            return np.array([])
        
        # Use Numba-accelerated function for fast array slicing
        result = self._get_latest_values_numba(
            self._data_arrays[symbol][val_type], 
            idx, 
            N
        )
        
        # Cache only for common lookback periods
        if N in (50, 100, 200, 400):
            self._value_cache[cache_key] = result
            
        return result
