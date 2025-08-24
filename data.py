import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_data(ticker, start_date, end_date, interval="1m"):
    """
    Fetch intraday data (default 1-min) from Yahoo Finance in chunks.
    
    ticker: Yahoo Finance symbol (e.g., '^GSPC' for S&P 500, 'GC=F' for Gold futures)
    start_date, end_date: date range in 'YYYY-MM-DD' format
    interval: data frequency (default '1m')
    
    """

    all_data = []  # store chunks
    chunk_size = 7  # days per request
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    while start < end:
        chunk_end = min(start + timedelta(days=chunk_size), end)
        print(f"Fetching {ticker} from {start.date()} to {chunk_end.date()}...")

        # Download data
        df = yf.download(
            ticker,
            start=start.strftime('%Y-%m-%d'),
            end=chunk_end.strftime('%Y-%m-%d'),
            interval=interval,
            auto_adjust=True
        )

        if not df.empty:
            df = df.reset_index()  # make Datetime a column
            
            # Standardize columns
            if "Datetime" not in df.columns:
                df = df.rename(columns={"index": "Datetime"})
            df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
            all_data.append(df)

        # Move to next chunk
        start = chunk_end + timedelta(days=1)

    # Combine chunks
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame(columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume'])


if __name__ == "__main__":
    
    # Fetch SPX
    spx_df = fetch_data('^GSPC', '2025-08-01', '2025-08-15')
    print("SPX Preview:")
    print(spx_df.head())
    spx_df.to_csv('spx_1min.csv', index=False)

    # Fetch Gold 
    gold_df = fetch_data('GC=F', '2025-08-21', '2025-08-22')
    print("Gold Preview:")
    print(gold_df.head())
    gold_df.to_csv('gold_1min.csv', index=False)
