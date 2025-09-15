"""
===============================================================================
financialdata.py
-------------------------------------------------------------------------------
Single-file Streamlit app for interactive financial data analysis and visualization.
Features:
- Single and multi-stock analysis
- Interactive charts and metrics
- Rolling averages and volume display
- Portable single-file version
===============================================================================
"""
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timedelta
import plotly.express as px
def fetch_financial_data(ticker,start_date,end_date):
    """
    Fetch financial data for a given ticker symbol between start and end dates.
    """
    data = yf.download(ticker, start=start_date, end=end_date)
    return data


def _get_close_series(data):
    """Return a pandas Series representing the Close prices for the fetched data.
    Handles cases where the DataFrame has different column names or is a Series.
    Returns None if no suitable close series is found.
    """
    if data is None:
        return None
    # If data is already a Series, assume it represents Close prices
    if isinstance(data, pd.Series):
        return data.rename('Close')

    # If DataFrame has 'Close' column
    try:
        cols = data.columns
    except Exception:
        cols = []

    if isinstance(cols, pd.MultiIndex):
        # For single ticker, look for ('Close', ticker) or ('Close',)
        for col in cols:
            # If col is ('Close', ticker) or just 'Close'
            if (str(col[0]).lower() == 'close'):
                try:
                    return data[col]
                except Exception:
                    continue
        # fallback: flatten and try to find any level with 'Close'
        for col in cols:
            if 'Close' in [str(c) for c in col]:
                try:
                    return data[col]
                except Exception:
                    continue

    # If single-level columns
    if hasattr(data, 'columns') and 'Close' in data.columns:
        return data['Close']

    # Try common alternatives (case-insensitive)
    for alt in ['close', 'adj close', 'adj_close', 'adjclose']:
        for c in getattr(data, 'columns', []):
            if str(c).lower() == alt:
                return data[c]

    # As a last resort, if DataFrame has at least one numeric column, return the first numeric column
    try:
        numeric_cols = data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            return data[numeric_cols[0]]
    except Exception:
        pass

    return None
def rolling_average(data, window):
    """
    Calculate the rolling average for the given data and window size.
    """
    close = _get_close_series(data)
    if close is None:
        return pd.Series(dtype=float)
    return close.rolling(window=window).mean()

def plot_comparison_chart(data_dict, tickers):
    """
    Plot comparison chart for multiple stocks.
    """
    fig = go.Figure()

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']

    any_traces = False
    skipped = []
    for i, ticker in enumerate(tickers):
        if ticker not in data_dict:
            skipped.append(ticker)
            continue

        raw = data_dict[ticker]
        # Extract a safe Close series
        close_series = _get_close_series(raw)
        if close_series is None or len(close_series) == 0:
            skipped.append(ticker)
            continue

        # Normalize index and clean
        try:
            close_series.index = pd.to_datetime(close_series.index).tz_localize(None)
        except Exception:
            close_series.index = pd.to_datetime(close_series.index)
        close_series = close_series.sort_index().dropna()

        if len(close_series) < 2:
            skipped.append(ticker)
            continue

        start_price = float(close_series.iloc[0])
        if start_price == 0:
            skipped.append(ticker)
            continue

        normalized_prices = ((close_series / start_price) - 1) * 100
        x_vals = pd.to_datetime(normalized_prices.index).date

        fig.add_trace(go.Scatter(
            x=x_vals,
            y=normalized_prices.values,
            mode='lines',
            name=f'{ticker}',
            line=dict(color=colors[i % len(colors)], width=2),
            hovertemplate=f'<b>{ticker}</b><br><b>Date</b>: %{{x}}<br><b>Return</b>: %{{y:.2f}}%<extra></extra>'
        ))
        any_traces = True

    fig.update_layout(
        title={
            'text': f"📊 Stock Performance Comparison - Normalized Returns (%)",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#2E86AB'}
        },
        xaxis_title="📅 Date",
        yaxis_title="📈 Return (%)",
        hovermode='x unified',
        template='plotly_white',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=80, b=40, l=40, r=40),
        height=600
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray', type='date')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

    if not any_traces:
        st.warning("No valid data to plot for the selected tickers and date range.")
    elif skipped:
        st.warning(f"Skipped tickers (no Close data found): {', '.join(skipped)}")
    else:
        st.plotly_chart(fig, use_container_width=True)

