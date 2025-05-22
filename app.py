
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests, os
from dotenv import load_dotenv
from textblob import TextBlob

load_dotenv()

# PulseStocks API - Market Emotion Engine 💹🧠
app = FastAPI(
    title="📊 PulseStocks API",
    description="Get real-time stock data & news sentiment in a heartbeat. Built for traders who follow both trends **and** emotions.",
    version="1.0.0",
    contact={
        "name": "PulseStocks Dev Team",
        "url": "https://github.com/yourusername/pulsestocks",
        "email": "support@pulsestocks.app"
    },
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup for frontend app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Restrict in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Config
IEX_API_KEY = os.getenv("IEX_API_KEY")
IEX_BASE_URL = "https://cloud.iexapis.com/stable"

@app.get("/", tags=["Status"])
def home():
    return {
        "app": "PulseStocks API",
        "version": "1.0",
        "status": "✅ Live",
        "features": [
            "📈 Real-time stock data",
            "🧠 AI-powered sentiment analysis",
            "📰 Latest headlines",
            "🚀 Ready for Flutter & web integration"
        ]
    }

@app.get("/stock/{symbol}", tags=["Stock Data"])
def get_stock(symbol: str):
    """
    Get real-time stock quote for a symbol (e.g., AAPL).
    """
    url = f"{IEX_BASE_URL}/stock/{symbol}/quote?token={IEX_API_KEY}"
    res = requests.get(url)
    if res.status_code != 200:
        return {"error": f"Failed to fetch data for {symbol.upper()}"}
    return res.json()

@app.get("/sentiment/{symbol}", tags=["Sentiment Analysis"])
def get_sentiment(symbol: str):
    """
    Fetch latest news for a stock and run basic sentiment analysis.
    """
    url = f"{IEX_BASE_URL}/stock/{symbol}/news/last/5?token={IEX_API_KEY}"
    res = requests.get(url)
    if res.status_code != 200:
        return {"error": "News fetch failed."}

    news_items = res.json()
    results = []
    score_total = 0

    for article in news_items:
        headline = article.get("headline", "")
        if not headline:
            continue
        sentiment_score = TextBlob(headline).sentiment.polarity
        label = (
            "🟢 Positive" if sentiment_score > 0.2 else
            "🔴 Negative" if sentiment_score < -0.2 else
            "🟡 Neutral"
        )
        score_total += sentiment_score
        results.append({
            "headline": headline,
            "sentiment": label,
            "score": round(sentiment_score, 2)
        })

    avg_score = round(score_total / len(results), 2) if results else 0.0
    overall = (
        "🟢 Bullish Mood" if avg_score > 0.2 else
        "🔴 Bearish Mood" if avg_score < -0.2 else
        "🟡 Mixed/Neutral Mood"
    )

    return {
        "symbol": symbol.upper(),
        "average_score": avg_score,
        "overall_sentiment": overall,
        "articles_analyzed": len(results),
        "detailed": results
    }