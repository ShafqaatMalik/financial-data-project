"""
===============================================================================
data.py
-------------------------------------------------------------------------------
Data fetching and cleaning helpers for Financial Data Dashboard.
Contains functions for downloading financial data, extracting price series,
and calculating rolling averages.
===============================================================================
"""

import pandas as pd
import yfinance as yf

# --- Data Fetching ---
def fetch_financial_data(ticker, start_date, end_date):
    """
    Fetch financial data for a given ticker symbol between start and end dates.
    Returns a pandas DataFrame.
    """
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

# --- Close Series Extraction ---
def _get_close_series(data):
    """
    Extract the Close price series from a DataFrame or Series.
    Handles MultiIndex columns and common alternatives.
    Returns None if not found.
    """
    if data is None:
        return None
    if isinstance(data, pd.Series):
        return data.rename('Close')
    try:
        cols = data.columns
    except Exception:
        cols = []
    if isinstance(cols, pd.MultiIndex):
        for col in cols:
            if any(str(level).lower() in ('close', 'adj close', 'adj_close', 'adjclose') for level in col):
                try:
                    return data[col]
                except Exception:
                    continue
    for col in cols:
        if str(col).lower() in ('close', 'adj close', 'adj_close', 'adjclose'):
            try:
                return data[col]
            except Exception:
                continue
    return None

# --- Rolling Average ---
def rolling_average(data, window=30):
    """
    Calculate rolling average for Close price series.
    Returns a pandas Series.
    """
    close = _get_close_series(data)
    if close is None:
        return pd.Series([float('nan')] * len(data))
    return close.rolling(window=window).mean()