def plot_financial_data(data, ticker):
    """
    Plot the financial data for a single ticker symbol with enhanced styling.
    Uses _get_close_series to safely extract prices and handles missing Volume.
    """
    close = _get_close_series(data)
    fig = go.Figure()

    if close is not None and len(close) >= 2:
        # Add Close Price trace
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(close.index).date,
            y=close.values,
            mode='lines',
            name='Close Price',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='<b>Date</b>: %{x}<br><b>Close</b>: $%{y:.2f}<extra></extra>'
        ))

        # Add 30-Day Moving Average trace
        rolling_avg = close.rolling(window=30).mean()
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(rolling_avg.index).date,
            y=rolling_avg.values,
            mode='lines',
            name='30-Day Moving Average',
            line=dict(color='#ff7f0e', width=2, dash='dash'),
            hovertemplate='<b>Date</b>: %{x}<br><b>30-Day MA</b>: $%{y:.2f}<extra></extra>'
        ))

        # Add Volume trace if available
        if isinstance(data, pd.DataFrame) and 'Volume' in data.columns:
            vol = data['Volume'].copy()
            vol.index = pd.to_datetime(vol.index).tz_localize(None)
            fig.add_trace(go.Bar(
                x=pd.to_datetime(vol.index).date,
                y=vol.values,
                name='Volume',
                yaxis='y2',
                opacity=0.3,
                marker_color='rgba(158,202,225,0.5)',
                hovertemplate='<b>Date</b>: %{x}<br><b>Volume</b>: %{y:,.0f}<extra></extra>'
            ))

        # Update layout for a full chart
        fig.update_layout(
            title={
                'text': f"📈 {ticker.upper()} Stock Analysis",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': '#2E86AB'}
            },
            xaxis_title="📅 Date",
            yaxis_title="💰 Price (USD)",
            yaxis2=dict(
                title="📊 Volume",
                overlaying='y',
                side='right',
                showgrid=False
            ),
            hovermode='x unified',
            template='plotly_white',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(t=80, b=40, l=40, r=40),
            height=600
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray', type='date')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')

    else:
        # Layout for when there is no data
        fig.update_layout(
            title=f"No valid price data to plot for {ticker}",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_white"
        )

    st.plotly_chart(fig, use_container_width=True)
def create_metrics_dashboard(data, ticker):
    """
    Create a metrics dashboard with key statistics.
    """
    if data is None or (hasattr(data, 'empty') and data.empty):
        return

    close_series = _get_close_series(data)
    if close_series is None or len(close_series) == 0:
        return

    # Calculate metrics
    current_price = float(close_series.iloc[-1])
    previous_price = float(close_series.iloc[-2]) if len(close_series) > 1 else current_price
    price_change = current_price - previous_price
    price_change_pct = (price_change / previous_price * 100) if previous_price != 0 else 0

    # Use safe accessors: only access DataFrame columns when data is a DataFrame
    if isinstance(data, pd.DataFrame) and 'High' in data.columns:
        try:
            high_52w = float(data['High'].max())
        except Exception:
            high_52w = float(close_series.max())
    else:
        high_52w = float(close_series.max())

    if isinstance(data, pd.DataFrame) and 'Low' in data.columns:
        try:
            low_52w = float(data['Low'].min())
        except Exception:
            low_52w = float(close_series.min())
    else:
        low_52w = float(close_series.min())

    if isinstance(data, pd.DataFrame) and 'Volume' in data.columns:
        try:
            avg_volume = float(data['Volume'].mean())
        except Exception:
            avg_volume = 0
    else:
        avg_volume = 0
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💵 Current Price",
            value=f"${current_price:.2f}",
            delta=f"{price_change_pct:+.2f}%"
        )
    
    with col2:
        st.metric(
            label="📈 52W High",
            value=f"${high_52w:.2f}"
        )
    
    with col3:
        st.metric(
            label="📉 52W Low",
            value=f"${low_52w:.2f}"
        )
    
    with col4:
        st.metric(
            label="📊 Avg Volume",
            value=f"{avg_volume:,.0f}"
        )

