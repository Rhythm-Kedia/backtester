from datetime import datetime

def covered_call_strategy(timestamp: datetime, close_price: float, options_chain: list, portfolio: dict):
    """
    Implements the Covered Call strategy.
    - Buys 100 shares of stock if none are held.
    - Sells one out-of-the-money (OTM) call option against the shares.
    """
    actions = []
    
    # Check if we own stock
    stock_quantity = portfolio.get("stock_quantity", 0)

    # If no stock, buy 100 shares
    if stock_quantity == 0:
        actions.append({"asset_type": "stock", "action": "buy", "quantity": 100})
        return actions

    # If we have stock but no short call, sell one
    has_short_call = any(opt['direction'] == 'short' and opt['option_type'] == 'call' for opt in portfolio['options'])
    
    if stock_quantity >= 100 and not has_short_call:
        # Find a suitable call option to sell (e.g., 5-10% OTM, nearest expiry)
        otm_calls = [
            opt for opt in options_chain 
            if opt['option_type'] == 'call' 
            and opt['strike'] > close_price * 1.05 
            and opt['strike'] < close_price * 1.15
        ]
        
        if otm_calls:
            # Sort by expiry and then strike to get the nearest, lowest-strike OTM call
            best_call = sorted(otm_calls, key=lambda x: (x['expiry'], x['strike']))[0]
            actions.append({
                "asset_type": "option", 
                "action": "sell", 
                "option_type": "call",
                "strike": best_call['strike'],
                "expiry": best_call['expiry'],
                "quantity": 1  # 1 contract for 100 shares
            })
            
    return actions

def cash_secured_put_strategy(timestamp: datetime, close_price: float, options_chain: list, portfolio: dict):
    """
    Implements the Cash-Secured Put strategy.
    - Sells an out-of-the-money (OTM) put option if there is enough cash to cover the potential assignment.
    """
    actions = []
    
    # Check if we already have a short put
    has_short_put = any(opt['direction'] == 'short' and opt['option_type'] == 'put' for opt in portfolio['options'])

    if not has_short_put:
        # Find a suitable put option to sell (e.g., 5-10% OTM, nearest expiry)
        otm_puts = [
            opt for opt in options_chain 
            if opt['option_type'] == 'put' 
            and opt['strike'] < close_price * 0.95
            and opt['strike'] > close_price * 0.85
        ]
        
        if otm_puts:
            # Sort by expiry and then strike to get the nearest, highest-strike OTM put
            best_put = sorted(otm_puts, key=lambda x: (x['expiry'], -x['strike']))[0]
            
            # Check if we have enough cash to secure the put
            required_cash = best_put['strike'] * 100
            if portfolio['cash'] >= required_cash:
                actions.append({
                    "asset_type": "option", 
                    "action": "sell", 
                    "option_type": "put",
                    "strike": best_put['strike'],
                    "expiry": best_put['expiry'],
                    "quantity": 1
                })

    return actions

def protective_put_strategy(timestamp: datetime, close_price: float, options_chain: list, portfolio: dict):
    """
    Implements the Protective Put (or Married Put) strategy.
    - Buys 100 shares of stock.
    - Buys an at-the-money (ATM) or slightly OTM put option to hedge.
    """
    actions = []
    
    stock_quantity = portfolio.get("stock_quantity", 0)

    # If no stock, buy 100 shares
    if stock_quantity == 0:
        actions.append({"asset_type": "stock", "action": "buy", "quantity": 100})
        return actions

    # If we have stock but no protective put, buy one
    has_long_put = any(opt['direction'] == 'long' and opt['option_type'] == 'put' for opt in portfolio['options'])

    if stock_quantity >= 100 and not has_long_put:
        # Find a suitable put option to buy (e.g., ATM or slightly OTM)
        protective_puts = [
            opt for opt in options_chain 
            if opt['option_type'] == 'put' 
            and opt['strike'] < close_price * 1.02 # ATM
            and opt['strike'] > close_price * 0.90 # Slightly OTM
        ]
        
        if protective_puts:
            # Sort by expiry and then strike to get the nearest expiry, highest strike put
            best_put = sorted(protective_puts, key=lambda x: (x['expiry'], -x['strike']))[0]
            actions.append({
                "asset_type": "option", 
                "action": "buy", 
                "option_type": "put",
                "strike": best_put['strike'],
                "expiry": best_put['expiry'],
                "quantity": 1
            })
            
    return actions
