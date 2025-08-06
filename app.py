import streamlit as st
import plotly.graph_objs as go
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

    # Create two columns for layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Candlestick Chart Section
        st.subheader("🕯️ Candlestick Chart with Buy/Sell Signals")

        try:
            # Define buy/sell signals based on technical indicators
            buys = df[(df['RSI'] < 30) & (df['Close'] > df['MA50'])]
            sells = df[df['RSI'] > 70]

            # Create candlestick chart
            candle_fig = go.Figure(
                data=[
                    go.Candlestick(
                        x=df.index,
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'],
                        name='OHLC',
                        increasing_line_color='green',
                        decreasing_line_color='red'
                    ),
                    go.Scatter(
                        x=buys.index,
                        y=buys['Close'],
                        mode='markers',
                        marker=dict(color='green', size=12, symbol='triangle-up'),
                        name='Buy Signal',
                        hovertemplate='<b>Buy Signal</b><br>Date: %{x}<br>Price: ₹%{y:.2f}<extra></extra>'
                    ),
                    go.Scatter(
                        x=sells.index,
                        y=sells['Close'],
                        mode='markers',
                        marker=dict(color='red', size=12, symbol='triangle-down'),
                        name='Sell Signal',
                        hovertemplate='<b>Sell Signal</b><br>Date: %{x}<br>Price: ₹%{y:.2f}<extra></extra>'
                    )
                ]
            )

            # Update layout for better appearance
            candle_fig.update_layout(
                height=500,
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis_rangeslider_visible=False,
                title=f"{st.session_state.ticker} - Stock Price with Trading Signals",
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                hovermode='x unified',
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )

            st.plotly_chart(candle_fig, use_container_width=True)

            # Signal summary
            buy_count = len(buys)
            sell_count = len(sells)
            st.info(f"📊 Signals in chart: {buy_count} Buy signals, {sell_count} Sell signals")

        except KeyError as e:
            st.error(f"Missing required columns for candlestick chart: {e}")
        except Exception as e:
            st.error(f"Error creating candlestick chart: {e}")

    with col2:
        # Latest indicators and metrics
        st.subheader("📊 Current Metrics")

        try:
            latest = df.iloc[-1]

            # Display key metrics
            st.metric("Close Price", f"₹{latest['Close']:.2f}")
            st.metric("MA50", f"₹{latest['MA50']:.2f}")
            st.metric("RSI", f"{latest['RSI']:.2f}")
            st.metric("PE Ratio", st.session_state.pe_ratio)

            # RSI gauge
            rsi_val = latest['RSI']
            if rsi_val < 30:
                rsi_color = "🟢 Oversold (Buy Zone)"
            elif rsi_val > 70:
                rsi_color = "🔴 Overbought (Sell Zone)"
            else:
                rsi_color = "🟡 Neutral"

            st.write(f"**RSI Status:** {rsi_color}")

            # Price vs MA50 trend
            if latest['Close'] > latest['MA50']:
                trend = "🔼 Above MA50 (Bullish)"
            else:
                trend = "🔽 Below MA50 (Bearish)"

            st.write(f"**Trend:** {trend}")

        except (KeyError, IndexError) as e:
            st.warning(f"Unable to display metrics: {e}")

    # Data table section
    st.subheader("📈 Latest Indicators")
    try:
        # Show last 5 days of data
        display_cols = ["Close", "MA50", "RSI", "MACD", "MACD_Hist"]
        available_cols = [col for col in display_cols if col in df.columns]

        if available_cols:
            recent_data = df[available_cols].tail(5).round(2)
            st.dataframe(recent_data, use_container_width=True)
        else:
            st.warning("Required indicator columns not found in data.")

        # Line chart for trends
        if len(available_cols) > 0:
            st.subheader("📊 Trend Lines")
            st.line_chart(df[available_cols])

    except Exception as e:
        st.warning(f"Error displaying indicators: {e}")

    # Dividend section
    st.subheader("💰 Top Dividend Stocks")
    table = get_top_dividends_table()
    if table is not None:
        st.dataframe(table, use_container_width=True)
    else:
        st.warning("Dividend data unavailable.")

# Chat history
st.subheader("💬 Chat with AI Assistant")
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