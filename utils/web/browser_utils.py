"""
Utility module for browser-based operations using Selenium WebDriver.
Provides functionality to render HTML files to images using headless Chrome.
"""

# Standard library imports
import os
from time import sleep
import tempfile
import threading

# Third-party imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from settings.media import BrowserSettings


# Global lock for browser operations
_browser_lock = threading.Lock()
# Singleton pattern for ChromeDriverManager to prevent multiple downloads
_driver_manager = None
_driver_manager_lock = threading.Lock()


def get_chrome_driver_manager():
    """Get or create a singleton ChromeDriverManager instance."""
    global _driver_manager
    with _driver_manager_lock:
        if _driver_manager is None:
            _driver_manager = ChromeDriverManager()
        return _driver_manager


def render_card_to_image(html_file: str, output_image: str) -> None:
    """
    Renders an HTML file to an image using headless Chrome browser.
    Uses a global lock to prevent concurrent ChromeDriver access.

    Args:
        html_file (str): Path to the HTML file to be rendered
        output_image (str): Path where the output image will be saved

    Returns:
        None

    Raises:
        FileNotFoundError: If the HTML file doesn't exist
        WebDriverException: If there's an issue with the browser
        Exception: For other unexpected errors
    """
    driver = None

    # Use a lock to prevent concurrent ChromeDriver operations
    with _browser_lock:
        try:
            if not os.path.exists(html_file):
                raise FileNotFoundError(f"HTML file not found: {html_file}")

            # Configure Chrome options for headless operation
            options = Options()
            options.add_argument('--headless')
            options.add_argument(f'--window-size={BrowserSettings.WINDOW_WIDTH},{BrowserSettings.WINDOW_HEIGHT}')

            # Add unique user data directory
            temp_dir = tempfile.mkdtemp()
            options.add_argument(f'--user-data-dir={temp_dir}')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            # Get the driver path using the singleton manager
            driver_manager = get_chrome_driver_manager()
            driver_path = driver_manager.install()

            # Initialize Chrome WebDriver with the installed driver
            driver = webdriver.Chrome(service=Service(driver_path), options=options)

            # Convert local file path to URL format
            file_path = f"file://{os.path.abspath(html_file)}"

            # Load and render the HTML file
            driver.get(file_path)
            sleep(BrowserSettings.BROWSER_WAIT_TIME)  # Wait for the page to render completely

            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_image), exist_ok=True)

            # Capture screenshot
            driver.save_screenshot(output_image)

        except FileNotFoundError as e:
            print(f"File error: {str(e)}")
            raise
        except WebDriverException as e:
            print(f"Browser error: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception as e:
                    print(f"Error while closing browser: {str(e)}")
