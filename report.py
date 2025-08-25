import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def _max_drawdown(equity: pd.Series) -> float:
    """
    
    Find the worst drop (loss) from a peak to a low point in the equity curve.
    In simple terms: what's the biggest fall in account value during the test?
    
    """
    if equity is None or equity.empty:
        return 0.0
    peak = equity.cummax()              # running highest value reached
    return float((peak - equity).max()) # difference between the high and the low after it

def plot_equity(df: pd.DataFrame, outfile: str = "equity_curve.png"):
    
    # Draw and save a line chart showing how account balance (equity) changed over time.
    
    required = {'Datetime', 'Cumulative_Returns'}
    if not required.issubset(df.columns):
        raise ValueError("DataFrame must include 'Datetime' and 'Cumulative_Returns' columns.")

    plt.figure(figsize=(12, 6))
    plt.plot(df['Datetime'], df['Cumulative_Returns'], label='Equity Curve')
    plt.title("Equity Curve (Account Value Over Time)")
    plt.xlabel("Time")
    plt.ylabel("Account Value")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outfile, dpi=144, bbox_inches="tight")
    plt.close()
    print(f"[saved plot] {outfile}")  # Tells user where the picture was saved

def plot_price_with_signals(df: pd.DataFrame, outfile: str = "price_with_signals.png"):
    
    # Draw and save a chart of the price with markers for when the strategy said BUY or SELL.
    
    required = {'Datetime', 'Close', 'Signal'}
    if not required.issubset(df.columns):
        raise ValueError("DataFrame must include 'Datetime', 'Close', and 'Signal' columns.")

    buys = df[df['Signal'] == 1]   # rows where strategy said "buy"
    sells = df[df['Signal'] == -1] # rows where strategy said "sell"

    plt.figure(figsize=(12, 6))
    plt.plot(df['Datetime'], df['Close'], label='Price')
    if not buys.empty:
        plt.scatter(buys['Datetime'], buys['Close'], marker='^', label='Buy', s=40)
    if not sells.empty:
        plt.scatter(sells['Datetime'], sells['Close'], marker='v', label='Sell', s=40)
    plt.title("Price with Buy/Sell Signals")
    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outfile, dpi=144, bbox_inches="tight")
    plt.close()
    print(f"[saved plot] {outfile}")

def _extract_trades_from_positions(df: pd.DataFrame) -> pd.DataFrame:

    required = {'Position', 'P&L', 'Datetime'}
    if not required.issubset(df.columns) or df.empty:
        return pd.DataFrame(columns=['EntryTime','ExitTime','Direction','TradePnL'])

    pos = df['Position'].fillna(0).to_numpy()
    trades, in_trade, entry_i, entry_pos = [], False, None, 0.0
    n = len(df)

    for i in range(n):
        if not in_trade:
            # Start a trade when we go from no position (0) to holding something
            if pos[i] != 0 and (i == 0 or pos[i-1] == 0):
                in_trade, entry_i, entry_pos = True, i, pos[i]
        else:
            # End a trade when we return to 0 (flat again)
            if pos[i] == 0:
                exit_i = i
                pnl_slice = df['P&L'].iloc[entry_i+1:exit_i+1] # sum profit/loss between entry and exit
                trade_pnl = float(pnl_slice.sum()) if len(pnl_slice) else 0.0
                trades.append({
                    'EntryTime': df['Datetime'].iloc[entry_i],
                    'ExitTime':  df['Datetime'].iloc[exit_i],
                    'Direction': 'LONG' if entry_pos > 0 else 'SHORT',
                    'TradePnL':  trade_pnl,
                })
                in_trade, entry_i = False, None

    # If a trade was still open at the end, close it there
    if in_trade and entry_i is not None:
        exit_i = n - 1
        pnl_slice = df['P&L'].iloc[entry_i+1:exit_i+1]
        trade_pnl = float(pnl_slice.sum()) if len(pnl_slice) else 0.0
        trades.append({
            'EntryTime': df['Datetime'].iloc[entry_i],
            'ExitTime':  df['Datetime'].iloc[exit_i],
            'Direction': 'LONG' if entry_pos > 0 else 'SHORT',
            'TradePnL':  trade_pnl,
        })

    return pd.DataFrame(trades, columns=['EntryTime','ExitTime','Direction','TradePnL'])

def performance_report(df: pd.DataFrame):
    """
    Print a simple summary of how the strategy performed.
    """
    equity = df['Cumulative_Returns']                # account value over time
    total_pnl = float(df['P&L'].sum())               # total profit or loss
    max_dd = _max_drawdown(equity)                   # biggest drop in account value
    ending = float(equity.iloc[-1]) if len(equity) else float('nan')

    # Count number of trade "fills" (every time we bought or sold something)
    fills_count = None
    if Path("trades.csv").exists():
        try:
            fills_count = len(pd.read_csv("trades.csv"))
        except Exception:
            fills_count = None

    # Try to load proper trade summary (round trips with entry + exit)
    if Path("trades_summary.csv").exists():
        try:
            trade_summ = pd.read_csv("trades_summary.csv")
        except Exception:
            trade_summ = _extract_trades_from_positions(df)
    else:
        trade_summ = _extract_trades_from_positions(df)

    closed_trades = int(len(trade_summ)) if trade_summ is not None else 0
    wins = int((trade_summ['TradePnL'] > 0).sum()) if closed_trades else 0
    win_rate = (wins / closed_trades) * 100.0 if closed_trades else 0.0
    avg_trade = float(trade_summ['TradePnL'].mean()) if closed_trades else 0.0

    # Print the results
    print("\n=== Performance Summary ===")
    if fills_count is not None:
        print(f"Fills Logged      : {fills_count}  (rows in trades.csv)")  # every action
    print(f"Closed Trades     : {closed_trades}")                        # completed round-trips
    print(f"Win Rate          : {win_rate:.2f}% ({wins}/{closed_trades})")
    print(f"Avg Trade P&L     : {avg_trade:.2f}")                        # average profit per trade
    print(f"Total P&L         : {total_pnl:.2f}")                        # overall profit/loss
    print(f"Max Drawdown      : {max_dd:.2f}")                           # biggest loss during test
    print(f"Ending Equity     : {ending:.2f}")                           # account balance at end
    print("============================\n")
