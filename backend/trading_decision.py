from tensorflow.keras.models import load_model
from model_lstm import *
from stock_data import *


# Function to run simulation script
def simulate(ticker, simulation_minutes = 57):
    logging.basicConfig(filename='stock_data_errors.log', level=logging.ERROR)
    for i in range(simulation_minutes-1):
        print(decision_making(ticker, i))

def decision_making(ticker, index=0):
    loaded_model = load_model(f"current_models/{ticker}_lstm.keras")

    # Fetch historical data
    stock_data = fetch_historical_data(ticker, '1d', '1m', index=index)

    # Scale the 'Close' data 
    scaled_data, scaler = scale_data(stock_data['Close'].values)

    # Create sequences for training
    X, y = create_sequences(scaled_data, 60)

    # Reshape X to be 3D [samples, time steps, features]
    X = X.reshape(X.shape[0], X.shape[1], 1)

    # Get the latest 60 minutes of data for prediction
    latest_data = stock_data['Close'].tail(60).values.reshape(-1, 1)

    # Predict the next minute's price
    predicted_price = predict_next_minute_price(loaded_model, latest_data, scaler)


    # Get current price
    current_price = (stock_data["Close"].iloc[-1].values[0])
    
    return predicted_price[0][0], current_price, stock_data['Volume'].iloc[-1].values[0] 


    
    #Fetch historical data (you can change ticker, period, and interval)
    #stock_data = fetch_historical_data(ticker, '1d', '1m', index=index+1)




if __name__ == '__main__':
    simulate("AAPL")
