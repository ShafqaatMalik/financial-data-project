import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st

# --- Page Configuration ---
st.set_page_config(
    page_title="Advanced Financial Data Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- Data Fetching Function ---
def fetch_financial_data(tickers, start_date, end_date):
    """
    Fetch financial data for given ticker symbols between start and end dates.
    """
    # yfinance expects a space-separated string for multiple tickers
    ticker_string = " ".join(tickers)
    data = yf.download(ticker_string, start=start_date, end=end_date)
    return data

# --- Plotting Function ---
def plot_financial_data(data, tickers, rolling_window):
    """
    Plot the financial data for given ticker symbols.
    """
    fig = go.Figure()

    # If only one ticker is selected, data structure is a simple DataFrame
    if len(tickers) == 1:
        ticker = tickers[0]
        # Plot Closing Price
        fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name=f'{ticker} Close'))
        # Plot Rolling Average
        rolling_avg = data['Close'].rolling(window=rolling_window).mean()
        fig.add_trace(go.Scatter(x=data.index, y=rolling_avg, mode='lines', name=f'{ticker} {rolling_window}-Day Avg', line=dict(dash='dash', color='yellow')))
    
    # If multiple tickers, data has multi-level columns
    else:
        for ticker in tickers:
            # Plot Closing Price for each ticker
            fig.add_trace(go.Scatter(x=data.index, y=data['Close'][ticker], mode='lines', name=f'{ticker} Close'))
            # Plot Rolling Average for each ticker
            rolling_avg = data['Close'][ticker].rolling(window=rolling_window).mean()
            fig.add_trace(go.Scatter(x=data.index, y=rolling_avg, mode='lines', name=f'{ticker} {rolling_window}-Day Avg', line=dict(dash='dash')))
    
    fig.update_layout(
        title="Stock Closing Prices and Rolling Averages",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        legend_title="Legend",
        template="plotly_dark", # Use a dark theme for a modern look
        xaxis_rangeslider_visible=True # Add a rangeslider for better navigation
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Streamlit App UI ---
st.title("📈 Advanced Financial Data Dashboard")

with st.expander("ℹ️ How to Use"):
    st.write("""
        1.  **Select Analysis Type**: Choose to analyze a single stock or compare multiple stocks.
        2.  **Select Ticker(s)**: Pick a stock from the dropdown. For multi-stock, you can select several.
        3.  **Select Date Range**: Choose a preset period (like 1M, 6M, YTD) or select 'Custom' to use the date pickers.
        4.  **Adjust Rolling Average**: Use the slider to change the moving average window.
        5.  Click **'Get Data'** to see the results.
    """)

# --- Sidebar for User Inputs ---
st.sidebar.header("Dashboard Controls")
# show screenshot in sidebar
try:
    st.sidebar.image("assets/app-screenshot.png", use_column_width=True)
except Exception:
    # ignore if asset missing or load fails
    pass

# 1. Analysis Type Selection
analysis_type = st.sidebar.radio(
    "Select Analysis Type",
    ("Single Stock Analysis", "Multi-Stock Comparison"),
    key="analysis_type"
)

# Pre-defined list of popular tickers
ticker_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "JPM", "V"]

# 2. Ticker Symbol Selection (conditional on analysis type)
tickers = []
if analysis_type == "Single Stock Analysis":
    ticker_input = st.sidebar.selectbox("Select Ticker Symbol", ticker_list)
    if ticker_input:
        tickers = [ticker_input]
else:
    tickers = st.sidebar.multiselect(
        "Select Ticker Symbols for Comparison",
        ticker_list,
        default=["AAPL", "MSFT"]
    )

# 3. Date Range Selection
date_preset = st.sidebar.selectbox(
    "Select Date Range",
    ("1M", "3M", "6M", "YTD", "1Y", "5Y", "Custom"),
    index=4 # Default to '1Y'
)

# Calculate start and end dates based on preset
end_date = pd.Timestamp.today()
if date_preset != "Custom":
    if date_preset == "1M":
        start_date = end_date - pd.DateOffset(months=1)
    elif date_preset == "3M":
        start_date = end_date - pd.DateOffset(months=3)
    elif date_preset == "6M":
        start_date = end_date - pd.DateOffset(months=6)
    elif date_preset == "YTD":
        start_date = pd.Timestamp(year=end_date.year, month=1, day=1)
    elif date_preset == "1Y":
        start_date = end_date - pd.DateOffset(years=1)
    elif date_preset == "5Y":
        start_date = end_date - pd.DateOffset(years=5)
else:
    # Show custom date inputs only if 'Custom' is selected
    start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
    end_date = st.sidebar.date_input("End Date", pd.Timestamp.today())

# 4. Rolling Average Slider
rolling_window = st.sidebar.slider("Rolling Average Window (Days)", min_value=10, max_value=200, value=30, step=10)

# --- Main Logic to Fetch and Plot ---
if st.sidebar.button("Get Data 📊"):
    if not tickers:
        st.warning("Please select at least one ticker symbol.")
    elif start_date >= end_date:
        st.error("Error: End date must be after start date.")
    else:
        with st.spinner(f"Fetching data for {', '.join(tickers)}..."):
            data = fetch_financial_data(tickers, start_date, end_date)
            
            if data.empty or data['Close'].isnull().all().any():
                 st.error("No data found for the given tickers and date range. Please try different inputs.")
            else:
                st.success("Data fetched successfully!")
                plot_financial_data(data, tickers, rolling_window)