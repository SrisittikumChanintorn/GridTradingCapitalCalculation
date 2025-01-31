import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
from closesystem import visualization_zone_each_price, full_contract_price_for_cent_acc

# Set Streamlit page layout
st.set_page_config(layout="wide")

# Sidebar Inputs
st.sidebar.header("Grid Trading Parameters")


# Symbol Input (String)
symbol = st.sidebar.text_input("Assets Symbol", value="CL=F")  # Default to Crude Oil Futures

# EMA Length Input (Integer)
EMA_length = st.sidebar.number_input("EMA Length", min_value=10, max_value=500, value=200, step=1)

first_action_price = st.sidebar.number_input("Initail Investment ( First Time Action Price )", min_value=0.0, value=73.0, step=0.1)
balance = st.sidebar.number_input("Balance (USD)", min_value=1, value=200, step=10)
min_price = st.sidebar.number_input("Last Buy Zone Price Levels", min_value=0.0, value=0.0, step=0.1)
max_price = st.sidebar.number_input("Maximum Boundary Price", min_value=min_price, value=100.0, step=1.0)
contract_size = st.sidebar.number_input("Contract Size", min_value=1, value=10, step=1)
lot_size_fundA = st.sidebar.number_input("Lot Size (Fund A)", min_value=0.001, value=0.02, step=0.001, format="%.3f")
lot_size_fundB = st.sidebar.number_input("Lot Size (Fund B)", min_value=0.001, value=0.01, step=0.001, format="%.3f")
num_Zone_fundA = st.sidebar.number_input("Number of Zones (Fund A)", min_value=1, value=10, step=1)
num_Zone_fundB = st.sidebar.number_input("Number of Zones (Fund B)", min_value=1, value=20, step=1)
asset_digit = st.sidebar.number_input("Asset Decimal Digits", min_value=1, value=3, step=1)

# Download historical data for selected symbol
data = yf.download(symbol, interval="1d", period="3y")

# Fix MultiIndex issue
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(1)  # Drop the first level of MultiIndex

# Validate Close column exists
if 'Close' not in data.columns:
    st.error(f"Error: Data from Yahoo Finance does not contain 'Close' prices for {symbol}.")
    st.stop()

# Ensure 'Close' data is properly filled and formatted
df = data.copy()
df['Qcut'] = pd.qcut(df["Close"], q=4, labels=False)
df['Qcut'] = df['Qcut'] + 1

df['Close'] = df['Close'].astype(float)  # Ensure numeric format
df['EMA_Trend'] = df['Close'].ewm(span=EMA_length, adjust=False, min_periods=EMA_length).mean()

# Ensure index is datetime
df.index = pd.to_datetime(df.index)

# Compute action levels
fundA, fundB, fundA_price, fundB_price, action_level, first_action_cost, balance, reminding_funds, used_funds, lot_size_fundA, Total_fundA_price, lot_size_fundB, Total_fundB_price = full_contract_price_for_cent_acc(
    first_action_price=first_action_price,
    min=min_price,
    max=max_price,
    contract_size=contract_size,
    lot_size_fundA=lot_size_fundA,
    lot_size_fundB=lot_size_fundB,
    num_Zone_fundA=num_Zone_fundA,
    num_Zone_fundB=num_Zone_fundB,
    asset_digit=asset_digit,
    balance=balance
)

# UI Layout
with st.container():
    
    st.markdown("""
        <style>
            .block-container {
                max-width: 90%;
                margin-left: 1rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title(f"Grid Trading Capital Calculation: {symbol}")
    st.write('\n')
    st.markdown("#### Calculate grid trading strategy minimum investment capital")
    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write('\n')

    st.markdown("### Assets Symbol")
    st.markdown("###### Gold : GC=F &nbsp; &nbsp; &nbsp; USOUSD : CL=F")
    st.markdown("###### EURUSD = EURUSD=X &nbsp; &nbsp; GBP/USD = GBPUSD=X &nbsp; &nbsp; USD/JPY = USDJPY=X  &nbsp; AUD/USD = AUDUSD=X &nbsp; &nbsp; USD/CHF = USDCHF=X &nbsp; &nbsp; USD/CAD = USDCAD=X &nbsp; &nbsp;  NZD/USD = NZDUSD=X")
    st.markdown("###### SP500 = ^GSPC &nbsp; &nbsp; S&P 500 = ^GSPC &nbsp; &nbsp; DJI = ^DJI")

    st.write('\n')
    st.write('\n')
    st.write('\n')

   

    # Create two columns for layout
    col1, col2 = st.columns([1.5, 3], gap="small")

    with col1:
        st.subheader("Action Level Data")
        st.dataframe(action_level, height=600, use_container_width=True)

    with col2:
        st.subheader("Market Price & Investment Zones")
        fig = visualization_zone_each_price(df, first_action_price, fundA, fundB, symbol)
        fig.update_layout(height=650, width=850)
        st.plotly_chart(fig, use_container_width=True)

    # Display Trading Summary
    st.write('')
    st.write('')
    st.markdown("<h2 style='text-align: left; color: white;'>Trading Strategy Summary</h2>", unsafe_allow_html=True)
    st.write('')
    st.markdown(f"<p style='font-size:20px;'><strong>Cost of First Investment   :</strong> {first_action_cost} USC</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:20px;'><strong>Remaining Funds            :</strong> {reminding_funds} USC</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:20px;'><strong>Total Funds Used           :</strong> {used_funds} USC</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:20px;'><strong>Fund A Investment Size     :</strong> {lot_size_fundA} per zone, <strong>Total Cost:</strong> {Total_fundA_price} USC</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:20px;'><strong>Fund B Investment Size     :</strong> {lot_size_fundB} per zone, <strong>Total Cost:</strong> {Total_fundB_price} USC</p>", unsafe_allow_html=True)

