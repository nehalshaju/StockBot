import streamlit as st
from core.state import init_session_state
from core.analyzer import analyze_stock
from core.dividend_utils import get_top_dividends_table
from core.context_builder import build_context
from core.llm_client import query_llm

init_session_state()

st.set_page_config(page_title="Stock Analysis Chatbot", layout="wide")

# Sidebar input
ticker_input = st.sidebar.text_input("Enter NSE stock ticker (e.g. INFY.NS):", value="RELIANCE.NS")
model_name = st.sidebar.selectbox(
    "Choose LLM model",
    [
        "openrouter/auto",
        "mistralai/mistral-large-2407",
        "mistralai/mixtral-8x22b-instruct",
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4o-2024-08-06",
        "openrouter/auto"
    ],
    index=0
)

if st.sidebar.button("Fetch & Analyze"):
    with st.spinner("Analyzing stock..."):
        try:
            df, pe, sentiment = analyze_stock(ticker_input)
            st.session_state.df = df
            st.session_state.ticker = ticker_input
            st.session_state.pe_ratio = f"{pe:.2f}" if pe else "N/A"
            st.session_state.sentiment = sentiment
            st.success(f"{ticker_input} loaded successfully.")
        except Exception as e:
            st.error(f"Error: {e}")

# Main content
st.title("Stock Analysis Chatbot")

if st.session_state.df is not None:
    df = st.session_state.df

    st.subheader("Latest Indicators")
    try:
        st.dataframe(df.tail(5)[["Close", "MA50", "RSI", "MACD", "MACD_Hist"]])
        st.line_chart(df[["Close", "MA50", "RSI", "MACD"]])
    except KeyError:
        st.warning("Required indicators missing in the data.")

    st.subheader("Top Dividend Stocks")
    table = get_top_dividends_table()
    if table is not None:
        st.dataframe(table)
    else:
        st.warning("Dividend data unavailable.")

# Chat history
for msg in st.session_state.history:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input
user_input = st.chat_input("Ask about the stock analysis...")
if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})

    if st.session_state.df is None:
        reply = "Please load stock data first using the sidebar."
    else:
        prompt = f"""
You are a financial stock assistant.

{build_context(
    st.session_state.ticker,
    st.session_state.df,
    st.session_state.pe_ratio,
    st.session_state.sentiment
)}

User question: "{user_input}"
"""
        reply = query_llm(prompt, model=model_name)

    st.session_state.history.append({"role": "assistant", "content": reply})
    st.rerun()
