import os
from dotenv import load_dotenv
from archive_scripts.script_newsapi import NewsFetcher

def test_news_fetcher():
    # Load environment variables
    load_dotenv()

    # Get API key from environment variables
    api_key = os.getenv('NEWS_API_KEY')

    if not api_key:
        print("Please set NEWS_API_KEY in your .env file")
        return

    # Initialize NewsFetcher
    news_fetcher = NewsFetcher(api_key)

    try:
        # Test getting top news
        print("Fetching top news...")
        news = news_fetcher.get_top_news(
            country='cn',
            category='technology',
            max_results=3
        )

        # Print the results
        print("\nResults:")
        for item in news:
            print(f"\nTitle: {item['title']}")
            print(f"Description: {item['description']}")
            print("-" * 50)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Always close the webdriver
        news_fetcher.driver.quit()

if __name__ == "__main__":
    test_news_fetcher()
