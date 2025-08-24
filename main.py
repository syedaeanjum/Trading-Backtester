from cleaningdata import clean_intraday_data
from strategies import ema_crossover, martingale_strategy
from backtest import backtest
from report import plot_equity, plot_price_with_signals, performance_report
import yfinance as yf
import pandas as pd


def fetch_data(ticker, start_date, end_date):
    # Fetch 1-min data from Yahoo Finance 
    all_data = []
    from datetime import datetime, timedelta

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    chunk_size = 7
    # Chunk size is 7 due to Yahoo's limit 

    while start < end:
        chunk_end = min(start + timedelta(days=chunk_size), end)
        print(f"Fetching {ticker} from {start.date()} to {chunk_end.date()}...")
        df = yf.download(
            ticker,
            start=start.strftime("%Y-%m-%d"),
            end=chunk_end.strftime("%Y-%m-%d"),
            interval="1m",
            auto_adjust=True,
        )
        if not df.empty:
            df = df.reset_index()
            df = df[["Datetime", "Open", "High", "Low", "Close", "Volume"]]
            all_data.append(df)
        start = chunk_end + timedelta(days=1)

    return (
        pd.concat(all_data, ignore_index=True)
        if all_data
        else pd.DataFrame(
            columns=["Datetime", "Open", "High", "Low", "Close", "Volume"]
        )
    )


def load_fetch_and_clean(instrument, start_date, end_date, start_time, end_time):
    
    if instrument.lower() == "spx":
        ticker = "^GSPC"
        csv_file = "spx_1min.csv"
    elif instrument.lower() == "gold":
        ticker = "GC=F"
        csv_file = "gold_1min.csv"
    else:
        raise ValueError("Instrument not supported. Choose 'spx' or 'gold'.")

    # Fetch
    df = fetch_data(ticker, start_date, end_date)
    df.to_csv(csv_file, index=False)
    print(f"{instrument.upper()} data saved to {csv_file}, shape: {df.shape}")

    # Clean
    df = clean_intraday_data(csv_file, start_time=start_time, end_time=end_time)
    return df


if __name__ == "__main__":
    
    # ================= CONFIGURATION =================
    
    instrument = "gold"  # "spx" or "gold"
    strategy = "martingale"  # "ema" or "martingale"
    start_date = "2025-08-21"
    end_date = "2025-08-22"
    backtest_start_time = "1:00"
    backtest_end_time = "18:00"

    # Martingale parameters
    base_lot = 10.00
    multiplier = 2
    step = 3500
    take_profit = 3500
    reverse_signals = True  # buy on down signals, sell on up signals

    # Backtest equity
    starting_equity = 1000.0  # configurable starting equity
    
    # =================================================

    
    df = load_fetch_and_clean(
        instrument, start_date, end_date, backtest_start_time, backtest_end_time
    )
    print(
        f"\nLoaded {instrument} data for {start_date} → {end_date}, shape: {df.shape}"
    )

    # Apply strategy
    if strategy.lower() == "ema":
        df = ema_crossover(df)
        print("EMA crossover signals generated.")
    elif strategy.lower() == "martingale":
        df = ema_crossover(df)  # EMA signals required for Martingale
        df = martingale_strategy(
            df,
            base_lot=base_lot,
            multiplier=multiplier,
            step=step,
            take_profit=take_profit,
        )
        print("Martingale strategy applied.")
    else:
        raise ValueError("Strategy not supported. Choose 'ema' or 'martingale'.")

    # Run backtest with starting equity
    results = backtest(df, starting_equity=starting_equity)
    print("Backtest complete.")

    # Generate reports
    plot_equity(results)
    plot_price_with_signals(results)
    performance_report(results)
