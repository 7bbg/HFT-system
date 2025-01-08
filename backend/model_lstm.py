import numpy as np
import time
import yfinance as yf
import logging
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from stock_data import *


# Scale the data using Min-Max Scaler
def scale_data(data):
    """Scale the data using Min-Max Scaler."""

    scaler = MinMaxScaler(feature_range=(0, 1))
    scale_data = scaler.fit_transform(data.reshape(-1, 1))  # Reshaping for single feature
    return scale_data, scaler

# Create sequences of data for training (60 minutes of past data to predict the next minute)
def create_sequences(data, time_step=60):
    """Create sequences of data for training."""
    X, y = [], []
    for i in range(time_step, len(data)):
        X.append(data[i-time_step:i, 0])  # 60 minutes of data
        y.append(data[i, 0])  # The next minute's price
    return np.array(X), np.array(y)

# Build the LSTM model
def build_lstm_model(X):
    """Build the LSTM model."""

    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

# Train the model
def train_model(model, X, y):
    """Train the model."""
    model.fit(X, y, epochs=5, batch_size=32)
    return model

# Predict the next minute's price using the LSTM model
def predict_next_minute_price(model, latest_data, scaler):
    """Predict the next minute's price."""
    # Scale the data
    scaled_latest_data = scaler.transform(latest_data)

    # Reshape the data for LSTM prediction (batch_size, time_step, features)
    latest_data_reshaped = scaled_latest_data.reshape(1, 60, 1)

    # Predict the next minute's price
    predicted_price = model.predict(latest_data_reshaped)

    # Reverse scaling to get actual predicted price
    predicted_price = scaler.inverse_transform(predicted_price)
    
    return predicted_price

def latest_60_minutes_of_data(stock_data):
    return stock_data['Close'].tail(60).values.reshape(-1, 1)

# Main function to fetch data, train model, and make predictions
def main():

    # Continuous Retraining and train for each stock ticker
    while True:

        # List of stock tickers
        stock_tickers = ["AAPL", 'GOOG','NFLX', 'AMZN', 'TSLA', 'NVDA']

        for ticker in stock_tickers:
            # Fetch historical data  for ticker
            stock_data = fetch_historical_data(ticker, '1d', '1m')
            
            # Scale the 'Close' data (values -> numpy array)
            scaled_data, scaler = scale_data(stock_data['Close'].values)

            # Create sequences for training
            X, y = create_sequences(scaled_data, 60)

            # Reshape X to be 3D [samples, time steps, features] 
            X = X.reshape(X.shape[0], X.shape[1], 1)

            # Build and train the LSTM model
            model = build_lstm_model(X)
            model = train_model(model, X, y)

            model.save(f'current_models/{ticker}_lstm.keras') # Save model
            
        time.sleep(3600) # Sleep for 1 hour then retrain on new data 


if __name__ == '__main__':
    main()
