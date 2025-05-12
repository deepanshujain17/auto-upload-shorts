import requests
import os
from datetime import datetime

# Replace with your actual GNews API key
# API_KEY = os.getenv("GNEWS_API_KEY")  # or paste it directly as a string
API_KEY = "7491e9afca2a0ca92223977617c2430e"

BASE_URL = "https://gnews.io/api/v4/search"

# Topics and their corresponding queries
topics = {
    "Economy": "indian economy",
    "Government": "modi OR cabinet",
    "Fuel Prices": "petrol diesel price",
    "Stock Market": "nifty OR sensex",
    "Sports": "cricket india",
    "Weather Alerts": "IMD weather alert",
    "Health": "covid OR dengue",
    "Law & Crime": "supreme court"
}

def fetch_topic_news(topic, query):
    params = {
        'q': query,
        'lang': 'en',
        'country': 'in',
        'max': 1,
        'token': API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        if articles:
            article = articles[0]
            return {
                "topic": topic,
                "title": article["title"],
                "url": article["url"],
                "publishedAt": article["publishedAt"]
            }
    except Exception as e:
        print(f"Error fetching {topic}: {str(e)}")
    return None

if __name__ == "__main__":
    print(f"📰 News of the Hour — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    for topic, query in topics.items():
        news = fetch_topic_news(topic, query)
        if news:
            print(f"\n🔹 {news['topic']}")
            print(f"🗞️  {news['title']}")
            print(f"🔗  {news['url']}")
            print(f"🕒  {news['publishedAt']}")
        else:
            print(f"\n🔹 {topic}: No news found.")
