import numpy as np
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt

from black_scholes_gpu import black_scholes_gpu
from strategies import covered_call_strategy, cash_secured_put_strategy, protective_put_strategy
from data_loader import load_market_data, generate_synthetic_data

# Global State
cash = 100000.0
PnL = 0.0
stocks = []
options = []
trade_log = []
plot = True

def run_backtest(market_data, strategy_function, risk_free_rate=0.05, volatility=0.2):
    global cash, PnL, stocks, options, trade_log
    portfolio_values = []
    timestamps = []

    start_date = market_data.index[0]
    end_date = market_data.index[-1]
    
    monthly_expiries = pd.date_range(start=start_date, end=end_date, freq='BME') + pd.DateOffset(days=14)
    fridays = monthly_expiries[monthly_expiries.dayofweek == 4]

    for timestamp, data_point in market_data.iterrows():
        close_price = data_point['close']

        future_expiries = [d for d in fridays if d > timestamp]
        if not future_expiries:
            continue

        time_to_expiry = np.array([(expiry - timestamp).days / 365.0 for expiry in future_expiries])
        
        strike_prices = np.linspace(close_price * 0.8, close_price * 1.2, 20)
        
        # Prepare inputs for GPU
        n_strikes = len(strike_prices)
        n_expiries = len(future_expiries)
        n_options = n_strikes * n_expiries

        s_flat = np.full(n_options, close_price, dtype=np.float64)
        k_flat = np.tile(strike_prices, n_expiries)
        t_flat = np.repeat(time_to_expiry, n_strikes)
        r_flat = np.full(n_options, risk_free_rate, dtype=np.float64)
        sigma_flat = np.full(n_options, volatility, dtype=np.float64)
        
        call_types = np.zeros(n_options, dtype=np.int32)
        put_types = np.ones(n_options, dtype=np.int32)
        
        call_prices = black_scholes_gpu(s_flat, k_flat, t_flat, r_flat, sigma_flat, call_types)
        put_prices = black_scholes_gpu(s_flat, k_flat, t_flat, r_flat, sigma_flat, put_types)

        # Assemble options chain
        options_chain = []
        idx = 0
        for i, expiry in enumerate(future_expiries):
            for j, strike in enumerate(strike_prices):
                options_chain.append({'expiry': expiry, 'strike': strike, 'option_type': 'call', 'price': call_prices[idx]})
                options_chain.append({'expiry': expiry, 'strike': strike, 'option_type': 'put', 'price': put_prices[idx]})
                idx += 1

        options_to_remove = []
        for i, opt in enumerate(options):
            if timestamp >= opt['expiry']:
                if opt['option_type'] == 'call':
                    if opt['direction'] == 'short' and close_price > opt['strike']: # Assignment
                        PnL -= (close_price - opt['strike']) * 100

                elif opt['option_type'] == 'put':
                     if opt['direction'] == 'short' and close_price < opt['strike']: # Assignment
                        PnL -= (opt['strike'] - close_price) * 100
                options_to_remove.append(i)
        
        for i in sorted(options_to_remove, reverse=True):
            del options[i]

        portfolio = {
            "cash": cash,
            "stock_quantity": sum(s['quantity'] for s in stocks),
            "options": options
        }
        
        actions = strategy_function(timestamp, close_price, options_chain, portfolio)

        for action in actions:
            if action['asset_type'] == 'stock':
                if action['action'] == 'buy':
                    cost = close_price * action['quantity']
                    if cash >= cost:
                        cash -= cost
                        stocks.append({"buy_price": close_price, "quantity": action['quantity']})
                        trade_log.append(f"{timestamp}: BOUGHT {action['quantity']} shares @ {close_price:.2f}")
            
            elif action['asset_type'] == 'option':
                opt_price = next(opt['price'] for opt in options_chain if opt['strike'] == action['strike'] and opt['expiry'] == action['expiry'] and opt['option_type'] == action['option_type'])
                
                if action['action'] == 'sell':
                    cash += opt_price * 100 * action['quantity']
                    options.append({**action, "entry_price": opt_price, "direction": "short"})
                    trade_log.append(f"{timestamp}: SOLD {action['quantity']} {action['option_type'].upper()} {action['strike']:.2f} @ {opt_price:.2f}")
                elif action['action'] == 'buy':
                    cost = opt_price * 100 * action['quantity']
                    if cash >= cost:
                        cash -= cost
                        options.append({**action, "entry_price": opt_price, "direction": "long"})
                        trade_log.append(f"{timestamp}: BOUGHT {action['quantity']} {action['option_type'].upper()} {action['strike']:.2f} @ {opt_price:.2f}")

        stock_value = sum(s['quantity'] * close_price for s in stocks)
        
        option_value = 0
        if options:
            opt_s = np.full(len(options), close_price)
            opt_k = np.array([o['strike'] for o in options])
            opt_t = np.array([(o['expiry'] - timestamp).days / 365.0 for o in options])
            opt_r = np.full(len(options), risk_free_rate)
            opt_sigma = np.full(len(options), volatility)
            opt_types = np.array([0 if o['option_type'] == 'call' else 1 for o in options])
            
            current_opt_prices = black_scholes_gpu(opt_s, opt_k, opt_t, opt_r, opt_sigma, opt_types)
            
            for i, opt in enumerate(options):
                if opt['direction'] == 'long':
                    option_value += current_opt_prices[i] * 100 * opt['quantity']
                else:
                    option_value -= current_opt_prices[i] * 100 * opt['quantity']

        portfolio_value = cash + stock_value + option_value
        portfolio_values.append(portfolio_value)
        timestamps.append(timestamp)

    result = {
        "final_cash": cash,
        "final_PnL": PnL,
        "stocks": stocks,
        "options": options,
        "trade_log": trade_log,
        "timestamps": timestamps,
        "portfolio_values": portfolio_values
    }

    if plot:
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, portfolio_values, label="Portfolio Value")
        plt.xlabel("Time")
        plt.ylabel("Portfolio Value")
        plt.title("Backtest Portfolio Value Over Time")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'backtest_{strategy_function.__name__}.png')
        plt.show()

    return result

if __name__ == '__main__':
    import time, os
    if 'synthetic_market_data.csv' not in os.listdir('.'):
        generate_synthetic_data(365*5)
    market_data = load_market_data()

    print("Running Covered Call Strategy...")
    start_time = time.time()
    cc_results = run_backtest(market_data.copy(), covered_call_strategy)
    end_time = time.time()
    print(f"Covered Call Strategy took {end_time - start_time:.2f} seconds.")
    
    print("\nRunning Cash Secured Put Strategy...")
    start_time = time.time()
    csp_results = run_backtest(market_data.copy(), cash_secured_put_strategy)
    end_time = time.time()
    print(f"Cash Secured Put Strategy took {end_time - start_time:.2f} seconds.")

    print("\nRunning Protective Put Strategy...")
    start_time = time.time()
    pp_results = run_backtest(market_data.copy(), protective_put_strategy)
    end_time = time.time()
    print(f"Protective Put Strategy took {end_time - start_time:.2f} seconds.")

    # Plotting comparison
    plt.figure(figsize=(14, 8))
    plt.plot(cc_results['timestamps'], cc_results['portfolio_values'], label='Covered Call')
    plt.plot(csp_results['timestamps'], csp_results['portfolio_values'], label='Cash Secured Put')
    plt.plot(pp_results['timestamps'], pp_results['portfolio_values'], label='Protective Put')
    plt.title('Strategy Performance Comparison')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value ($)')
    plt.legend()
    plt.grid(True)
    plt.show()
