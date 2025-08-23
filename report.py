import matplotlib.pyplot as plt

def plot_price_with_signals(df):
    plt.figure(figsize=(12,6))
    plt.plot(df['Datetime'], df['Close'], label='Close', alpha=0.5)
    plt.plot(df['Datetime'], df['EMA_short'], label='EMA 9', color='blue')
    plt.plot(df['Datetime'], df['EMA_long'], label='EMA 21', color='orange')

    # Buy/sell markers
    plt.scatter(df[df['Signal']==1]['Datetime'], df[df['Signal']==1]['Close'], marker='^', color='green', label='Buy')
    plt.scatter(df[df['Signal']==-1]['Datetime'], df[df['Signal']==-1]['Close'], marker='v', color='red', label='Sell')

    plt.legend()
    plt.xlabel('Datetime')
    plt.ylabel('Price')
    plt.title('Price with EMA 9/21 Crossover Signals')
    plt.show()

def plot_equity(df):
    plt.figure(figsize=(12,6))
    plt.plot(df['Datetime'], df['Cumulative_Returns'], label='Equity Curve', color='purple')
    plt.xlabel('Datetime')
    plt.ylabel('Cumulative Returns')
    plt.title('Strategy Equity Curve')
    plt.legend()
    plt.show()

def performance_report(df):
    total_return = df['Cumulative_Returns'].iloc[-1] - 1
    num_trades = (df['Signal'] != 0).sum()
    print(f"Total Return: {total_return:.2%}")
    print(f"Number of Trades: {num_trades}")
