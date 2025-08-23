import pandas as pd

def backtest(df):
    """
    Simple backtest for EMA crossover signals.
    Assumes df has a 'Signal' column: 1=buy, -1=sell, 0=flat.
    Calculates:
    - Position (current holding)
    - Strategy returns per bar
    - Cumulative returns
    """
    df = df.copy()
    
    # Position: carry forward last signal 
    df['Position'] = df['Signal'].replace(to_replace=0, method='ffill').shift(1).fillna(0)
    
    # Calculate returns
    df['Returns'] = df['Close'].pct_change().fillna(0)
    df['Strategy_Returns'] = df['Position'] * df['Returns']
    
    # Cumulative returns
    df['Cumulative_Returns'] = (1 + df['Strategy_Returns']).cumprod()
    
    return df
