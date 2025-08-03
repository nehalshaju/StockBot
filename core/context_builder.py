def build_context(ticker, df, pe_ratio, sentiment):
    return f"""
Stock: {ticker}
Last Price: Rs.{df['Close'].iloc[-1]:.2f}
MA50: Rs.{df['MA50'].iloc[-1]:.2f}
RSI: {df['RSI'].iloc[-1]:.2f}
MACD: {df['MACD'].iloc[-1]:.2f}
MACD Histogram: {df['MACD_Hist'].iloc[-1]:.2f}
PE Ratio: {pe_ratio}
News Sentiment Score: {sentiment:.2f}
"""
