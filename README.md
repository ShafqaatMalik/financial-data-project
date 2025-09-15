# Financial Data Dashboard
This code is a Streamlit application that fetches and displays financial data for a given ticker symbol. It uses the yfinance library to download stock data and Plotly for visualization. The user can input a ticker symbol, data range and a rolling average to fetch the data. It also allows the user to calculate and visualize a rolling average of the closing prices. The application is interactive and provides a user-friendly interface for financial data analysis. 

## Features
- Single and multi-stock analysis
- Interactive charts and metrics
- Rolling averages and volume display
- Modular codebase for maintainability
- Unit tests for data helpers

## Quick Start
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the app:**
   ```bash
   streamlit run app.py
   ```
3. **Run unit tests:**
   ```bash
   python test_data.py
   ```

## File Structure
```
├── app.py                # Main Streamlit UI
├── data.py               # Data fetching and cleaning helpers
├── plots.py              # Charting functions
├── metrics.py            # Analytics/statistics functions
├── test_data.py          # Unit tests for data helpers
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
├── assets/               # Screenshots and images
```

## Screenshots

![alt text](<assets/single-stock analysis.png>)
![alt text](<assets/multi-stock comparison.png>)