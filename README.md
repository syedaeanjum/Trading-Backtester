### Trading Backtesting Framework (Python 🐍)

A modular Python framework for designing, testing, and analyzing trading strategies using historical market data.
Built with clean, well-documented code and beginner-friendly explanations so both engineers and non-traders can follow along.

✨ Features

📊 Data Pipeline:

  - Fetches 1-minute intraday data from Yahoo Finance (SPX, Gold, or any symbol).

   - Cleans and filters data to custom session windows (e.g., New York trading hours).

  - Automatically saves raw and cleaned CSVs for reproducibility.

🧠 Strategies Implemented:

  - Single EMA

    - Buy when price is above the EMA, sell when below.

    - Default: 9 EMA.

- EMA Crossover

    - Trend-following: compare short-term vs long-term EMAs.

    - Default: 9 vs 21 EMA.

- Bollinger Bands (Mean Reversion)

  - Middle band (SMA or EMA), with Upper/Lower bands at ±k × stdev.

  - Buy when price < Lower band, Sell when price > Upper band.

  - Configurable window length, deviation factor, and band type.

- Martingale

  - Scales position size when price moves against you.

  - Parameters for step size, take-profit, and flip rules.

  - Option to ignore flips while in drawdown (close_on_flip=False).

⚙️ Execution Engine

  - Converts signals into trades with:
  
  - Position sizing
  
  - Profit/Loss (P&L)
  
  - Explicit trade closes
  
  - Configurable toggle for behavior on signal flips.

📈 Backtesting & Reporting

Tracks:

  - Equity curve
  
  - Total P&L
  
  - Max drawdown
  
  - Win rate
  
  - Avg trade profit
  
  - Saves Detailed Logs:
  
  - trades.csv → every action (open/add/close).
  
  - trades_summary.csv → one row per completed trade with entry, exit, direction, and P&L.

Auto-generates charts:

  - Equity curve (equity_curve.png)
  
  - Price with buy/sell signals (price_with_signals.png)

📂 Project Structure


├── main.py               |  Run backtests (configure instrument, strategy, params)

├── data.py               |  Fetches intraday data from Yahoo Finance

├── cleaningdata.py       |  Cleans and filters data to session windows

├── strategies.py         |  Strategies (EMA single/crossover, Bollinger, Martingale) + execution engine

├── backtest.py           |  Core backtester: equity curve, trade summary, P&L

├── report.py             |  Reporting: charts + performance summary

├── trades.csv            |  (output) all fills for a run

├── trades_summary.csv    |  (output) round-trip trades



# Clone repo and install dependencies
git clone https://github.com/syedaeanjum/trading-backtester.git

cd trading-backtester

pip install -r requirements.txt



# Run a backtest

python main.py
----------------------------------------------------------

Example Console Output:

Loaded gold data for 2025-08-19 → 2025-08-20, shape: (196, 6)

Martingale strategy applied.


All trades saved to trades.csv (80 rows)

Saved trade summary to trades_summary.csv (21 trades)



--- Performance Summary ---
 
Starting Equity   : 1000.00

Closed Trades     : 21

Win Rate          : 71.43% (15/21)

Avg Trade P&L     : 25.67

Total P&L         : 539.00

Max Drawdown      : 180.50

Ending Equity     : 1539.00

----------------------------------------------------------
🔧 Strategy Configuration Examples



- EMA Single

  strategy = "ema_single"
  
  ema_single_window = 9
  
  ema_position_size = 2.0


- EMA Crossover

  strategy = "ema"
  
  ema_short = 9
  
  ema_long = 21
  
  ema_position_size = 2.0



- Bollinger Bands

  strategy = "bollinger"
  
  bb_window   = 20
  
  bb_num_std  = 2.0
  
  bb_use_ema  = False
  
  bb_hold_mid = True
  
  ema_position_size = 2.0



- Martingale

  strategy = "martingale"
  
  base_lot        = 13.0
  
  multiplier      = 2
  
  step            = 10
  
  take_profit     = 15
  
  reverse_signals = True
  
  close_on_flip   = False





