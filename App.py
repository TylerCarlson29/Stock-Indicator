pip install yfinance

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- APP CONFIG ---
st.set_page_config(page_title="Market Insights", layout="wide")
st.title("📈 Financial Data & RSI Dashboard")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("User Settings")
ticker = st.sidebar.text_input("Enter Ticker Symbol", value="NVDA").upper()
days_to_plot = st.sidebar.slider("Days to View", 30, 365, 180)

# --- DATA FETCHING ---
@st.cache_data
def get_data(symbol, days):
    data = yf.download(symbol, period=f"{days}d")
    return data

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- MAIN CONTENT ---
try:
    df = get_data(ticker, days_to_plot)
    
    if not df.empty:
        # Metrics Row
        last_price = df['Close'].iloc[-1]
        prev_price = df['Close'].iloc[-2]
        price_diff = last_price - prev_price
        
        col1, col2, col3 = st.columns(3)
        col1.metric(f"{ticker} Price", f"${last_price:,.2f}", f"{price_diff:,.2f}")
        
        # Calculate RSI
        df['RSI'] = calculate_rsi(df)
        current_rsi = df['RSI'].iloc[-1]
        col2.metric("RSI (14)", f"{current_rsi:.2f}")

        # Main Price Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Price", line=dict(color="#00FFAA")))
        fig.update_layout(title=f"{ticker} Price Action", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # RSI Chart
        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI", line=dict(color="#FFB000")))
        rsi_fig.add_hline(y=70, line_dash="dash", line_color="red")
        rsi_fig.add_hline(y=30, line_dash="dash", line_color="green")
        rsi_fig.update_layout(title="RSI Indicator", yaxis_range=[0, 100], template="plotly_dark")
        st.plotly_chart(rsi_fig, use_container_width=True)
        
        # Raw Data Toggle
        with st.expander("View Raw Data"):
            st.dataframe(df.tail(10))
    else:
        st.warning("No data found for that ticker. Please check the symbol.")

except Exception as e:
    st.error(f"Error: {e}")
