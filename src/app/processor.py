"""
Processes stock data to compute multiple momentum indicators.
"""

import pandas as pd
import numpy as np
from app.logger import setup_logger

logger = setup_logger(__name__)


def compute_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Compute multiple momentum indicators on a stock DataFrame.

    Args:
        data (pd.DataFrame): Must contain 'Close', 'High', 'Low' prices.

    Returns:
        pd.DataFrame: The original DataFrame with new indicator columns.
    """
    try:
        data = data.copy()

        # Required columns
        if not all(col in data.columns for col in ["Close", "High", "Low"]):
            raise ValueError("Data must contain 'Close', 'High', and 'Low' columns.")

        # RSI
        delta = data["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        data["RSI"] = 100 - (100 / (1 + rs))

        # MACD
        ema_12 = data["Close"].ewm(span=12, adjust=False).mean()
        ema_26 = data["Close"].ewm(span=26, adjust=False).mean()
        data["MACD"] = ema_12 - ema_26
        data["MACD_Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()

        # Stochastic Oscillator
        low_14 = data["Low"].rolling(window=14).min()
        high_14 = data["High"].rolling(window=14).max()
        data["Stoch_%K"] = 100 * (data["Close"] - low_14) / (high_14 - low_14)
        data["Stoch_%D"] = data["Stoch_%K"].rolling(window=3).mean()

        # Rate of Change (ROC)
        data["ROC"] = data["Close"].pct_change(periods=12) * 100

        # Momentum
        data["Momentum"] = data["Close"] - data["Close"].shift(10)

        # Williams %R
        data["Williams_%R"] = -100 * (high_14 - data["Close"]) / (high_14 - low_14)

        # True Strength Index (TSI)
        price_change = data["Close"].diff()
        double_smoothed_pc = price_change.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
        double_smoothed_abs_pc = price_change.abs().ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
        data["TSI"] = 100 * (double_smoothed_pc / double_smoothed_abs_pc)

        # Awesome Oscillator (AO)
        median_price = (data["High"] + data["Low"]) / 2
        sma_5 = median_price.rolling(window=5).mean()
        sma_34 = median_price.rolling(window=34).mean()
        data["AO"] = sma_5 - sma_34

        # Commodity Channel Index (CCI)
        typical_price = (data["High"] + data["Low"] + data["Close"]) / 3
        sma_tp = typical_price.rolling(window=20).mean()
        mad = typical_price.rolling(window=20).apply(lambda x: np.mean(np.abs(x - x.mean())), raw=True)
        data["CCI"] = (typical_price - sma_tp) / (0.015 * mad)

        # Chande Momentum Oscillator (CMO)
        gain_cmo = delta.clip(lower=0).rolling(window=14).sum()
        loss_cmo = -delta.clip(upper=0).rolling(window=14).sum()
        data["CMO"] = 100 * (gain_cmo - loss_cmo) / (gain_cmo + loss_cmo)

        # Ultimate Oscillator (UO)
        bp = data["Close"] - data[["Low", "Close"].shift(1)].min(axis=1)
        tr = data[["High", "Close"].shift(1)].max(axis=1) - data[["Low", "Close"].shift(1)].min(axis=1)
        avg7 = bp.rolling(7).sum() / tr.rolling(7).sum()
        avg14 = bp.rolling(14).sum() / tr.rolling(14).sum()
        avg28 = bp.rolling(28).sum() / tr.rolling(28).sum()
        data["UO"] = 100 * (4 * avg7 + 2 * avg14 + avg28) / 7

        logger.info("Momentum indicators computed successfully.")
        return data

    except Exception as e:
        logger.error(f"Error computing momentum indicators: {e}")
        return pd.DataFrame()
