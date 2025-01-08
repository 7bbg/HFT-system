
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import yfinance as yf
import time
import plotly.graph_objects as go
import os

LOCAL_SERVER = "http://localhost:5000"

# Function to get market data from the Flask API
def get_market_data(ticker, index=0):

    response = requests.get(f'{LOCAL_SERVER}/market_data?ticker={ticker}&index={index}')
    data = response.json()
    return pd.DataFrame(data)

# Function to get close price from the market data
def get_close_price(data, ticker):
    prices = data[f"('Close', '{ticker}')"]
    return prices


# Function to get CPU and memory utilization from the Flask API
def get_system_utilization():
    response = requests.get(f'{LOCAL_SERVER}/system_utilization')
    cpu_utilization = response.json()['cpu_utilization']
    memory_utilization = response.json()['memory_utilization']
    return cpu_utilization, memory_utilization

# Function to get market data from the Flask API
def get_hft_stat(ticker, index=0):
    response = requests.get(f'{LOCAL_SERVER}/trading/hft-stats?ticker={ticker}&index={index}')
    stats = response.json()

    absolute_error = stats["absolute_error"]
    signal = stats["signal"]
    money = stats["money"]

    return absolute_error, signal, money


# Create a Streamlit app
st.title('Trading Algorithm Visualization')

# Create a dropdown menu to select the ticker
ticker = st.sidebar.selectbox('Select a ticker', ["AAPL", 'GOOG','NFLX', 'AMZN', 'TSLA', 'NVDA'])

# Create a button to start the visualization
start_button = st.button('Visualize')

# Create a placeholder for the visualization
visualization_placeholder = st.empty()

# Create placeholders for each chart
price_placeholder = st.empty()
absolute_error_placeholder = st.empty()
money_placeholder = st.empty()
cpu_placeholder = st.empty()
memory_placeholder = st.empty()
signal_placeholder = st.empty()

# Store past system utilization information for revisting
memory_stack = []
cpu_stack = []

# Function to update the visualization
def update_visualization():

    
    global memory_stack
    global cpu_stack

    absolute_error_stack = []
    signal_stack = [[],[]]
    money_stack = []

    # Update the visualization placeholder with Plotly charts for the next 58 timestep
    for i in range(58):
        # Get updated market data from the API
        market_data = get_market_data(ticker, i)
        prices = get_close_price(market_data, ticker)
        cpu_utilization, memory_utilization = get_system_utilization()
        absolute_error, signal, money = get_hft_stat(ticker, i)
        
        absolute_error_stack.append(absolute_error)
        money_stack.append(money)
        cpu_stack.append(cpu_utilization)
        memory_stack.append(memory_utilization)
        
        # If signal is buy update 0 index else if signal is SELL 1 index
        if(signal == "BUY"):

            signal_stack[0].append(signal_stack[0][-1]+1 if len(signal_stack[0]) else 1)
            signal_stack[1].append(signal_stack[1][-1] if len(signal_stack[1]) else 0)
            
        elif (signal == "SELL"):
            signal_stack[1].append(signal_stack[1][-1]+1 if len(signal_stack[1]) else 1)
            signal_stack[0].append(signal_stack[0][-1] if len(signal_stack[0]) else 0)

        

        # Create a Plotly figure for price movements
        fig1 = px.line(x=range(len(prices)), y=prices, title='Price Movements', labels={'x': 'Time', 'y': 'Price'})
        
        # Create a Plotly figure for absolute error over time
        fig2 = px.line(x=range(len(absolute_error_stack)), y=absolute_error_stack, title='Absolute Error', labels={'x': 'Time', 'y': 'Absolute Error (%)'})
    
        # Create a Plotly figure for avaiable money over time
        fig3 = px.line(x=range(len(money_stack)), y=money_stack, title='Avaliable Money', labels={'x': 'Time', 'y': 'Avaliable Money ($)'})

        # Create a Plotly figure for CPU utilization
        fig4 = px.line(x=range(len(cpu_stack)), y=cpu_stack, title='CPU Utilization', labels={'x': 'Time', 'y': 'CPU Utilization (%)'})

        # Create a Plotly figure for memory utilization
        fig5 = px.line(x=range(len(memory_stack)), y=memory_stack, title='Memory Utilization', labels={'x': 'Time', 'y': 'Memory Utilization (%)'})

        # Create a Plotly figure with multiple traces (for different signals[Buy, Sell])
        fig = go.Figure()

        # Add the sell line
        fig.add_trace(go.Scatter(x=list(range(len(signal_stack[1]))), y=signal_stack[1], mode='lines', name='Sell'))

        # Add the buy line
        fig.add_trace(go.Scatter(x=list(range(len(signal_stack[0]))), y=signal_stack[0], mode='lines', name='Buy'))

        # Update layout (optional)
        fig.update_layout(
            title='Buy and Sell Values Over Time',
            xaxis_title='Time',
            yaxis_title='Value',
            template='plotly_dark',  
        )

        # Update the placeholder with the new data
        price_placeholder.plotly_chart(fig1, use_container_width=True, key=f'price_{time.time()}')
        absolute_error_placeholder.plotly_chart(fig2, use_container_width=True, key=f'absolute_error_{time.time()}')
        money_placeholder.plotly_chart(fig3, use_container_width=True, key=f'money_{time.time()}')
        cpu_placeholder.plotly_chart(fig4, use_container_width=True,  key=f'cpu_{time.time()}')
        memory_placeholder.plotly_chart(fig5, use_container_width=True, key=f'memory_{time.time()}')
        signal_placeholder.plotly_chart(fig, use_container_width=True, key=f'signal_{time.time()}')


        print("Updated Placeholders")

        time.sleep(1)  # Set to 1s For HFT simulation 
    
# Start the visualization when the button is clicked
if start_button:
    update_visualization()
