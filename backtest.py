import pandas as pd
from typing import Optional

def _max_drawdown(series: pd.Series) -> float:
    """
    Max drawdown = the worst drop from a high point to a later low point
    in the equity curve. In everyday words: "What was the biggest dip
    in the account value during the test?"
    """
    if series is None or series.empty:
        return 0.0
    peak = series.cummax()        # running highest value seen so far
    drawdown = peak - series      # how far we are below the best point
    return float(drawdown.max())  # the largest dip

def _extract_trades_from_positions(df: pd.DataFrame) -> pd.DataFrame:

    required = {'Position', 'P&L', 'Datetime', 'Closed'}
    if not required.issubset(df.columns) or df.empty:
        return pd.DataFrame(columns=['EntryTime', 'ExitTime', 'Direction', 'TradePnL'])

    # Convenience arrays for quick checks
    pos = df['Position'].fillna(0).to_numpy()   # + means long, - means short, 0 means flat (no trade)
    closed = df['Closed'].fillna(0).to_numpy()  # 1 marks a bar where a trade was closed

    trades = []          # we will append a dict for each completed trade
    in_trade = False     # are we currently inside a trade?
    entry_i = None       # index where the current trade started
    entry_pos = 0.0      # the position sign/size at entry (sign tells us long/short)

    for i in range(len(df)):
        if not in_trade:
            # Start a trade when we’re flat (0) and this bar shows a non-zero position.
            if pos[i] != 0 and (i == 0 or pos[i-1] == 0):
                in_trade = True
                entry_i = i
                entry_pos = pos[i]
        else:
            # Close the trade if this bar is marked as an exit (TP, flip, or session end)
            if closed[i] == 1:
                exit_i = i
                # Sum profit/loss from the bar *after* we entered up to and including this exit bar
                pnl_slice = df['P&L'].iloc[entry_i+1:exit_i+1]
                trade_pnl = float(pnl_slice.sum()) if len(pnl_slice) else 0.0

                trades.append({
                    'EntryTime': df['Datetime'].iloc[entry_i],
                    'ExitTime':  df['Datetime'].iloc[exit_i],
                    'Direction': 'LONG' if entry_pos > 0 else 'SHORT',
                    'TradePnL':  trade_pnl,
                })

                # We are flat again after closing
                in_trade = False
                entry_i = None
                entry_pos = 0.0

                # Special case: if the strategy flipped on this same bar,
                # a new position may already be open. If so, start a new trade immediately.
                if pos[i] != 0:
                    in_trade = True
                    entry_i = i
                    entry_pos = pos[i]

    # If session is up while in a trade, close it at the last bar
    
    if in_trade and entry_i is not None:
        exit_i = len(df) - 1
        pnl_slice = df['P&L'].iloc[entry_i+1:exit_i+1]
        trade_pnl = float(pnl_slice.sum()) if len(pnl_slice) else 0.0
        trades.append({
            'EntryTime': df['Datetime'].iloc[entry_i],
            'ExitTime':  df['Datetime'].iloc[exit_i],
            'Direction': 'LONG' if entry_pos > 0 else 'SHORT',
            'TradePnL':  trade_pnl,
        })

    # Return a table of finished trades
    return pd.DataFrame(trades, columns=['EntryTime', 'ExitTime', 'Direction', 'TradePnL'])

def backtest(
    df: pd.DataFrame,
    starting_equity: float = 1000.0,
    trades_df: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    What this does:
    1) Builds the equity curve (account value over time) from the bar-by-bar P&L.
    2) Saves two CSVs for you to inspect:
        - trades.csv          → every action/fill (open/add/flip/close). Good for detailed logs.
        - trades_summary.csv  → one row per completed trade with entry/exit and P&L.
    3) Prints a summary: closed trades, win rate, total P&L, worst drawdown, ending equity.

    Inputs:
        - df : your bar data with at least 'P&L', 'Position', 'Closed', 'Datetime'
        - starting_equity : where the account starts
        - trades_df  : optional detailed fills from the strategy (if provided, we save it directly)
    """
    df = df.copy()

    # Make sure we have essential columns.
    if 'P&L' not in df.columns:
        df['P&L'] = 0.0
    if 'Closed' not in df.columns:
        # If the strategy didn’t mark exits, we assume none (win-rate may not be meaningful).
        df['Closed'] = 0

    # 1) Equity curve: account value at each step = starting money + sum of P&L so far
    equity = df['P&L'].cumsum() + starting_equity
    df['Cumulative_Returns'] = equity

    # Totals for the printout
    total_pnl = float(df['P&L'].sum())
    max_dd    = _max_drawdown(equity)
    ending    = float(equity.iloc[-1]) if len(equity) else starting_equity

    # 2) Save a detailed fills log (every action). If the strategy provided a table, use it.
    if trades_df is not None and not trades_df.empty:
        out = trades_df.copy()
        out.to_csv("trades.csv", index=False)
        print(f"\nAll trades saved to trades.csv ({len(out)} rows)\n")
    else:
        fallback = df[df['P&L'] != 0].copy()
        if not fallback.empty:
            if 'Signal' in df.columns:
                fallback['Action'] = df.loc[fallback.index, 'Signal'].map({1: 'BUY', -1: 'SELL', 0: 'HOLD'})
            else:
                fallback['Action'] = 'TRADE'
            fallback_out = fallback.reset_index()[['Datetime', 'Action', 'Close', 'P&L', 'Cumulative_Returns']]
            fallback_out.to_csv("trades.csv", index=False)
            print(f"\nAll trades saved to trades.csv (fallback: {len(fallback_out)} rows)\n")

    # Build the one-row-per-trade summary using the explicit Closed flags
    trade_summ = _extract_trades_from_positions(df)
    trade_summ.to_csv("trades_summary.csv", index=False)
    print(f"Saved trade summary to trades_summary.csv ({len(trade_summ)} trades)")

    # Win rate and average trade P&L from the trade summary
    closed_trades = int(len(trade_summ))
    if closed_trades > 0:
        wins = int((trade_summ['TradePnL'] > 0).sum())
        win_rate = (wins / closed_trades) * 100.0
        avg_trade = float(trade_summ['TradePnL'].mean())
    else:
        wins = 0
        win_rate = 0.0
        avg_trade = 0.0

    # 3) Print a clear summary to the console
    print("\n=== Performance Summary ===")
    print(f"Starting Equity   : {starting_equity:.2f}")
    print(f"Closed Trades     : {closed_trades}")                   # number of full round-trips
    print(f"Win Rate          : {win_rate:.2f}% ({wins}/{closed_trades})")
    print(f"Avg Trade P&L     : {avg_trade:.2f}")                   # average profit per completed trade
    print(f"Total P&L         : {total_pnl:.2f}")                   # overall profit/loss
    print(f"Max Drawdown      : {max_dd:.2f}")                      # biggest peak-to-trough dip
    print(f"Ending Equity     : {ending:.2f}")                      # account value at the end
    print("============================")


    return df
