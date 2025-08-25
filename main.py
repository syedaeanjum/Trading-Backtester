from cleaningdata import clean_intraday_data
from strategies import (
    ema_single,          # single-EMA signals (e.g., 9 EMA)
    ema_crossover,       # short/long EMA crossover
    execute_signals,     # turns signals into trades/P&L/Closed flags
    martingale_strategy  # martingale engine
)
from backtest import backtest
from report import plot_equity, plot_price_with_signals, performance_report
import yfinance as yf
import pandas as pd


def fetch_data(ticker: str, start_date: str, end_date: str, interval: str = "1m") -> pd.DataFrame:
    """
    Download intraday data from Yahoo Finance in week-sized chunks (Yahoo limit).
    Returns columns: Datetime, Open, High, Low, Close, Volume
    """
    all_data = []
    from datetime import datetime, timedelta

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    chunk_size = 7  # days per request (Yahoo limit)

    while start < end:
        chunk_end = min(start + timedelta(days=chunk_size), end)
        print(f"Fetching {ticker} from {start.date()} to {chunk_end.date()}...")
        df = yf.download(
            ticker,
            start=start.strftime("%Y-%m-%d"),
            end=chunk_end.strftime("%Y-%m-%d"),  # Yahoo end is exclusive
            interval=interval,
            auto_adjust=True,
        )
        if not df.empty:
            df = df.reset_index()
            # Standardize column names
            if "Datetime" not in df.columns and "index" in df.columns:
                df = df.rename(columns={"index": "Datetime"})
            df = df[["Datetime", "Open", "High", "Low", "Close", "Volume"]]
            all_data.append(df)
        # Move to the day after chunk_end (since Yahoo end is exclusive)
        start = chunk_end + timedelta(days=1)

    if all_data:
        out = pd.concat(all_data, ignore_index=True)
    else:
        out = pd.DataFrame(columns=["Datetime", "Open", "High", "Low", "Close", "Volume"])
    return out


def load_fetch_and_clean(instrument: str, start_date: str, end_date: str, start_time: str, end_time: str) -> pd.DataFrame:
    """
    Fetch raw data for the instrument, save to CSV, then trim to the session window.
    """
    if instrument.lower() == "spx":
        ticker = "^GSPC"
        csv_file = "spx_1min.csv"
    elif instrument.lower() == "gold":
        ticker = "GC=F"
        csv_file = "gold_1min.csv"
    else:
        raise ValueError("Instrument not supported. Choose 'spx' or 'gold'.")

    # Fetch & persist raw
    df = fetch_data(ticker, start_date, end_date, interval="1m")
    df.to_csv(csv_file, index=False)
    print(f"{instrument.upper()} data saved to {csv_file}, shape: {df.shape}")

    # Clean to session window (e.g., 09:30–16:00 for equities)
    df_clean = clean_intraday_data(csv_file, start_time=start_time, end_time=end_time)
    return df_clean


if __name__ == "__main__":
    
    
    # ================= CONFIGURATION =================
    
    instrument = "gold"                # "spx" or "gold"

    # Choose one: "ema_single" (price vs one EMA), "ema" (two-EMA crossover), or "martingale"
    strategy = "martingale"

    # Date range
    start_date = "2025-08-19"
    end_date   = "2025-08-20"

    # Session window (HH:MM in 24h)
    backtest_start_time = "15:00"
    backtest_end_time   = "17:00"

    # --- EMA settings ---
    ema_single_window  = 9      # for ema_single
    ema_short          = 9      # for ema crossover
    ema_long           = 21
    ema_position_size  = 2.0    # lot size for EMA-only strategies

    # --- Martingale settings (only used if strategy == "martingale") ---
    base_lot        = 13.00
    multiplier      = 2
    step            = 10          # price units for add
    take_profit     = 15          # price units for TP
    reverse_signals = True        # invert EMA signals before martingale logic
    close_on_flip   = False       # don't close on flip while in drawdown

    # Backtest equity
    starting_equity = 1000.0
    # =================================================

    # Load data
    df = load_fetch_and_clean(
        instrument, start_date, end_date, backtest_start_time, backtest_end_time
    )
    print(f"\nLoaded {instrument} data for {start_date} → {end_date}, shape: {df.shape}")

    # Build signals + optional execution engine
    trades_df = None
    if strategy.lower() == "ema_single":
        # Single EMA signals (BUY when price > EMA(window), SELL when price < EMA(window))
        df = ema_single(df, window=ema_single_window)
        # Turn signals into actual positions/P&L/Closed flags
        df = execute_signals(df, position_size=ema_position_size, flat_on_zero=True)
        print(f"{ema_single_window} EMA signals generated (position size={ema_position_size}).")

    elif strategy.lower() == "ema":
        # Two-EMA crossover signals (short vs long)
        df = ema_crossover(df, short_window=ema_short, long_window=ema_long)
        # Turn signals into actual positions/P&L/Closed flags
        df = execute_signals(df, position_size=ema_position_size, flat_on_zero=True)
        print(f"EMA crossover signals generated (short={ema_short}, long={ema_long}, position size={ema_position_size}).")

    elif strategy.lower() == "martingale":
        # Martingale uses EMA signals as a directional base first
        df = ema_crossover(df, short_window=ema_short, long_window=ema_long)
        # Apply Martingale engine (produces trades_df/fills and P&L directly)
        df, trades_df = martingale_strategy(
            df,
            base_lot=base_lot,
            multiplier=multiplier,
            step=step,
            take_profit=take_profit,
            reverse_signals=reverse_signals,
            close_on_flip=close_on_flip,
        )
        print("Martingale strategy applied.")
    else:
        raise ValueError("Strategy not supported. Choose 'ema_single', 'ema', or 'martingale'.")

    # Run backtest (saves trades.csv and trades_summary.csv; prints summary)
    results = backtest(df, starting_equity=starting_equity, trades_df=trades_df)
    print("Backtest complete.")

    # Save plots and print a readable report
    plot_equity(results)
    plot_price_with_signals(results)
    performance_report(results)
