import unittest
import pandas as pd
import numpy as np
import logging
from io import StringIO
from unittest.mock import patch

from stock_data import fetch_historical_data, get_recent_data_excluding_last_60, get_recent_data_last_60_min

class TestStockDataFunctions(unittest.TestCase):

    @patch("yfinance.download")
    def test_fetch_historical_data(self, mock_download):
        # Mock the stock data to return a sample DataFrame
        mock_data = pd.DataFrame({
            'Open': [100, 102, 105, 107, 110],
            'High': [101, 103, 106, 108, 111],
            'Low': [99, 101, 104, 106, 109],
            'Close': [100, 102, 105, 107, 110],
            'Volume': [1000, 2000, 3000, 4000, 5000]
        }, index=pd.date_range("2025-01-07 09:00", periods=5))

        mock_download.return_value = mock_data
        
        # Call the function and check the result
        stock_data = fetch_historical_data(ticker="AAPL", period="1d", interval="1m", all=True)
        self.assertIsNotNone(stock_data)
        self.assertEqual(len(stock_data), 5)
        self.assertEqual(stock_data.iloc[0]['Close'], 100)

            


    def test_get_recent_data_excluding_last_60(self):
        # Create a sample stock data for testing
        stock_data = pd.DataFrame({
            'Open': np.arange(100, 110),
            'High': np.arange(101, 111),
            'Low': np.arange(99, 109),
            'Close': np.arange(100, 110),
            'Volume': np.arange(1000, 1010)
        }, index=pd.date_range("2025-01-07 09:00", periods=10))

        # Test the function for excluding the last 60 minutes
        stock_data_excluding_last_60 = get_recent_data_excluding_last_60(stock_data)

        self.assertEqual(len(stock_data_excluding_last_60), 0)

    def test_get_recent_data_last_60_min(self):
        # Create a sample stock data for testing
        stock_data = pd.DataFrame({
            'Open': np.arange(100, 110),
            'High': np.arange(101, 111),
            'Low': np.arange(99, 109),
            'Close': np.arange(100, 110),
            'Volume': np.arange(1000, 1010)
        }, index=pd.date_range("2025-01-07 09:00", periods=10))

        # Test the function for retrieving the last 60 minutes
        stock_data_last_60 = get_recent_data_last_60_min(stock_data)

        self.assertEqual(len(stock_data_last_60), 10)
        self.assertEqual(stock_data_last_60["Close"].iloc[-1], 109)

    @patch('sys.stdout', new_callable=StringIO)
    def test_logging_on_fetch_error(self, mock_stdout):
        # Simulate an error in fetching data
        with patch('yfinance.download', side_effect=Exception("API failure")):
            stock_data = fetch_historical_data(ticker="AAPL", period="1d", interval="1m", all=True)
            
            # Check if error was logged
            output = mock_stdout.getvalue()
            self.assertIn("Error fetching data:", output)
            self.assertIn("API failure", output)

if __name__ == '__main__':
    unittest.main()
