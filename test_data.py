"""
===============================================================================
test_data.py
-------------------------------------------------------------------------------
Unit tests for data.py (data fetching and cleaning helpers).
Tests cover extraction of Close series, rolling averages, and edge cases.
===============================================================================
"""
import unittest
import pandas as pd
from data import _get_close_series, rolling_average

class TestDataHelpers(unittest.TestCase):
    def test_get_close_series_dataframe(self):
        df = pd.DataFrame({
            'Close': [100, 101, 102],
            'Volume': [1000, 1100, 1200]
        }, index=pd.date_range('2023-01-01', periods=3))
        close = _get_close_series(df)
        self.assertTrue(isinstance(close, pd.Series))
        self.assertEqual(list(close), [100, 101, 102])

    def test_get_close_series_series(self):
        s = pd.Series([200, 201, 202], name='Close', index=pd.date_range('2023-01-01', periods=3))
        close = _get_close_series(s)
        self.assertTrue(isinstance(close, pd.Series))
        self.assertEqual(list(close), [200, 201, 202])

    def test_get_close_series_multiindex(self):
        arrays = [['Close', 'Close', 'Volume'], ['AAPL', 'MSFT', 'AAPL']]
        index = pd.MultiIndex.from_arrays(arrays, names=('Type', 'Ticker'))
        df = pd.DataFrame([[1, 2, 100], [3, 4, 200]], columns=index)
        close = _get_close_series(df)
        self.assertTrue(isinstance(close, pd.DataFrame) or isinstance(close, pd.Series))

    def test_rolling_average(self):
        import math
        df = pd.DataFrame({'Close': [10, 20, 30, 40, 50]})
        avg = rolling_average(df, window=2)
        avg_list = list(avg)
        self.assertTrue(math.isnan(avg_list[0]))
        self.assertEqual(avg_list[1:], [15.0, 25.0, 35.0, 45.0])

    def test_get_close_series_none(self):
        self.assertIsNone(_get_close_series(None))

if __name__ == "__main__":
    unittest.main()
