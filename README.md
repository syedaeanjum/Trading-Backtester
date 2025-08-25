### Trading Backtesting Framework (Python 🐍)

A modular Python framework for designing, testing, and analyzing trading strategies using historical market data.
Built with clean, well-documented code and beginner-friendly explanations so both engineers and non-traders can follow along.

✨ Features:

Data Pipeline:

  - Fetches 1-minute intraday data from Yahoo Finance (SPX, Gold, or any symbol).
  
  - Cleans and filters data to session windows (e.g., New York hours).

Strategies Implemented:

  - Single EMA: Buy when price is above the 9 EMA, sell when below.
  
  - EMA Crossover: Trend-following using short-term vs long-term EMAs.
  
  - Martingale: Scales position size when price moves against you, with parameters for step size, take-profit, and flip rules.

Execution Engine:
  
  - Converts signals into trades with position sizing, profit/loss (P&L), and explicit trade closes.
  
  - Option to toggle behavior on signal flips (close_on_flip).

Backtesting & Reporting:

  - Tracks equity curve, total P&L, max drawdown, win rate, and average trade profit.

Saves Detailed Logs:

  - trades.csv → every action (open/add/close).
  
  - trades_summary.csv → one row per completed trade with entry, exit, direction, and P&L.

Auto-Generates Charts:

  - Equity curve (equity_curve.png).
  
  - Price with buy/sell signals (price_with_signals.png).

📂 Project Structure


├── main.py           |  Run backtests (configure instrument, strategy, params)

├── data.py           |  Fetches intraday data from Yahoo Finance

├── cleaningdata.py   |  Cleans and filters data to session windows

├── strategies.py     |  Strategies (EMA, crossover, martingale) + execution engine

├── backtest.py       |  Core backtester: equity curve, trade summary, P&L

├── report.py         |  Reporting: charts + performance summary

├── trades.csv        |  (output) all fills for a run

├──                   |  trades_summary.csv# (output) round-trip trades



# Clone repo and install dependencies
git clone https://github.com/syedaeanjum/trading-backtester.git

cd trading-backtester

pip install -r requirements.txt



# Run a backtest

python main.py

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

------------------------------

