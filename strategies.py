import pandas as pd


# =====================  SIMPLE SIGNAL STRATEGIES  =====================


def ema_single(df: pd.DataFrame, window: int = 9) -> pd.DataFrame:
    """
    Single EMA Strategy:
    1) Compute one EMA (an average of price that favors recent data).
    2) If price is above the EMA → set Signal =  +1 (BUY).
    3) If price is below the EMA → set Signal =  -1 (SELL).

    """
    df = df.copy()

    # Make sure 'Close' is numeric; if not, convert bad strings to NaN
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

    # Calculate the EMA line we compare price against
    df["EMA"] = df["Close"].ewm(span=window, adjust=False).mean()

    # Build signals based on where price is relative to the EMA
    df["Signal"] = 0
    mask_valid = df["Close"].notna() & df["EMA"].notna()
    df.loc[mask_valid & (df["Close"] > df["EMA"]), "Signal"] = 1  # BUY
    df.loc[mask_valid & (df["Close"] < df["EMA"]), "Signal"] = -1  # SELL

    return df


def ema_crossover(
    df: pd.DataFrame, short_window: int = 9, long_window: int = 21
) -> pd.DataFrame:
    """
    EMA Crossover Strategy (classic trend-following idea):
    1) Compute two EMAs: a short-term one and a long-term one.
    2) If short EMA is above long EMA → set Signal = +1 (BUY).
    3) If short EMA is below long EMA → set Signal = -1 (SELL).

    Note: This only creates signals. To get P&L and trades, call execute_signals() after this.
    """
    df = df.copy()

    # Make sure 'Close' is numeric
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

    # Short-term and long-term moving averages of price
    df["EMA_short"] = df["Close"].ewm(span=short_window, adjust=False).mean()
    df["EMA_long"] = df["Close"].ewm(span=long_window, adjust=False).mean()

    # Signals based on the relative position of the two EMAs
    df["Signal"] = 0
    mask_valid = df["EMA_short"].notna() & df["EMA_long"].notna()
    df.loc[mask_valid & (df["EMA_short"] > df["EMA_long"]), "Signal"] = 1
    df.loc[mask_valid & (df["EMA_short"] < df["EMA_long"]), "Signal"] = -1

    return df


# =====================  TURN SIGNALS INTO TRADES (NO MARTINGALE)  =====================


def execute_signals(
    df: pd.DataFrame,
    position_size: float = 1.0,
    flat_on_zero: bool = True,
) -> pd.DataFrame:

    df = df.copy()
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

    # Initialize columns
    df["Position"] = 0.0
    df["P&L"] = 0.0
    df["Closed"] = 0

    side_prev = 0  # +1 long, -1 short, 0 flat

    for i in range(1, len(df)):
        price_prev = df.at[i - 1, "Close"]
        price_now = df.at[i, "Close"]
        if pd.isna(price_prev) or pd.isna(price_now):
            continue

        # Decide what we held during THIS bar using the previous bar's signal
        sig_prev = int(df.at[i - 1, "Signal"]) if "Signal" in df.columns else 0
        target_side = sig_prev if (sig_prev != 0 or flat_on_zero) else side_prev

        # P&L earned/lost during this bar from the side we were holding
        if side_prev != 0:
            df.at[i, "P&L"] = (price_now - price_prev) * side_prev * position_size

        # If our target side changes, the current bar is an exit (close here)
        if side_prev != 0 and target_side != side_prev:
            df.at[i, "Closed"] = 1

        # Adopt the new side going forward
        side_prev = target_side
        df.at[i, "Position"] = side_prev * position_size

    # If still in a trade at the end, mark the last bar as closed
    if side_prev != 0 and len(df) > 0:
        last_i = len(df) - 1
        df.at[last_i, "Closed"] = 1

    return df


# =====================  MARTINGALE STRATEGY (SELF-CONTAINED)  =====================


