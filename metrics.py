"""
===============================================================================
metrics.py
-------------------------------------------------------------------------------
Analytics/statistics functions for Financial Data Dashboard.
Contains functions for calculating and displaying key metrics and statistics
for single and multiple stocks.
===============================================================================
"""

import pandas as pd
import streamlit as st
from data import _get_close_series

# --- Multi-Stock Comparison Metrics ---
def create_comparison_metrics(data_dict, tickers):
    """
    Create and display comparison metrics for multiple stocks.
    Shows current price, total return, volatility, and average volume.
    """
    metrics_data = []
    for ticker in tickers:
        if ticker in data_dict and not data_dict[ticker].empty:
            data = data_dict[ticker]
            close_series = _get_close_series(data)
            if close_series is None:
                continue
            current_price = float(close_series.iloc[-1])
            start_price = float(close_series.iloc[0])
            total_return = ((current_price / start_price) - 1) * 100
            volatility = float(close_series.pct_change().std() * 100)
            if isinstance(data, pd.DataFrame) and 'Volume' in data.columns:
                try:
                    avg_volume = float(data['Volume'].mean())
                except Exception:
                    avg_volume = 0
            else:
                avg_volume = 0
            metrics_data.append({
                'Ticker': ticker,
                'Current Price': f"${current_price:.2f}",
                'Total Return': f"{total_return:.2f}%",
                'Volatility': f"{volatility:.2f}%",
                'Avg Volume': f"{avg_volume:,.0f}"
            })
    if metrics_data:
        st.dataframe(pd.DataFrame(metrics_data))
    else:
        st.info("No valid data to compare.")

# --- Single Stock Metrics Dashboard ---
def create_metrics_dashboard(data, ticker):
    """
    Create and display key metrics for a single stock.
    Shows current price, total return, volatility, and average volume.
    """
    close_series = _get_close_series(data)
    if close_series is None or len(close_series) < 2:
        st.info("Not enough data for metrics.")
        return
    current_price = float(close_series.iloc[-1])
    start_price = float(close_series.iloc[0])
    total_return = ((current_price / start_price) - 1) * 100
    volatility = float(close_series.pct_change().std() * 100)
    if isinstance(data, pd.DataFrame) and 'Volume' in data.columns:
        try:
            avg_volume = float(data['Volume'].mean())
        except Exception:
            avg_volume = 0
    else:
        avg_volume = 0
    st.metric(label=f"{ticker} Current Price", value=f"${current_price:.2f}")
    st.metric(label="Total Return", value=f"{total_return:.2f}%")
    st.metric(label="Volatility", value=f"{volatility:.2f}%")
    st.metric(label="Average Volume", value=f"{avg_volume:,.0f}")
