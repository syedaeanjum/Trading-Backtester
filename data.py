import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_spx_1min(start_date, end_date):
    # Fetch SPX 1-min data from Yahoo Finance 
    
    all_data = []  # store chunks
    chunk_size = 7  # days per request
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    while start < end:
        chunk_end = min(start + timedelta(days=chunk_size), end)
        print(f"Fetching {start.date()} to {chunk_end.date()}...")
        
        # download data
        df = yf.download(
            '^GSPC', 
            start=start.strftime('%Y-%m-%d'),
            end=chunk_end.strftime('%Y-%m-%d'), 
            interval='1m', 
            auto_adjust=True
        )

        if not df.empty:
            df = df.reset_index()  # make Datetime a column
            df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]  # Select columns
            all_data.append(df)  # Ssave chunk

        start = chunk_end + timedelta(days=1)  # next chunk

    # Combine chunks or return empty
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame(columns=['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume'])

if __name__ == "__main__":
    spx_1min_df = fetch_spx_1min('2025-07-15', '2025-08-15')  # fetch data
    print(spx_1min_df.head())  # show preview
    spx_1min_df.to_csv('spx_1min.csv', index=False)  # save CSV
