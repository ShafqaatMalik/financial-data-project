import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
def fetch_financial_data(ticker,start_date,end_date):
    """
    Fetch financial data for a given ticker symbol between start and end dates.
    """
    data = yf.download(ticker, start=start_date, end=end_date)
    return data
def rolling_average(data, window):
    """
    Calculate the rolling average for the given data and window size.
    """
    data = data['Close'].rolling(window=window).mean()
    return data

def plot_financial_data(data, ticker):
    """
    Plot the financial data for a given ticker symbol.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close'))
    fig.add_trace(go.Scatter(x=data.index, y=rolling_average(data, 30), mode='lines', name='30-Day Rolling Average'))
    fig.update_layout(title=f"Financial Data for {ticker}", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig)
def streamlit_app():
    """
    Streamlit application to display financial data.
    """
    st.title("Financial Data Viewer")
    
    ticker = st.text_input("Enter Ticker Symbol (e.g., AAPL, MSFT):", "AAPL")
    start_date = st.date_input("Start Date", pd.to_datetime("2020-01-01"))
    end_date = st.date_input("End Date", pd.to_datetime("2023-01-01"))
    
    if st.button("Fetch Data"):
        data = fetch_financial_data(ticker, start_date, end_date)
        data = rolling_average(data, 30)        
        if not data.empty:
            plot_financial_data(data, ticker)
        else:
            st.error("No data found for the given ticker and date range.")
    

