# ui.py
from StockBot.core.data import get_latest_price
from StockBot.core.analysis import compute_indicators
from StockBot.core.sentiment import get_news_sentiment
from StockBot.core.data import get_price_data

def cli_bot():
    print("🤖 Welcome to the Indian Stock Analysis Bot!")
    while True:
        inp = input("You: ").strip().lower()
        if inp == "exit":
            print("🤖 Goodbye!")
            break
        elif inp.startswith("price"):
            sym = inp.split()[1].upper()
            price = get_latest_price(sym)
            print(f"🤖 Latest price of {sym}: Rs.{price:.2f}")
        elif inp.startswith("indicators"):
            sym = inp.split()[1].upper()
            df = compute_indicators(get_price_data(sym))
            print(df.tail(3)[['Close', 'MA50', 'RSI']])
        elif inp.startswith("sentiment"):
            sym = inp.split()[1].upper()
            sentiment_score = get_news_sentiment(sym)
            print(f"🤖 News sentiment for {sym}: {sentiment_score:.2f}")
        else:
            print("🤖 Sorry, I didn’t understand. Try: price, indicators, sentiment, or exit")

# Usage:
# cli_bot()
