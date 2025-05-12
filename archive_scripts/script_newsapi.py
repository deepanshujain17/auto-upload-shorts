import os
import time
from datetime import datetime
from newsapi import NewsApiClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NewsFetcher:
    def __init__(self, api_key):
        self.newsapi = NewsApiClient(api_key=api_key)
        self.setup_webdriver()

    def setup_webdriver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def get_top_news(self, country='us', category='general', max_results=5):
        """
        Fetch top headlines from NewsAPI
        """
        try:
            top_headlines = self.newsapi.get_top_headlines(
                q='(India OR Delhi OR Mumbai OR Bangalore) AND (politics OR economy OR society)',
                country='in',
                category=category,
                language='en',
                domains='ndtv.com,indianexpress.com,hindustantimes.com,timesofindia.indiatimes.com'
            )
            return top_headlines['articles'][:max_results]
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            return []

    def capture_article_screenshot(self, article_url, article_title):
        """
        Capture a screenshot of the news article
        """
        try:
            self.driver.get(article_url)
            # Wait for page to load
            time.sleep(3)

            # Set window size for better capture
            self.driver.set_window_size(1200, 800)

            # Create images directory if it doesn't exist
            os.makedirs('images', exist_ok=True)

            # Generate filename based on current date and article title
            date_str = datetime.now().strftime('%Y%m%d')
            safe_title = "".join(x for x in article_title if x.isalnum() or x in (' ', '-', '_'))[:50]
            filename = f'images/news_{date_str}_{safe_title}.png'

            # Capture screenshot
            self.driver.save_screenshot(filename)
            print(f"Screenshot saved as {filename}")
            return filename
        except Exception as e:
            print(f"Error capturing screenshot: {str(e)}")
            return None

    def fetch_and_save_top_news(self):
        """
        Fetch top news and save screenshots
        """
        articles = self.get_top_news()
        captured_images = []

        for article in articles:
            if article['url'] and article['title']:
                image_path = self.capture_article_screenshot(article['url'], article['title'])
                if image_path:
                    captured_images.append({
                        'path': image_path,
                        'title': article['title'],
                        'url': article['url']
                    })

        return captured_images

    def __del__(self):
        """
        Clean up webdriver when done
        """
        if hasattr(self, 'driver'):
            self.driver.quit()

def main():
    # You need to set your NewsAPI key as an environment variable
    api_key = os.getenv('NEWS_API_KEY')
    if not api_key:
        print("Please set the NEWS_API_KEY environment variable")
        return

    news_fetcher = NewsFetcher(api_key)
    captured_images = news_fetcher.fetch_and_save_top_news()

    print("\nCaptured News Articles:")
    for image in captured_images:
        print(f"\nTitle: {image['title']}")
        print(f"Image saved at: {image['path']}")
        print(f"Source URL: {image['url']}")

if __name__ == "__main__":
    main()
