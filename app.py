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
    try:
        data = yf.download(ticker, period="3mo")

        # Check if data exists
        if data is None or data.empty:
            st.write(f"{name}: Data not available")
            continue

        close = data["Close"]

        # Ensure enough data
        if len(close) < 20:
            st.write(f"{name}: Not enough data")
            continue

        price = float(close.iloc[-1])
        ma20 = float(close.rolling(20).mean().iloc[-1])

        # Final safety check
        if ma20 == 0:
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

    except Exception as e:
        st.write(f"{name}: Error loading data")

# Market Risk
try:
    nifty = yf.download("^NSEI", period="3mo")

    if nifty is not None and not nifty.empty:
        close = nifty["Close"]

        if len(close) >= 50:
            price = float(close.iloc[-1])
            ma50 = float(close.rolling(50).mean().iloc[-1])

            if price < ma50:
                st.write("⚠️ Market Risk HIGH")
            else:
                st.write("✅ Market SAFE")

except:
    st.write("Market data error")
