#!/usr/bin/python
# -*- coding: utf-8 -*-

# performance.py

from __future__ import print_function

import numpy as np
import pandas as pd

def create_sharpe_ratio(returns, periods=252):
    """
    Create the Sharpe ratio for the strategy, based on a 
    benchmark of zero (i.e. no risk-free rate information).

    Parameters:
    returns - A pandas Series representing period percentage returns.
    periods - Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    """
    if np.std(returns) == 0: return 0.0
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)

def create_drawdowns(pnl):
    """
    Calculate the largest peak-to-trough drawdown of the PnL curve
    as well as the duration of the drawdown. Requires that the 
    pnl_returns is a pandas Series.

    Parameters:
    pnl - A pandas Series representing period percentage returns.

    Returns:
    drawdown, duration - Highest peak-to-trough drawdown and duration.
    """
    # Convert to np array if a pd Series because it is faster
    if isinstance(pnl, pd.Series):
        idx = pnl.index
        pnl_array = pnl.values
    else:
        pnl_array = pnl
        idx = pd.RangeIndex(len(pnl_array))
    
    hwm_array = np.zeros(len(pnl_array))
    drawdown_array = np.zeros(len(pnl_array))
    duration_array = np.zeros(len(pnl_array), dtype=int)
    
    for t in range(1, len(pnl_array)):
        hwm_array[t] = max(hwm_array[t-1], pnl_array[t])
        drawdown_array[t] = hwm_array[t] - pnl_array[t]
        duration_array[t] = 0 if drawdown_array[t] == 0 else duration_array[t-1] + 1
    
    drawdown = pd.Series(drawdown_array, index=idx)
    
    return drawdown, drawdown.max(), max(duration_array)