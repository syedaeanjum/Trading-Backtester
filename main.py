import pandas as pd
from strategies import ema_crossover
from backtest import backtest
from report import plot_equity, plot_price_with_signals, performance_report

def main():
    # Load cleaned data
    df = pd.read_csv("spx_1min_clean.csv", parse_dates=['Datetime'])

    # Apply EMA 9/21 crossover strategy
    df = ema_crossover(df, short_window=9, long_window=21)

    # Run backtest
    df = backtest(df)

    # Plot results
    plot_price_with_signals(df)  # price + EMA + buy/sell arrows
    plot_equity(df)              # cumulative returns (equity curve)

    # Print performance metrics
    performance_report(df)

if __name__ == "__main__":
    main()
