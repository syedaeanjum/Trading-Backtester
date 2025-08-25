import pandas as pd
def clean_intraday_data(csv_file, start_time="15:00", end_time="18:00"):

    # Load CSV
    df = pd.read_csv(csv_file, parse_dates=["Datetime"])

    # chronological order
    df = df.sort_values("Datetime").reset_index(drop=True)

    # Drop duplicates
    df = df.drop_duplicates(subset="Datetime")

    # Filter to trading hours only
    df = df.set_index("Datetime")
    df = df.between_time(start_time, end_time)

    # Optional: forward-fill missing OHLC/volume
    df = df.ffill()

    # Reset index back
    df = df.reset_index()

    return df


if __name__ == "__main__":
    # Example configuration for backtest time
    backtest_start_time = "08:00"
    backtest_end_time = "11:00"

    # Clean SPX data
    cleaned_df_spx = clean_intraday_data(
        "spx_1min.csv", start_time=backtest_start_time, end_time=backtest_end_time
    )
    print("SPX Preview:")
    print(cleaned_df_spx.head())
    print(cleaned_df_spx.tail())
    cleaned_df_spx.to_csv("spx_1min_clean.csv", index=False)

    # Clean Gold data
    cleaned_df_gold = clean_intraday_data(
        "gold_1min.csv", start_time=backtest_start_time, end_time=backtest_end_time
    )
    print("Gold Preview:")
    print(cleaned_df_gold.head())
    print(cleaned_df_gold.tail())
    cleaned_df_gold.to_csv("gold_1min_clean.csv", index=False)
