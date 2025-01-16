import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv

load_dotenv()

class Scraper:
    """
    Main class that orchestrates the scraping process.
    Manages the Chrome driver and coordinates different scraping operations.
    """
    def __init__(self, headless=False):
        self.options = uc.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
            
        chrome_path_env = os.getenv('CHROME_PATH')
        if chrome_path_env and len(chrome_path_env) > 0:
            chrome_path = chrome_path_env
        elif os.name == 'posix':  # Linux/Mac
            chrome_path = '/usr/bin/google-chrome'
        else:  # Windows
            chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
            
        if os.path.exists(chrome_path):
            self.options.binary_location = chrome_path
        else:
            raise Exception("Chrome is not installed in the default path. Please install it.")
            
        self.driver = None
        self.page_scraper = None
    
    def start(self):
        """Initializes the Chrome driver and scraping components."""
        self.driver = uc.Chrome(options=self.options)
        self.page_scraper = PageScraper(self.driver)
    
    def stop(self):
        """Stops the Chrome driver and cleans up resources."""
        if self.driver:
            self.driver.quit()
    
    def scrape_upwork(self, keyword):
        """
        Orchestrates the scraping of Upwork search results.
        
        Args:
            keyword (str): The keyword to search for on Upwork
            
        Returns:
            dict: The scraped data from the results page
        """
        if not self.driver:
            self.start()
            
        try:
            base_url = f"https://www.upwork.com/nx/search/talent/?nbs=1&q={keyword}"
            return self.page_scraper.scrape_search_page(base_url, 1)
                
        except Exception as e:
            print(f"Error during scraping: {e}")
            return None

class PageScraper:
    """
    Class responsible for scraping Upwork search result pages.
    Extracts information from the profile list on a given page.
    """
    def __init__(self, driver):
        """
        Args:
            driver: Chrome driver instance to use for scraping
        """
        self.driver = driver
        
    def scrape_search_page(self, base_url, page_number):
        """
        Scrapes an Upwork search results page.
        
        Args:
            base_url (str): The base URL of the search
            page_number (int): The page number to scrape
            
        Returns:
            str: The HTML of the profiles section
        """
        url = f"{base_url}&page={page_number}"
        self.driver.get(url)
        
        profiles_section = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "profiles-list"))
        )
        
        return profiles_section.get_attribute('outerHTML')

class ProfileScraper:
    """
    Class responsible for scraping individual profile pages.
    Will be implemented to extract detailed information from Upwork profiles.
    """
    def __init__(self, driver):
        """
        Args:
            driver: Chrome driver instance to use for scraping
        """
        self.driver = driver
