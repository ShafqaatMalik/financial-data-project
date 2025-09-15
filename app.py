"""
===============================================================================
app.py
-------------------------------------------------------------------------------
Main application file for interactive financial data analysis and visualization.
Features:
- Single and multi-stock analysis
- Interactive charts and metrics
- Professional UI with Streamlit
- Modularized for maintainability
===============================================================================
"""

import streamlit as st
from datetime import datetime, timedelta
from data import fetch_financial_data
from plots import plot_financial_data, plot_comparison_chart
from metrics import create_metrics_dashboard, create_comparison_metrics
import pandas as pd

def streamlit_app():
    """
    Main function to launch the Streamlit financial data dashboard.
    Handles UI layout, user input, data fetching, and visualization.
    """
    # =====================
    # Streamlit Page Config
    # =====================
    st.set_page_config(
        page_title="Financial Data Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown('<h1 class="main-header">📊 Financial Data Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Analyze stock performance with interactive charts and key metrics</p>', unsafe_allow_html=True)

    # =====================
    # Analysis Mode Selection
    # =====================
    analysis_mode = st.radio(
        "📊 **Analysis Mode:**",
        ["Single Stock Analysis", "Multi-Stock Comparison"],
        horizontal=True,
        help="Choose between analyzing one stock in detail or comparing multiple stocks"
    )

    # =====================
    # Sidebar: Stock Selection
    # =====================
    st.sidebar.header("🔧 Configuration")
    popular_stocks = {
        "Apple Inc.": "AAPL",
        "Microsoft Corp.": "MSFT", 
        "Google (Alphabet)": "GOOGL",
        "Amazon": "AMZN",
        "Tesla": "TSLA",
        "NVIDIA": "NVDA",
        "Meta (Facebook)": "META",
        "Netflix": "NFLX"
    }
    st.sidebar.subheader("📈 Select Stock(s)")
    if analysis_mode == "Single Stock Analysis":
        # --- Single Stock Selection ---
        selection_method = st.sidebar.radio(
            "Choose method:",
            ["Popular Stocks", "Custom Ticker"]
        )
        if selection_method == "Popular Stocks":
            selected_company = st.sidebar.selectbox(
                "Select a company:",
                list(popular_stocks.keys())
            )
            ticker = popular_stocks[selected_company]
            st.sidebar.info(f"Selected: {ticker}")
            tickers = [ticker]
        else:
            ticker = st.sidebar.text_input(
                "Enter Ticker Symbol:",
                value="AAPL",
                help="Enter stock symbol (e.g., AAPL, MSFT, GOOGL)"
            ).upper()
            tickers = [ticker] if ticker else []
    else:
        # --- Multi-Stock Selection ---
        st.sidebar.write("**Select multiple stocks to compare:**")
        selected_companies = st.sidebar.multiselect(
            "Popular stocks:",
            list(popular_stocks.keys()),
            default=["Apple Inc.", "Microsoft Corp.", "Google (Alphabet)"],
            help="Select multiple companies to compare"
        )
        popular_tickers = [popular_stocks[company] for company in selected_companies]
        custom_tickers_input = st.sidebar.text_input(
            "Additional tickers (comma-separated):",
            placeholder="e.g., TSLA, NVDA, META",
            help="Enter additional ticker symbols separated by commas"
        )
        custom_tickers = []
        if custom_tickers_input:
            # Parse custom tickers from input
            custom_tickers = [ticker.strip().upper() for ticker in custom_tickers_input.split(",") if ticker.strip()]
        tickers = popular_tickers + custom_tickers
        if tickers:
            st.sidebar.success(f"Comparing: {', '.join(tickers)}")
        else:
            st.sidebar.warning("Please select at least one stock to compare")

    # =====================
    # Sidebar: Date Range Selection
    # =====================
    st.sidebar.subheader("📅 Date Range")
    date_preset = st.sidebar.selectbox(
        "Quick select:",
        ["Custom", "Last 1 Month", "Last 3 Months", "Last 6 Months", "Last 1 Year", "Last 2 Years"]
    )
    today = datetime.now().date()
    if date_preset == "Last 1 Month":
        start_date = today - timedelta(days=30)
        end_date = today
    elif date_preset == "Last 3 Months":
        start_date = today - timedelta(days=90)
        end_date = today
    elif date_preset == "Last 6 Months":
        start_date = today - timedelta(days=180)
        end_date = today
    elif date_preset == "Last 1 Year":
        start_date = today - timedelta(days=365)
        end_date = today
    elif date_preset == "Last 2 Years":
        start_date = today - timedelta(days=730)
        end_date = today
    else:
        # Custom date selection
        start_date = st.sidebar.date_input(
            "Start Date", 
            value=datetime(2023, 1, 1).date(),
            max_value=today
        )
        end_date = st.sidebar.date_input(
            "End Date", 
            value=today,
            max_value=today
        )

    # =====================
    # Sidebar: Analysis Options
    # =====================
    st.sidebar.subheader("⚙️ Analysis Options")
    show_volume = st.sidebar.checkbox("Show Volume", value=True)
    ma_window = st.sidebar.slider("Moving Average Days", 5, 100, 30)
    button_text = "🚀 Analyze Stock" if analysis_mode == "Single Stock Analysis" else "📊 Compare Stocks"

    # =====================
    # Main Analysis Trigger
    # =====================
    if st.sidebar.button(button_text, type="primary"):
        if tickers:
            with st.spinner(f"Fetching data for {', '.join(tickers)}..."):
                try:
                    # --- Fetch data for each ticker ---
                    data_dict = {}
                    for ticker in tickers:
                        data = fetch_financial_data(ticker, start_date, end_date)
                        data_dict[ticker] = data
                    if data_dict:
                        # --- Check for missing or empty data ---
                        missing_raw = [t for t in tickers if (t not in data_dict) or data_dict.get(t) is None or (hasattr(data_dict.get(t),'empty') and data_dict.get(t).empty)]
                        missing_close = [t for t in tickers if t in data_dict and data_dict[t] is not None and hasattr(data_dict[t],'empty') and data_dict[t].empty]
                        if missing_raw:
                            st.warning(f"No raw data fetched for: {', '.join(missing_raw)}")
                        if missing_close:
                            st.warning(f"Fetched data missing Close prices for: {', '.join(missing_close)}")
                            for t in missing_close:
                                st.caption(f"Preview of raw data for {t} (first 5 rows):")
                                try:
                                    st.dataframe(data_dict[t].head())
                                except Exception:
                                    st.write(repr(data_dict[t]))
                        # --- Render analysis and charts ---
                        if analysis_mode == "Single Stock Analysis":
                            ticker = tickers[0]
                            data = data_dict[ticker]
                            st.subheader("📊 Key Metrics")
                            create_metrics_dashboard(data, ticker)
                            st.divider()
                            st.subheader("📈 Price Chart & Analysis")
                            plot_financial_data(data, ticker)
                        else:
                            st.subheader("📊 Stock Comparison Metrics")
                            create_comparison_metrics(data_dict, list(data_dict.keys()))
                            st.divider()
                            st.subheader("📈 Performance Comparison")
                            plot_comparison_chart(data_dict, list(data_dict.keys()))
                    else:
                        # --- No data found for tickers ---
                        failed_tickers = [t for t in tickers if t not in data_dict]
                        st.error(f"❌ No data found for: {', '.join(failed_tickers)}. Please check the ticker symbols and try again.")
                except Exception as e:
                    # --- Error handling and traceback display ---
                    import traceback
                    tb = traceback.format_exc()
                    st.error(f"❌ Error fetching data: {str(e)}")
                    with st.expander("Show error details"):
                        st.code(tb)
        else:
            st.warning("⚠️ Please select at least one stock to analyze.")

    # =====================
    # Footer & Attribution
    # =====================
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #6C757D; font-size: 0.9rem;'>
        💡 Built with Streamlit & yfinance | Data provided by Yahoo Finance
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    # Entry point for running the Streamlit app
    streamlit_app()
