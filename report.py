import yfinance as yf
import pandas as pd
import pandas_ta as ta
from fpdf import FPDF
from datetime import datetime
import streamlit as st
from io import BytesIO

# === CONFIG ===
DEFAULT_TICKER = "INFY.NS"

# === FETCH STOCK DATA ===
def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    stock_summary = {
        "Company": info.get("longName", "N/A"),
        "Sector": info.get("sector", "N/A"),
        "Market Cap": info.get("marketCap", "N/A"),
        "PE Ratio": info.get("trailingPE", "N/A"),
        "EPS": info.get("trailingEps", "N/A"),
        "Dividend Yield": info.get("dividendYield", "N/A"),
        "52 Week High": info.get("fiftyTwoWeekHigh", "N/A"),
        "52 Week Low": info.get("fiftyTwoWeekLow", "N/A"),
        "Current Price": info.get("currentPrice", "N/A")
    }
    return stock_summary, stock

# === DIVIDEND HISTORY ===
def get_dividend_history(stock):
    dividends = stock.dividends
    if dividends.empty:
        return "No dividend history available."
    return dividends.tail(5).to_string()

# === PRICE SUMMARY ===
def get_price_summary(stock):
    hist = stock.history(period="1y")
    if hist.empty:
        return hist, "No historical price data available."
    summary = {
        "1Y High": hist["Close"].max(),
        "1Y Low": hist["Close"].min(),
        "1Y Mean": hist["Close"].mean(),
        "1Y Volatility (Std Dev)": hist["Close"].std()
    }
    return hist, "\n".join([f"{k}: {round(v, 2)}" for k, v in summary.items()])

# === TECHNICAL INDICATORS ===
def get_technical_indicators(df):
    df['RSI'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'])
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_Hist'] = macd['MACDh_12_26_9']
    latest = df.iloc[-1]
    return f"RSI: {latest['RSI']:.2f}\nMACD: {latest['MACD']:.2f}\nMACD Histogram: {latest['MACD_Hist']:.2f}"

# === PDF REPORT GENERATOR ===
def generate_pdf(stock_data, dividend_text, price_text, tech_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(200, 10, txt=f"Stock Analysis Report: {stock_data['Company']}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, "Basic Stock Data", ln=True)
    pdf.set_font("Arial", size=12)
    for k, v in stock_data.items():
        pdf.multi_cell(0, 10, f"{k}: {v}")

    pdf.ln(5)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, "Dividend History", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, dividend_text)

    pdf.ln(5)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, "Price Summary", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, price_text)

    pdf.ln(5)
    pdf.set_font("Arial", style='B', size=12)
    pdf.cell(200, 10, "Technical Indicators", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, tech_text)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# === STREAMLIT APP ===
st.title("📄 PDF Stock Report Generator")
ticker = st.text_input("Enter stock ticker (e.g., INFY.NS):", value=DEFAULT_TICKER)

if st.button("Generate Report"):
    with st.spinner("Fetching and analyzing data..."):
        stock_data, stock_obj = fetch_stock_data(ticker)
        dividend_history = get_dividend_history(stock_obj)
        hist_df, price_summary = get_price_summary(stock_obj)
        tech_indicators = get_technical_indicators(hist_df)

        pdf_file = generate_pdf(stock_data, dividend_history, price_summary, tech_indicators)

    st.success("✅ PDF Report Generated!")
    st.download_button(
        label="📥 Download PDF",
        data=pdf_file,
        file_name=f"{ticker}_stock_report.pdf",
        mime="application/pdf"
    )
