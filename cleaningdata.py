import pandas as pd

def clean_intraday_data(csv_file, start_time="15:00", end_time="18:00"):
    """
    Load and clean intraday data from CSV:
    - Parse datetime
    - Sort chronologically
    - Drop duplicates
    - Filter to market hours (default: NYSE 09:30–16:00)
    - Forward-fill any missing values
    """

    # Load CSV
    df = pd.read_csv(csv_file, parse_dates=['Datetime'])

    # Ensure chronological order
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
    cleaned_df = clean_intraday_data("spx_1min.csv")
    print(cleaned_df.head())
    print(cleaned_df.tail())

    # Save clean dataset
    cleaned_df.to_csv("spx_1min_clean.csv", index=False)
