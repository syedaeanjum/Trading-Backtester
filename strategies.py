import pandas as pd

# --------------------- EMA Crossover ---------------------

def ema_crossover(df, short_window=9, long_window=21):
    """
    Generate EMA crossover signals.
    Signal = 1 -> Buy
    Signal = -1 -> Sell
    
    """
    df = df.copy()
    df['EMA_short'] = df['Close'].ewm(span=short_window, adjust=False).mean()
    df['EMA_long'] = df['Close'].ewm(span=long_window, adjust=False).mean()
    
    df['Signal'] = 0
    df.loc[df['EMA_short'] > df['EMA_long'], 'Signal'] = 1
    df.loc[df['EMA_short'] < df['EMA_long'], 'Signal'] = -1
    
    return df

# --------------------- Martingale Strategy ---------------------

def martingale_strategy(df, base_lot=0.02, multiplier=2, step=10, take_profit=5):

    df = df.copy()

    # Ensure numeric
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')

    # INVERT signals here
    df['Signal'] = df['Signal'] * -1  

    df['Position'] = 0.0
    df['P&L'] = 0.0
    current_lot = base_lot
    entry_price = None

    for i in range(1, len(df)):
        signal = df.at[i-1, 'Signal']
        if pd.isna(df.at[i-1, 'Close']):
            continue

        price_change = df.at[i, 'Close'] - df.at[i-1, 'Close']

        # Open first position if signal exists
        if signal != 0 and entry_price is None:
            entry_price = df.at[i-1, 'Close']
            df.at[i, 'Position'] = current_lot
            df.at[i, 'P&L'] = price_change * signal * current_lot
            continue

        # Update P&L for open position
        if entry_price is not None:
            df.at[i, 'P&L'] = price_change * signal * current_lot
            df.at[i, 'Position'] = current_lot

            # Check take profit
            if (df.at[i, 'Close'] - entry_price) * signal >= take_profit:
                current_lot = base_lot
                entry_price = None  # close position

            # Check step against trade → open next Martingale lot
            elif abs(df.at[i, 'Close'] - entry_price) >= step:
                current_lot *= multiplier
                entry_price = df.at[i, 'Close']  # new entry for next lot

    df['Cumulative_Returns'] = df['P&L'].cumsum()
    return df
