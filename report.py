import matplotlib.pyplot as plt

def plot_equity(df):

    plt.figure(figsize=(12, 6))
    plt.plot(df['Datetime'], df['Cumulative_Returns'], label='Equity Curve', color='purple')
    plt.title("Equity Curve")
    plt.xlabel("Datetime")
    plt.ylabel("Cumulative Returns")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_price_with_signals(df):

    plt.figure(figsize=(12, 6))
    plt.plot(df['Datetime'], df['Close'], label='Close Price', color='blue')

    # Plot buy signals
    buy_signals = df[df['Signal'] == 1]
    plt.scatter(buy_signals['Datetime'], buy_signals['Close'], marker='^', color='green', label='Buy Signal')

    # Plot sell signals
    sell_signals = df[df['Signal'] == -1]
    plt.scatter(sell_signals['Datetime'], sell_signals['Close'], marker='v', color='red', label='Sell Signal')

    plt.title("Price with Signals")
    plt.xlabel("Datetime")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def performance_report(df):

    total_trades = df['Signal'].abs().sum()
    total_pnl = df['P&L'].sum()
    max_drawdown = df['Cumulative_Returns'].min()
    ending_equity = df['Cumulative_Returns'].iloc[-1]

    print("\n=== Performance Summary ===")
    print(f"Total Trades Taken : {total_trades}")
    print(f"Total P&L         : {total_pnl:.2f}")
    print(f"Max Drawdown      : {max_drawdown:.2f}")
    print(f"Ending Equity     : {ending_equity:.2f}")
    print("============================\n")
