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
    """Plot financial data using Plotly.
    """   
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))
    fig.update_layout(title=f'Financial Data for {ticker}', xaxis_title='Date', yaxis_title='Price')
    st.plotly_chart(fig)
def main():
    """Main function to run the Streamlit app.
    """
    st.title("Financial Data Viewer")
    ticker = st.text_input("Enter Ticker Symbol", "AAPL")
    start_date = st.date_input("Start Date", pd.to_datetime("2020-01-01"))
    end_date = st.date_input("End Date", pd.to_datetime("2023-01-01"))
    
    if st.button("Fetch Data"):
        data = fetch_financial_data(ticker, start_date, end_date)
        if not data.empty:
            st.write(data)
            plot_financial_data(data, ticker)
            window = st.slider("Rolling Average Window Size", 1, 30, 5)
            rolling_avg = rolling_average(data, window)
            st.line_chart(rolling_avg)
        else:
            st.error("No data found for the given ticker and date range.")
if __name__ == "__main__":
    main()  




