import yfinance as yf
import streamlit as st

st.title("🚀 My AI Stock Dashboard")

stocks = {
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "L&T": "LT.NS",
    "Tata Power": "TATAPOWER.NS"
}

for name, ticker in stocks.items():
    data = yf.download(ticker, period="3mo")["Close"]
    
    price = data.iloc[-1]
    ma20 = data.rolling(20).mean().iloc[-1]
    
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
nifty = yf.download("^NSEI", period="3mo")["Close"]
if nifty.iloc[-1] < nifty.rolling(50).mean().iloc[-1]:
    st.write("⚠️ Market Risk HIGH")
else:
    st.write("✅ Market SAFE")
