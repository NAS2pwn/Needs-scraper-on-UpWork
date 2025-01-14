import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

class Scraper:
    def __init__(self, headless=False):
        self.options = uc.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
            
        # Définir le chemin vers Chrome selon l'OS
        if os.name == 'posix':  # Linux/Mac
            chrome_path = '/usr/bin/google-chrome'
        else:  # Windows
            chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
            
        if os.path.exists(chrome_path):
            self.options.binary_location = chrome_path
        else:
            raise Exception("Chrome n'est pas installé au chemin par défaut. Veuillez l'installer.")
            
        self.driver = None
    
    def start(self):
        self.driver = uc.Chrome(options=self.options)
    
    def stop(self):
        if self.driver:
            self.driver.quit()
    
    def scrape_upwork(self, keyword):
        if not self.driver:
            self.start()
            
        try:
            url = f"https://www.upwork.com/nx/search/talent/?nbs=1&q={keyword}&page=1"
            self.driver.get(url)
            
            profiles_section = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "profiles-list"))
            )
            
            return profiles_section.get_attribute('outerHTML')
                
        except Exception as e:
            print(f"Error during scraping: {e}")
            return None