import yfinance as yf
import streamlit as st

st.title("🚀 My AI Stock Dashboard")

stocks = {
    # Core
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "L&T": "LT.NS",
    "ITC": "ITC.NS",

    # Growth
    "Tata Power": "TATAPOWER.NS",
    "ABB India": "ABB.NS",
    "Kalyan Jewellers": "KALYANKJIL.NS",
    "Clean Science": "CLEAN.NS",

    # High Growth / Tech
    "KPIT Tech": "KPITTECH.NS",
    "Dixon Tech": "DIXON.NS",

    # PSU / Rail
    "Bank of Baroda": "BANKBARODA.NS",
    "IRFC": "IRFC.NS",
    "IRCTC": "IRCTC.NS",

    # Thematic / Risk
    "Suzlon": "SUZLON.NS",
    "Apollo Micro": "APOLLO.NS",

    # Hidden Multibaggers
    "Kaynes": "KAYNES.NS",
    "Data Patterns": "DATAPATTNS.NS",
    "Jupiter Wagons": "JWL.NS",
    "Apar Industries": "APARINDS.NS",
    "Syrma SGS": "SYRMA.NS"
}

for name, ticker in stocks.items():
    st.subheader(name)

    try:
        data = yf.download(ticker, period="3mo")

        if data is None or data.empty:
            st.write("Data not available")
            continue

        close = data["Close"]

        if len(close) < 20:
            st.write("Not enough data")
            continue

        price = float(close.iloc[-1])
        ma20 = float(close.rolling(20).mean().iloc[-1])

        if ma20 == 0:
            st.write("Data issue")
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

        st.write(f"Price: ₹{round(price,2)}")
        st.write(f"Signal: {signal}")

    except:
        st.write("Error loading data")

    st.markdown("---")


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
