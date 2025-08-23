import pandas as pd

# 9 ema
def ema_crossover(df, short_window=9, long_window=21):
    df = df.copy()
    df['EMA_short'] = df['Close'].ewm(span=short_window, adjust=False).mean()
    df['EMA_long'] = df['Close'].ewm(span=long_window, adjust=False).mean()
    
    df['Signal'] = 0
    df.loc[df['EMA_short'] > df['EMA_long'], 'Signal'] = 1
    df.loc[df['EMA_short'] < df['EMA_long'], 'Signal'] = -1
    
    return df
