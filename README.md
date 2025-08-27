# Financial Data Project
## Overview

This code is a Streamlit application that fetches and displays financial data for a given ticker symbol. It uses the yfinance library to download stock data and Plotly for visualization. The user can input a ticker symbol, start date, and end date to fetch the data. It also allows the user to calculate and visualize a rolling average of the closing prices. The application is interactive and provides a user-friendly interface for financial data analysis.

## How to Run


### Installation and Running

1. **Clone or download this repository** to your local machine.

2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit application:**
   ```bash
   streamlit run financialdata.py
   ```

4. **Access the application:**
   - The application will automatically open in your default web browser
   - If it doesn't open automatically, navigate to `http://localhost:8501`


```

### Usage
1. Enter a stock ticker symbol (e.g., AAPL, MSFT, GOOGL)
2. Select start and end dates for the data range
3. Click "Fetch Data" to display the stock price chart with rolling average

### Dependencies
- `streamlit` - Web application framework
- `yfinance` - Yahoo Finance data downloader
- `pandas` - Data manipulation and analysis
- `plotly` - Interactive plotting library
    