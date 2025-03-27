import streamlit as st 
import numpy as np
import pandas as pd
import yfinance as yf
from closesystem import visualization_zone_each_price, full_contract_price_for_cent_acc

# Set Streamlit page layout
st.set_page_config(layout="wide")

# Sidebar Inputs
st.sidebar.header("Grid Trading Parameters")

# Asset selection dictionary
asset_buttons = {
    "USOUSD": "CL=F",
    "Gold": "GC=F",
    "EURUSD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CHF": "USDCHF=X",
    "USD/CAD": "USDCAD=X",
    "NZD/USD": "NZDUSD=X",
    "S&P500": "^GSPC"
}

# Initialize session state
if "symbol" not in st.session_state:
    st.session_state.symbol = list(asset_buttons.values())[0]  # default to first asset
if "init_price" not in st.session_state:
    st.session_state.init_price = None
if "max_price" not in st.session_state:
    st.session_state.max_price = None



symbol = st.session_state.symbol

# Download data
data = yf.download(symbol, interval="1d", period="3y")
if 'Close' not in data.columns:
    st.error(f"Error: 'Close' not found for {symbol}.")
    st.stop()

latest_price = float(data['Close'].dropna().iloc[-1])
max_dynamic = float(data['Close'].max() * 1.1)

# Update session values if not yet set
if st.session_state.init_price is None:
    st.session_state.init_price = latest_price
if st.session_state.max_price is None:
    st.session_state.max_price = max_dynamic


