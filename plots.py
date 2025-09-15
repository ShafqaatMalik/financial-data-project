"""
===============================================================================
plots.py
-------------------------------------------------------------------------------
Charting functions for Financial Data Dashboard.
Contains functions for rendering interactive price and comparison charts
using Plotly and Streamlit.
===============================================================================
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from data import _get_close_series, rolling_average

# --- Single Stock Price Chart ---
def plot_financial_data(data, ticker):
    """
    Plot the financial data for a single ticker symbol with enhanced styling.
    Shows Close price, moving average, and volume (if available).
    """
    close = _get_close_series(data)
    if close is None or len(close) < 2:
        st.warning(f"Not enough price data to plot {ticker}.")
        return
    rolling_avg = close.rolling(window=30).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(close.index).date,
        y=close.values,
        mode='lines',
        name='Close Price',
        line=dict(color='#1f77b4', width=2),
        hovertemplate='<b>Date</b>: %{x}<br><b>Close</b>: $%{y:.2f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(rolling_avg.index).date,
        y=rolling_avg.values,
        mode='lines',
        name='30-Day Moving Average',
        line=dict(color='#ff7f0e', width=2, dash='dash'),
        hovertemplate='<b>Date</b>: %{x}<br><b>30-Day MA</b>: $%{y:.2f}<extra></extra>'
    ))
    if isinstance(data, pd.DataFrame) and 'Volume' in data.columns:
        fig.add_trace(go.Bar(
            x=pd.to_datetime(data.index).date,
            y=data['Volume'],
            name='Volume',
            marker_color='rgba(204,204,204,0.5)',
            yaxis='y2',
            opacity=0.3
        ))
        fig.update_layout(
            yaxis2=dict(
                title='Volume',
                overlaying='y',
                side='right',
                showgrid=False
            )
        )
    fig.update_layout(
        title=f"{ticker} Price Chart",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Multi-Stock Comparison Chart ---
def plot_comparison_chart(data_dict, tickers):
    """
    Plot comparison chart for multiple tickers.
    Shows normalized price performance for each stock.
    """
    fig = go.Figure()
    for ticker in tickers:
        data = data_dict.get(ticker)
        close = _get_close_series(data)
        if close is None or len(close) < 2:
            continue
        norm_close = close / close.iloc[0] * 100
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(close.index).date,
            y=norm_close.values,
            mode='lines',
            name=ticker,
            line=dict(width=2),
            hovertemplate=f'<b>{ticker}</b><br>Date: %{{x}}<br>Performance: %{{y:.2f}}%<extra></extra>'
        ))
    fig.update_layout(
        title="Stock Performance Comparison (Normalized)",
        xaxis_title="Date",
        yaxis_title="Performance (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)