def create_comparison_metrics(data_dict, tickers):
    """
    Display comparison metrics for multiple stocks side by side.
    """
    cols = st.columns(len(tickers))
    for i, ticker in enumerate(tickers):
        data = data_dict.get(ticker)
        close_series = _get_close_series(data)
        if close_series is None or len(close_series) == 0:
            cols[i].warning(f"No price data for {ticker}.")
            continue
        current_price = float(close_series.iloc[-1])
        start_price = float(close_series.iloc[0])
        total_return = ((current_price / start_price) - 1) * 100 if start_price != 0 else 0
        high_price = float(data['High'].max()) if isinstance(data, pd.DataFrame) and 'High' in data.columns else None
        low_price = float(data['Low'].min()) if isinstance(data, pd.DataFrame) and 'Low' in data.columns else None
        avg_volume = float(data['Volume'].mean()) if isinstance(data, pd.DataFrame) and 'Volume' in data.columns else 0
        cols[i].metric(
            label=f"{ticker} Price",
            value=f"${current_price:.2f}",
            delta=f"{total_return:+.2f}%"
        )
        if high_price is not None:
            cols[i].write(f"High: ${high_price:.2f}")
        if low_price is not None:
            cols[i].write(f"Low: ${low_price:.2f}")
        cols[i].write(f"Avg Volume: {avg_volume:,.0f}")

