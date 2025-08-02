#!/usr/bin/python
# -*- coding: utf-8 -*-

# plot_performance.py

import os.path
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

if __name__ == "__main__":
    # Read the equity curve CSV
    data = pd.read_csv(
        "equity.csv", 
        header=0, 
        parse_dates=True, 
        index_col=0
    ).sort_index()

    # Plot three charts: Equity curve, returns, drawdowns
    fig = plt.figure(figsize=(10, 8))
    fig.patch.set_facecolor('white')  # Set background to white

    # Plot the equity curve
    ax1 = fig.add_subplot(311, ylabel='Portfolio Value (%)')
    data['equity_curve'].plot(ax=ax1, color="blue", lw=2.)
    ax1.set_title("Equity Curve")
    ax1.grid(True)

    # Plot the returns
    ax2 = fig.add_subplot(312, ylabel='Period Returns (%)')
    data['returns'].plot(ax=ax2, color="black", lw=2.)
    ax2.set_title("Returns")
    ax2.grid(True)

    # Plot the drawdowns
    ax3 = fig.add_subplot(313, ylabel='Drawdowns (%)')
    data['drawdown'].plot(ax=ax3, color="red", lw=2.)
    ax3.set_title("Drawdowns")
    ax3.grid(True)

    plt.tight_layout()
    plt.show()

