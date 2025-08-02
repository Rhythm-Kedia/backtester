import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_synthetic_data(days=365, initial_price=100.0, mu=0.0002, sigma=0.015):
    """
    Generates synthetic daily stock price data for now using this only
    """
    
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    prices = [initial_price]
    for _ in range(1, days):
        drift = mu
        shock = np.random.normal(0, sigma)
        price = prices[-1] * np.exp(drift + shock)
        prices.append(price)
        
    market_data = pd.DataFrame({
        'timestamp': pd.to_datetime(dates),
        'close': prices
    })
    market_data.set_index('timestamp', inplace=True)
    market_data.to_csv('synthetic_market_data.csv')

def load_market_data(file_path='synthetic_market_data.csv'):
    market_data = pd.read_csv(file_path, parse_dates=['timestamp'], index_col='timestamp')
    return market_data
