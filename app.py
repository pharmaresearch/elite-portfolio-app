import yfinance as yf
import streamlit as st
import pandas as pd

st.title("🚀 My AI Stock Dashboard")

stocks = {
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "L&T": "LT.NS",
    "Tata Power": "TATAPOWER.NS"
}

for name, ticker in stocks.items():
    data = yf.download(ticker, period="3mo")

    # Check if data exists
    if data.empty:
        st.write(f"{name}: Data not available")
        continue

    close = data["Close"]

    # Need at least 20 values
    if len(close) < 20:
        st.write(f"{name}: Not enough data")
        continue

    price = close.iloc[-1]
    ma20 = close.rolling(20).mean().iloc[-1]

    # Proper NaN check (THIS FIXES ERROR)
    if pd.isna(ma20):
        st.write(f"{name}: Data issue")
        continue

    momentum = price / ma20

    if momentum > 1.05:
        signal = "🚀 STRONG BUY"
    elif momentum > 1:
        signal = "🟢 BUY"
    elif momentum < 0.95:
        signal = "🔻 SELL"
    else:
        signal = "⚖️ HOLD"

    st.write(f"{name}: ₹{round(price,2)} → {signal}")

# Market Risk
nifty = yf.download("^NSEI", period="3mo")

if not nifty.empty:
    close = nifty["Close"]
    if len(close) >= 50:
        ma50 = close.rolling(50).mean().iloc[-1]
        if not pd.isna(ma50):
            if close.iloc[-1] < ma50:
                st.write("⚠️ Market Risk HIGH")
            else:
                st.write("✅ Market SAFE")
