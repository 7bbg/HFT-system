import numpy as np
import time
import pandas as pd
import yfinance as yf
import logging

# Fetch historical data for a specified stock
def fetch_historical_data(ticker="AAPL", period="1d", interval='1m', all=False, index = 0):
    """Fetch historical data for a specified stock."""

    try:
        # Try to fetch data
        print(f"Fetching data for {ticker}...")
        stock_data = yf.download(ticker, period=period, interval=interval)
        if stock_data.empty:
            raise ValueError(f"No data found for {ticker}")
        print("Data fetched successfully!")

        return stock_data[:-59+int(index)] if not all else stock_data
    
    except Exception as e:
        # If there's an error log it
        print(f"Error fetching data: {e}")
        logging.error(f"Error fetching data: {e}")
        return None


# Function to get the current date and time, excluding the last 60 minutes
def get_recent_data_excluding_last_60(stock_data):
    """Get the stock data excluding the last 60 minutes."""

    if(len(stock_data)<=60):
        return pd.DataFrame()

    # Remove the last 60 minutes from the stock data
    stock_data_excluding_last_60 = stock_data[:len(stock_data)-60]
    
    return stock_data_excluding_last_60

def get_recent_data_last_60_min(stock_data):
    """Get the stock data last 60 minutes."""
    return stock_data[-60:]


# Main function to run the script
def main():
    logging.basicConfig(filename='logs/stock_data_errors.log', level=logging.ERROR)

    # Fetch historical data for the last day with 1-minute intervals
    stock_data = fetch_historical_data(ticker="AAPL", period="1d", interval="1m", all=True)

    # Get data excluding the last 60 minutes
    stock_data_excluding_last_60 = get_recent_data_excluding_last_60(stock_data)

    # Get last 60 minutes data
    stock_data_last_60 = get_recent_data_last_60_min(stock_data)

    print("All stock recent data")
    print(stock_data)
    
    print("All stock recent data exclusing last 60 min")
    print(stock_data_excluding_last_60)

    print("All stock recent data last 60 min")
    print(stock_data_last_60)



if __name__ == '__main__':
    main()