def streamlit_app():
    """
    Enhanced Streamlit application to display financial data with modern UI.
    """
    # Page configuration
    st.set_page_config(
        page_title="Financial Data Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #6C757D;
        text-align: center;
        margin-bottom: 3rem;
    }
    .sidebar-content {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Main header
    st.markdown('<h1 class="main-header">📊 Financial Data Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Analyze stock performance with interactive charts and key metrics</p>', unsafe_allow_html=True)
    
    # Analysis mode selection
    analysis_mode = st.radio(
        "📊 **Analysis Mode:**",
        ["Single Stock Analysis", "Multi-Stock Comparison"],
        horizontal=True,
        help="Choose between analyzing one stock in detail or comparing multiple stocks"
    )
    
    # Sidebar for inputs
    st.sidebar.header("🔧 Configuration")
    
    # Popular stock suggestions
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
    
    # Stock selection
    st.sidebar.subheader("📈 Select Stock(s)")
    
    if analysis_mode == "Single Stock Analysis":
        # Option to choose from popular stocks or enter custom
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
    
    else:  # Multi-Stock Comparison
        st.sidebar.write("**Select multiple stocks to compare:**")
        
        # Multi-select for popular stocks
        selected_companies = st.sidebar.multiselect(
            "Popular stocks:",
            list(popular_stocks.keys()),
            default=["Apple Inc.", "Microsoft Corp.", "Google (Alphabet)"],
            help="Select multiple companies to compare"
        )
        popular_tickers = [popular_stocks[company] for company in selected_companies]
        
        # Additional custom tickers
        custom_tickers_input = st.sidebar.text_input(
            "Additional tickers (comma-separated):",
            placeholder="e.g., TSLA, NVDA, META",
            help="Enter additional ticker symbols separated by commas"
        )
        
        custom_tickers = []
        if custom_tickers_input:
            custom_tickers = [ticker.strip().upper() for ticker in custom_tickers_input.split(",") if ticker.strip()]
        
        tickers = popular_tickers + custom_tickers
        
        if tickers:
            st.sidebar.success(f"Comparing: {', '.join(tickers)}")
        else:
            st.sidebar.warning("Please select at least one stock to compare")
    
    # Date selection with presets
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
    else:  # Custom
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
    
    # Analysis options
    st.sidebar.subheader("⚙️ Analysis Options")
    show_volume = st.sidebar.checkbox("Show Volume", value=True)
    ma_window = st.sidebar.slider("Moving Average Days", 5, 100, 30)
    
    # Fetch and display data
    button_text = "🚀 Analyze Stock" if analysis_mode == "Single Stock Analysis" else "📊 Compare Stocks"
    
    if st.sidebar.button(button_text, type="primary"):
        if tickers:
            with st.spinner(f"Fetching data for {', '.join(tickers)}..."):
                try:
                    # Fetch data for all tickers
                    data_dict = {}
                    for ticker in tickers:
                        data = fetch_financial_data(ticker, start_date, end_date)
                        # store even empty results so we can show debug info
                        data_dict[ticker] = data
                    
                    if data_dict:
                        # Check which tickers are missing Close data
                        missing_raw = [t for t in tickers if (t not in data_dict) or data_dict.get(t) is None or (hasattr(data_dict.get(t),'empty') and data_dict.get(t).empty)]
                        missing_close = [t for t in tickers if t in data_dict and _get_close_series(data_dict[t]) is None]

                        if missing_raw:
                            st.warning(f"No raw data fetched for: {', '.join(missing_raw)}")
                        if missing_close:
                            st.warning(f"Fetched data missing Close prices for: {', '.join(missing_close)}")
                            # show a small preview for debugging
                            for t in missing_close:
                                st.caption(f"Preview of raw data for {t} (first 5 rows):")
                                try:
                                    st.dataframe(data_dict[t].head())
                                except Exception:
                                    st.write(repr(data_dict[t]))
                        if analysis_mode == "Single Stock Analysis":
                            # Single stock analysis (original functionality)
                            ticker = tickers[0]
                            data = data_dict[ticker]
                            
                            # Display metrics dashboard
                            st.subheader("📊 Key Metrics")
                            create_metrics_dashboard(data, ticker)
                            
                            st.divider()
                            
                            # Display chart
                            st.subheader("📈 Price Chart & Analysis")
                            plot_financial_data(data, ticker)
                            
                            # Additional insights
                            with st.expander("📋 Additional Insights"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write("**📈 Price Statistics:**")
                                    # Safely show high/low only if DataFrame has those columns
                                    if isinstance(data, pd.DataFrame) and 'High' in data.columns:
                                        try:
                                            st.write(f"• Highest Price: ${float(data['High'].max()):.2f}")
                                        except Exception:
                                            st.write("• Highest Price: N/A")
                                    else:
                                        st.write("• Highest Price: N/A")

                                    if isinstance(data, pd.DataFrame) and 'Low' in data.columns:
                                        try:
                                            st.write(f"• Lowest Price: ${float(data['Low'].min()):.2f}")
                                        except Exception:
                                            st.write("• Lowest Price: N/A")
                                    else:
                                        st.write("• Lowest Price: N/A")

                                    close_series = _get_close_series(data)
                                    if close_series is not None and len(close_series) > 0:
                                        try:
                                            st.write(f"• Average Price: ${float(close_series.mean()):.2f}")
                                            st.write(f"• Price Volatility: {float(close_series.std()):.2f}")
                                        except Exception:
                                            st.write("• Average Price: N/A")
                                            st.write("• Price Volatility: N/A")
                                    else:
                                        st.write("• Average Price: N/A")
                                        st.write("• Price Volatility: N/A")
                                
                                with col2:
                                    st.write("**📊 Trading Statistics:**")
                                    if isinstance(data, pd.DataFrame) and 'Volume' in data.columns:
                                        try:
                                            st.write(f"• Total Volume: {int(data['Volume'].sum()):,}")
                                            st.write(f"• Average Daily Volume: {float(data['Volume'].mean()):,.0f}")
                                            st.write(f"• Highest Volume Day: {int(data['Volume'].max()):,}")
                                        except Exception:
                                            st.write("• Total Volume: N/A")
                                            st.write("• Average Daily Volume: N/A")
                                            st.write("• Highest Volume Day: N/A")
                                    else:
                                        st.write("• Total Volume: N/A")
                                        st.write("• Average Daily Volume: N/A")
                                        st.write("• Highest Volume Day: N/A")

                                    st.write(f"• Trading Days: {len(data)}")
                            
                            # Download option
                            csv = data.to_csv()
                            st.download_button(
                                label="📥 Download Data as CSV",
                                data=csv,
                                file_name=f"{ticker}_stock_data.csv",
                                mime="text/csv"
                            )
                        else:
                            # Multi-stock comparison
                            st.subheader("📊 Stock Comparison Metrics")
                            create_comparison_metrics(data_dict, list(data_dict.keys()))
                            
                            st.divider()
                            
                            # Display comparison chart
                            st.subheader("📈 Performance Comparison")
                            plot_comparison_chart(data_dict, list(data_dict.keys()))
                            
                            # Individual stock details in tabs
                            st.subheader("📋 Individual Stock Details")
                            tabs = st.tabs([f"📈 {ticker}" for ticker in data_dict.keys()])
                            
                            for i, (ticker, data) in enumerate(data_dict.items()):
                                with tabs[i]:
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        close_series = _get_close_series(data)
                                        if close_series is None or len(close_series) == 0:
                                            st.warning(f"No price data for {ticker}.")
                                        else:
                                            current_price = float(close_series.iloc[-1])
                                            start_price = float(close_series.iloc[0])
                                            total_return = ((current_price / start_price) - 1) * 100
                                            
                                            st.metric(
                                                label=f"{ticker} Current Price",
                                                value=f"${current_price:.2f}",
                                                delta=f"{total_return:+.2f}% total return"
                                            )
                                    
                                    with col2:
                                        # Safe extraction for tab display
                                        if isinstance(data, pd.DataFrame) and 'High' in data.columns:
                                            try:
                                                high_price = float(data['High'].max())
                                            except Exception:
                                                high_price = None
                                        else:
                                            high_price = None

                                        if isinstance(data, pd.DataFrame) and 'Low' in data.columns:
                                            try:
                                                low_price = float(data['Low'].min())
                                            except Exception:
                                                low_price = None
                                        else:
                                            low_price = None

                                        if isinstance(data, pd.DataFrame) and 'Volume' in data.columns:
                                            try:
                                                avg_volume = float(data['Volume'].mean())
                                            except Exception:
                                                avg_volume = 0
                                        else:
                                            avg_volume = 0
                                        
                                        st.write("**Key Stats:**")
                                        if high_price is not None:
                                            st.write(f"• High: ${high_price:.2f}")
                                        else:
                                            st.write("• High: N/A")
                                        if low_price is not None:
                                            st.write(f"• Low: ${low_price:.2f}")
                                        else:
                                            st.write("• Low: N/A")
                                        st.write(f"• Avg Volume: {avg_volume:,.0f}")
                            
                            # Download comparison data
                            comparison_data = pd.DataFrame()
                            for ticker, data in data_dict.items():
                                close_series = _get_close_series(data)
                                if close_series is not None:
                                    # align by date
                                    try:
                                        comparison_data = comparison_data.join(close_series.rename(f"{ticker}_Close"), how='outer') if not comparison_data.empty else close_series.rename(f"{ticker}_Close").to_frame()
                                    except Exception:
                                        # fallback: convert to DataFrame
                                        comparison_data = comparison_data.join(pd.DataFrame(close_series.rename(f"{ticker}_Close")), how='outer') if not comparison_data.empty else pd.DataFrame(close_series.rename(f"{ticker}_Close"))
                                if isinstance(data, pd.DataFrame) and 'Volume' in data.columns:
                                    try:
                                        vol = data['Volume'].rename(f"{ticker}_Volume")
                                        comparison_data = comparison_data.join(vol, how='outer')
                                    except Exception:
                                        pass
                            
                            csv = comparison_data.to_csv()
                            st.download_button(
                                label="📥 Download Comparison Data as CSV",
                                data=csv,
                                file_name=f"stock_comparison_{'_'.join(data_dict.keys())}.csv",
                                mime="text/csv"
                            )
                        
                    else:
                        failed_tickers = [t for t in tickers if t not in data_dict]
                        st.error(f"❌ No data found for: {', '.join(failed_tickers)}. Please check the ticker symbols and try again.")
                        
                except Exception as e:
                    import traceback
                    tb = traceback.format_exc()
                    st.error(f"❌ Error fetching data: {str(e)}")
                    with st.expander("Show error details"):
                        st.code(tb)
        else:
            st.warning("⚠️ Please select at least one stock to analyze.")
    
    # Footer
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
    streamlit_app()
    

