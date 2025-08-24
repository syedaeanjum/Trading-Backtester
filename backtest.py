def backtest(df, starting_equity=1000.0):
    """
    Backtest a strategy.
    - df must have 'P&L' column
    - starting_equity: initial account balance
    
    """
    df = df.copy()
    
    # Ensure P&L exists
    if 'P&L' not in df.columns:
        df['P&L'] = 0.0

    # Compute cumulative returns from starting equity
    df['Cumulative_Returns'] = df['P&L'].cumsum() + starting_equity

    # Performance summary
    total_trades = df['P&L'].astype(bool).sum()
    total_pnl = df['P&L'].sum()
    max_drawdown = (df['Cumulative_Returns'].cummax() - df['Cumulative_Returns']).max()
    ending_equity = df['Cumulative_Returns'].iloc[-1]

    print("\n=== Performance Summary ===")
    print(f"Starting Equity   : {starting_equity:.2f}")
    print(f"Total Trades Taken: {total_trades}")
    print(f"Total P&L        : {total_pnl:.2f}")
    print(f"Max Drawdown     : {max_drawdown:.2f}")
    print(f"Ending Equity    : {ending_equity:.2f}")
    print("============================")

    return df
