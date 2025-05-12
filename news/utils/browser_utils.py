from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import os

def render_card_to_image(html_file, output_image):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--window-size=1000,800')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(f"file://{os.path.abspath(html_file)}")
    sleep(2)  # allow time for render
    driver.save_screenshot(output_image)
    driver.quit()
