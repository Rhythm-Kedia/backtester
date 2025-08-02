#!/usr/bin/python
# -*- coding: utf-8 -*-

# hft_data.py

import os
import datetime
import numpy as np
import pandas as pd

from event import MarketEvent
from data import DataHandler


class HistoricCSVDataHandlerHFT(DataHandler):
    """
    HistoricCSVDataHandlerHFT is designed to read CSV files for
    each requested symbol from disk and provide an interface
    to obtain the "latest" bar in a manner identical to a live
    trading interface.

    This version assumes DTN IQFeed-style high-frequency data.
    """

    def __init__(self, events, csv_dir, symbol_list):
        self.events = events
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list

        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        self.bar_index = 0

        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        """
        Opens CSVs from disk into pandas DataFrames with proper
        datetime index and reindexing to ensure consistent timeline.
        """
        comb_index = None

        for s in self.symbol_list:
            file_path = os.path.join(self.csv_dir, f"{s}.csv")
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"CSV file for symbol '{s}' not found at {file_path}")

            df = pd.read_csv(
                file_path,
                header=0,
                index_col=0,
                parse_dates=True,
                names=['datetime', 'open', 'low', 'high', 'close', 'volume', 'oi']
            ).sort_values(by='datetime')

            self.symbol_data[s] = df

            if comb_index is None:
                comb_index = df.index
            else:
                comb_index = comb_index.union(df.index)

            self.latest_symbol_data[s] = []

        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(
                index=comb_index, method='pad'
            )
            self.symbol_data[s]["returns"] = self.symbol_data[s]["close"].pct_change()
            self.symbol_data[s] = self.symbol_data[s].iterrows()

    def _get_new_bar(self, symbol):
        """Yields the next bar for a given symbol."""
        for b in self.symbol_data[symbol]:
            yield b

    def get_latest_bar(self, symbol):
        try:
            return self.latest_symbol_data[symbol][-1]
        except (KeyError, IndexError):
            raise Exception(f"No bars found for symbol: {symbol}")

    def get_latest_bars(self, symbol, N=1):
        try:
            return self.latest_symbol_data[symbol][-N:]
        except KeyError:
            raise Exception(f"No bars found for symbol: {symbol}")

    def get_latest_bar_datetime(self, symbol):
        return self.get_latest_bar(symbol)[0]

    def get_latest_bar_value(self, symbol, val_type):
        return getattr(self.get_latest_bar(symbol)[1], val_type)

    def get_latest_bars_values(self, symbol, val_type, N=1):
        return np.array([
            getattr(b[1], val_type) for b in self.get_latest_bars(symbol, N)
        ])

    def update_bars(self):
        """
        Appends the latest bar to latest_symbol_data for all symbols
        and emits a MarketEvent.
        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
            except StopIteration:
                self.continue_backtest = False

        self.events.put(MarketEvent())

