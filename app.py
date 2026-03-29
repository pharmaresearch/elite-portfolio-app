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
    data = yf.download(ticker, period="3mo")

    # ✅ FIX: Check if data is empty
    if data.empty:
        st.write(f"{name}: Data not available")
        continue

    close = data["Close"]

    price = close.iloc[-1]
    ma20 = close.rolling(20).mean().iloc[-1]

    # ✅ FIX: avoid division error
    if ma20 == 0 or ma20 != ma20:  # handles NaN
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
    if close.iloc[-1] < close.rolling(50).mean().iloc[-1]:
        st.write("⚠️ Market Risk HIGH")
    else:
        st.write("✅ Market SAFE")