balance = st.sidebar.number_input("Balance (USD)", min_value=1, value=500, step=10)
first_action_price = st.sidebar.number_input("Initail Investment ( First Time Action Price )", min_value=0.0, value=st.session_state.init_price, step=0.1)
min_price = st.sidebar.number_input("Last Buy Zone Price Levels", min_value=0.0, value=0.0, step=0.1)
max_price = st.sidebar.number_input("Maximum Boundary Price", min_value=min_price, value=st.session_state.max_price, step=1.0)
contract_size = st.sidebar.number_input("Contract Size", min_value=1, value=10, step=1)
asset_digit = st.sidebar.number_input("Asset Decimal Digits", min_value=1, value=3, step=1)
lot_size_fundA = st.sidebar.number_input("Lot Size (Fund A)", min_value=0.001, value=0.02, step=0.001, format="%.3f")
lot_size_fundB = st.sidebar.number_input("Lot Size (Fund B)", min_value=0.001, value=0.01, step=0.001, format="%.3f")
num_Zone_fundA = st.sidebar.number_input("Number of Zones (Fund A)", min_value=1, value=5, step=1)
num_Zone_fundB = st.sidebar.number_input("Number of Zones (Fund B)", min_value=1, value=10, step=1)
EMA_length = st.sidebar.number_input("EMA Length", min_value=10, max_value=500, value=200, step=1)

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

    st.markdown("""
        ##### This program is designed to **calculate the minimum capital required** for running a grid trading strategy. It helps you determine how much capital you'd need to execute your chosen grid zones on a selected asset.

        ---

        ### ♟️ What is Grid Trading?

        Grid Trading is a non-directional strategy that avoids using stop-losses.  
        Instead, it invests fully at specific price zones — aiming to hold positions until the market recovers to profit levels.  
        It’s best suited for:

        - 📊 Sideways or mean-reverting markets  
        - 🏦 Assets with strong fundamentals (hard to drop to zero)

        This program also includes a **KZM-style**, which separates the strategy into:

        - 🅰️ **Fund A** – Larger position sizes at wider intervals, targeting long-term opportunities  
        - 🅱️ **Fund B** – Smaller positions at tighter zones, aiming for quicker, smaller returns

        ---

        ### 🧭 How to Use

        1. **Select an Asset** – Choose one with low likelihood of collapse  
        2. **Set Price Boundaries** – Define expected max/min range  
        3. **Define Grid Zones** – Number of price levels (for both Fund A and B)  
        4. **Set Position Sizes** – Specify how much to invest per level for each strategy

        ---

        ### 💡 Pro Tip

        Grid strategies usually offer **linear, stable returns** with low risk.  
        Many traders use them for:

        - 📈 Long-term growth with consistent income  
        - 🧪 Gaining trading experience with focus on capital survival  
        - 🔁 Reinvesting profits into higher-risk strategies later

        <br>
        <br>
    """, unsafe_allow_html=True)





    st.markdown("### <br> Asset Selection ", unsafe_allow_html=True)

    # Move the asset button UI here below the heading but before explanation
    cols = st.columns(4)
    for idx, (label, ticker) in enumerate(asset_buttons.items()):
        with cols[idx % 4]:
            if st.button(label):
                st.session_state.symbol = ticker
                st.session_state.init_price = None
                st.session_state.max_price = None
                st.rerun()

    st.markdown("""<br>
    <div style='font-size: 17px; line-height: 1.8; margin-bottom: 40px;'>
    <strong>Important Required Inputs that    MUST MANUAL INITAIL     :</strong><br><br>
    1. <strong>Select Asset Symbol</strong> – Choose the financial asset you want to trade (e.g., Gold, EURUSD, SP500).<br>
    2. <strong>Initial Investment</strong> – The first price level where your investment will begin.<br>
    3. <strong>Maximum Boundary Price</strong> – The upper limit of the price range you expect the asset to stay below.<br>
    4. <strong>Last Buy Zone Price Levels</strong> – The lowest price level at which you will still buy the asset.<br>
    5. <strong>Contract Size</strong> – The contract size associated with the selected asset.<br>
    6. <strong>Lot Size (Fund A)</strong> – The fixed lot size for each grid level in Fund A's strategy.<br>
    7. <strong>Lot Size (Fund B)</strong> – The fixed lot size for each grid level in Fund B's strategy.<br>
    8. <strong>Number of Zones (Fund A)</strong> – The total number of price zones in Fund A's grid strategy.<br>
    9. <strong>Number of Zones (Fund B)</strong> – The total number of price zones in Fund B's grid strategy.<br>
    10. <strong>Asset Decimal Digits</strong> – The number of decimal places used by the selected asset.<br>
    </div>
    """, unsafe_allow_html=True)

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)

    df = data.copy()
    df['Qcut'] = pd.qcut(df["Close"], q=4, labels=False) + 1
    df['Close'] = df['Close'].astype(float)
    df['EMA_Trend'] = df['Close'].ewm(span=EMA_length, adjust=False, min_periods=EMA_length).mean()
    df.index = pd.to_datetime(df.index)

    fundA, fundB, fundA_price, fundB_price, action_level, first_action_cost, balance, reminding_funds, used_funds, lot_size_fundA, Total_fundA_price, lot_size_fundB, Total_fundB_price = full_contract_price_for_cent_acc(
        balance=balance, 
        first_action_price=first_action_price,
        max=max_price,
        min=min_price,
        contract_size=contract_size,
        asset_digit=asset_digit,
        lot_size_fundA=lot_size_fundA,
        lot_size_fundB=lot_size_fundB,
        num_Zone_fundA=num_Zone_fundA,
        num_Zone_fundB=num_Zone_fundB,
    )

    col1, col2 = st.columns([1.5, 3], gap="small")

    with col1:
        st.subheader("Action Level Data")
        st.dataframe(action_level, height=600, use_container_width=True)

    with col2:
        st.subheader("Market Price & Investment Zones")
        fig = visualization_zone_each_price(df, first_action_price, fundA, fundB, symbol)
        fig.update_layout(height=650, width=850)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<h2 style='text-align: left; color: white;'>Trading Strategy Summary</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:20px;'><strong>Cost of First Investment   :</strong> {np.round(first_action_cost,2)} USC</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:20px;'><strong>Remaining Funds            :</strong> {np.round(reminding_funds,2)} USC</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:20px;'><strong>Total Funds Used           :</strong> {np.round(used_funds,2)} USC</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:20px;'><strong>Fund A Investment Size     :</strong> {lot_size_fundA} per zone, <strong>Total Cost:</strong> {np.round(Total_fundA_price,2)} USC</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:20px;'><strong>Fund B Investment Size     :</strong> {lot_size_fundB} per zone, <strong>Total Cost:</strong> {np.round(Total_fundB_price,2)} USC</p>", unsafe_allow_html=True)