def martingale_strategy(
    df: pd.DataFrame,
    base_lot: float = 0.02,       # starting trade size
    multiplier: float = 2.0,      # how much to increase after price moves against us
    step: float = 10.0,           # how far price must move against us before adding more
    take_profit: float = 5.0,     # how much gain we want before closing the trade
    reverse_signals: bool = False,# whether to flip signals (buy↔sell)
    close_on_flip: bool = False   # if False, ignore flips while in drawdown
):
    df = df.copy()
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')

    sig_mult = -1 if reverse_signals else 1
    df['Signal'] = (df['Signal'] * sig_mult) if 'Signal' in df.columns else 0

    df['Position'] = 0.0
    df['P&L']      = 0.0
    df['Closed']   = 0
    trades = []

    side = 0              # +1 long, -1 short, 0 flat
    current_lot = 0.0
    entry_price = None

    for i in range(1, len(df)):
        price_prev = df.at[i-1, 'Close']
        price_now  = df.at[i,   'Close']
        if pd.isna(price_prev) or pd.isna(price_now):
            continue

        sig = int(df.at[i-1, 'Signal'])

        # Open when flat and a signal appears
        if side == 0 and sig != 0:
            side = sig
            current_lot = base_lot
            entry_price = price_prev
            trades.append({
                'Datetime': df.at[i-1, 'Datetime'],
                'Action':  'BUY' if side == 1 else 'SELL',
                'Close':   entry_price,
                'Position': current_lot * side,
                'Note': 'Open'
            })

        # Manage open trade
        if side != 0 and entry_price is not None:
            delta   = (price_now - price_prev) * side
            bar_pnl = delta * current_lot
            df.at[i, 'P&L'] = bar_pnl
            df.at[i, 'Position'] = current_lot * side

            # Take Profit
            if (price_now - entry_price) * side >= take_profit:
                trades.append({
                    'Datetime': df.at[i, 'Datetime'],
                    'Action':  'SELL' if side == 1 else 'BUY',
                    'Close':   price_now,
                    'Position': 0.0,
                    'Note': f'TP close (+{take_profit})'
                })
                df.at[i, 'Position'] = 0.0
                df.at[i, 'Closed']   = 1
                side = 0
                current_lot = 0.0
                entry_price = None
                continue

            # Martingale add if price moved against entry by 'step'
            if abs(price_now - entry_price) >= step:
                current_lot = current_lot * multiplier if current_lot > 0 else base_lot
                entry_price = price_now
                trades.append({
                    'Datetime': df.at[i, 'Datetime'],
                    'Action':  'BUY' if side == 1 else 'SELL',
                    'Close':   price_now,
                    'Position': current_lot * side,
                    'Note': f'Add x{multiplier}'
                })

        # Flip handling
        if side != 0 and sig != 0 and sig != side:
            # Check unrealized P&L from entry (are we in drawdown?)
            in_drawdown = ((price_now - entry_price) * side) < 0 if entry_price is not None else False

            if close_on_flip or not in_drawdown:
                # Close current side
                trades.append({
                    'Datetime': df.at[i, 'Datetime'],
                    'Action':  'SELL' if side == 1 else 'BUY',
                    'Close':   price_now,
                    'Position': 0.0,
                    'Note': 'Flip close' if close_on_flip else 'Flip close (no DD)'
                })
                df.at[i, 'Closed']   = 1
                df.at[i, 'Position'] = 0.0

                # Open new side
                side = sig
                current_lot = base_lot
                entry_price = price_now
                trades.append({
                    'Datetime': df.at[i, 'Datetime'],
                    'Action':  'BUY' if side == 1 else 'SELL',
                    'Close':   entry_price,
                    'Position': current_lot * side,
                    'Note': 'Flip open'
                })
                df.at[i, 'Position'] = current_lot * side
            else:
                # Ignore flip while in drawdown; keep riding current position
                pass

    # Force close at end of session if still open
    if side != 0 and entry_price is not None and len(df) > 0:
        last_i = len(df) - 1
        last_price = df.at[last_i, 'Close']
        trades.append({
            'Datetime': df.at[last_i, 'Datetime'],
            'Action':  'SELL' if side == 1 else 'BUY',
            'Close':   last_price,
            'Position': 0.0,
            'Note': 'Session close'
        })
        df.at[last_i, 'Position'] = 0.0
        df.at[last_i, 'Closed']   = 1

    trades_df = pd.DataFrame(trades, columns=['Datetime', 'Action', 'Close', 'Position', 'Note'])
    return df, trades_df
