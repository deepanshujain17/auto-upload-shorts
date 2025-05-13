"""
Utility module for browser-based operations using Selenium WebDriver.
Provides functionality to render HTML files to images using headless Chrome.
"""

# Standard library imports
import os
from time import sleep

# Third-party imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from settings import VideoSettings


def render_card_to_image(html_file: str, output_image: str) -> None:
    """
    Renders an HTML file to an image using headless Chrome browser.

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
    try:
        if not os.path.exists(html_file):
            raise FileNotFoundError(f"HTML file not found: {html_file}")

        # Configure Chrome options for headless operation
        options = Options()
        options.add_argument('--headless')
        options.add_argument(f'--window-size={VideoSettings.WINDOW_WIDTH},{VideoSettings.WINDOW_HEIGHT}')

        # Initialize Chrome WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Convert local file path to URL format
        file_path = f"file://{os.path.abspath(html_file)}"

        # Load and render the HTML file
        driver.get(file_path)
        sleep(VideoSettings.BROWSER_WAIT_TIME)  # Wait for the page to render completely

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
