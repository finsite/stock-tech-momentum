"""Processes stock data to compute multiple momentum indicators."""

from typing import Any

import numpy as np
import pandas as pd

from app.logger import setup_logger

logger = setup_logger(__name__)


def compute_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """Compute multiple momentum indicators on a stock DataFrame.
    
    Args:
    ----
      data(pd.DataFrame): Must contain 'Close', 'High', 'Low' prices.
      data: pd.DataFrame:
      data: pd.DataFrame:

    :param data: pd.DataFrame:
    :param data: pd.DataFrame:
    :param data: pd.DataFrame:
    :param data: type data: pd.DataFrame :
    :param data: type data: pd.DataFrame :
    :param data: pd.DataFrame:
    :param data: pd.DataFrame:
    :param data: pd.DataFrame: 

    """
    try:
        data = data.copy()

        if not all(col in data.columns for col in ["Close", "High", "Low"]):
            raise ValueError("Data must contain 'Close', 'High', and 'Low' columns.")

        # RSI (Relative Strength Index)
        delta = data["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        data["RSI"] = 100 - (100 / (1 + rs))

        # MACD (Moving Average Convergence Divergence)
        ema_12 = data["Close"].ewm(span=12, adjust=False).mean()
        ema_26 = data["Close"].ewm(span=26, adjust=False).mean()
        data["MACD"] = ema_12 - ema_26
        data["MACD_Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()

        # Stochastic Oscillator
        low_14 = data["Low"].rolling(window=14).min()
        high_14 = data["High"].rolling(window=14).max()
        data["Stoch_%K"] = 100 * (data["Close"] - low_14) / (high_14 - low_14)
        data["Stoch_%D"] = data["Stoch_%K"].rolling(window=3).mean()

        # ROC (Rate of Change)
        data["ROC"] = data["Close"].pct_change(periods=12) * 100

        # Momentum
        data["Momentum"] = data["Close"] - data["Close"].shift(10)

        # Williams %R
        data["Williams_%R"] = -100 * (high_14 - data["Close"]) / (high_14 - low_14)

        # TSI (True Strength Index)
        price_change = data["Close"].diff()
        double_smoothed_pc = (
            price_change.ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
        )
        double_smoothed_abs_pc = (
            price_change.abs().ewm(span=25, adjust=False).mean().ewm(span=13, adjust=False).mean()
        )
        data["TSI"] = 100 * (double_smoothed_pc / double_smoothed_abs_pc)

        # AO (Awesome Oscillator)
        median_price = (data["High"] + data["Low"]) / 2
        sma_5 = median_price.rolling(window=5).mean()
        sma_34 = median_price.rolling(window=34).mean()
        data["AO"] = sma_5 - sma_34

        # CCI (Commodity Channel Index)
        typical_price = (data["High"] + data["Low"] + data["Close"]) / 3
        sma_tp = typical_price.rolling(window=20).mean()
        mad = typical_price.rolling(window=20).apply(
            lambda x: np.mean(np.abs(x - x.mean())), raw=True
        )
        data["CCI"] = (typical_price - sma_tp) / (0.015 * mad)

        # CMO (Chande Momentum Oscillator)
        gain_cmo = delta.clip(lower=0).rolling(window=14).sum()
        loss_cmo = -delta.clip(upper=0).rolling(window=14).sum()
        data["CMO"] = 100 * (gain_cmo - loss_cmo) / (gain_cmo + loss_cmo)

        # UO (Ultimate Oscillator)
        prev_close = data["Close"].shift(1)
        bp = data["Close"] - pd.concat([data["Low"], prev_close], axis=1).min(axis=1)
        tr = pd.concat([data["High"], prev_close], axis=1).max(axis=1) - pd.concat(
            [data["Low"], prev_close], axis=1
        ).min(axis=1)
        avg7 = bp.rolling(7).sum() / tr.rolling(7).sum()
        avg14 = bp.rolling(14).sum() / tr.rolling(14).sum()
        avg28 = bp.rolling(28).sum() / tr.rolling(28).sum()
        data["UO"] = 100 * (4 * avg7 + 2 * avg14 + avg28) / 7

        logger.info("All momentum indicators computed successfully.")
        return data

    except Exception as e:
        logger.error(f"Error computing momentum indicators: {e}")
        return pd.DataFrame()


def analyze_momentum(data: pd.DataFrame) -> dict[str, Any]:
    """Analyze stock data using momentum indicators and return a structured
    result.
    
    Args:
    ----
      data(pd.DataFrame): The input data containing stock OHLC values.
      data: pd.DataFrame:
      data: pd.DataFrame:

    :param data: pd.DataFrame:
    :param data: pd.DataFrame:
    :param data: pd.DataFrame:
    :param data: type data: pd.DataFrame :
    :param data: type data: pd.DataFrame :
    :param data: pd.DataFrame:
    :param data: pd.DataFrame:
    :param data: pd.DataFrame: 

    """
    df = compute_indicators(data)
    if df.empty:
        return {}

    latest = df.iloc[-1]
    return {
        "RSI": latest.get("RSI"),
        "MACD": latest.get("MACD"),
        "MACD_Signal": latest.get("MACD_Signal"),
        "Stoch_%K": latest.get("Stoch_%K"),
        "Stoch_%D": latest.get("Stoch_%D"),
        "ROC": latest.get("ROC"),
        "Momentum": latest.get("Momentum"),
        "Williams_%R": latest.get("Williams_%R"),
        "TSI": latest.get("TSI"),
        "AO": latest.get("AO"),
        "CCI": latest.get("CCI"),
        "CMO": latest.get("CMO"),
        "UO": latest.get("UO"),
    }
