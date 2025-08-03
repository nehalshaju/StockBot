# sentiment.py
from textblob import TextBlob

def get_news(symbol):
    # Dummy example — you’d integrate a real API
    return [
        f"{symbol} shares hit new highs!",
        f"{symbol} drops after quarterly earnings",
    ]

def get_news_sentiment(symbol):
    articles = get_news(symbol)
    sentiments = [TextBlob(article).sentiment.polarity for article in articles]
    return sum(sentiments) / len(sentiments) if sentiments else 0
