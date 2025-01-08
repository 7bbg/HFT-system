from flask import Flask, jsonify, request
import yfinance as yf
import numpy as np
import time
import psutil
from stock_data import *
from trading_decision import *
from constants import *

app = Flask(__name__)

money = MONEY

# Function to get CPU and memory utilization
def get_system_utilization():
    cpu_utilization = psutil.cpu_percent()
    memory_utilization = psutil.virtual_memory().percent
    return cpu_utilization, memory_utilization

def compare_predicted_vs_actual(predicted_price, actual_price):
    # Calculate absolute error
    absolute_error = abs(predicted_price - actual_price)
    
    return absolute_error * 100

def get_actual_price(ticker, index):
    stock_data = fetch_historical_data(ticker, '1d', '1m', index=index)
    actual_price = stock_data['Close'].tail(1).iloc[0].to_numpy()[0]
    return actual_price

# Route to return market data
@app.route('/market_data', methods=['GET'])
def market_data():
    ticker = request.args.get('ticker',default='AAPL')
    index = request.args.get('index')
    data = fetch_historical_data( ticker= ticker,
                                    period= "1d",
                                    interval= '1m',
                                    index = int(index))
    return data.to_json(orient='records') if ticker in tickers else jsonify({})

# Route to return HFT stats over time
@app.route('/trading/hft-stats', methods=['GET'])
def hft_stats():
    global money

    index = int(request.args.get('index'))
    ticker = request.args.get('ticker',default='AAPL')

    predicted_price, current_price, volume = decision_making(ticker, index)
    actual_price = get_actual_price(ticker, index+1)
    absolute_error = compare_predicted_vs_actual(predicted_price, actual_price)

    signal = 'HOLD'
    if(predicted_price > current_price ):
        money -=  (volume * current_price)
        signal = 'BUY'
    elif predicted_price < current_price :
        signal = 'SELL'
        money +=  (volume * current_price)
    else:
        signal = 'HOLD'

        
    return jsonify({'absolute_error': absolute_error, "signal": signal, "money": money}) if ticker in tickers else jsonify({})

# Route to return CPU and memory utilization
@app.route('/system_utilization', methods=['GET'])
def system_utilization():
    cpu_utilization, memory_utilization =  get_system_utilization()
    return jsonify({'cpu_utilization': cpu_utilization, 'memory_utilization': memory_utilization})

if __name__ == '__main__':
    app.run(debug=True)