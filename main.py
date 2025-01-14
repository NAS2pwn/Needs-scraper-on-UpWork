import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_upwork(keyword):
    options = uc.ChromeOptions()
    # Décommente la ligne suivante pour le mode headless
    # options.add_argument('--headless')
    
    driver = uc.Chrome(options=options)
    
    try:
        url = f"https://www.upwork.com/nx/search/talent/?nbs=1&q={keyword}&page=1"
        driver.get(url)
        
        profiles_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "profiles-list"))
        )
        
        html_content = profiles_section.get_attribute('outerHTML')
        return html_content
            
    except Exception as e:
        print(f"Error during scraping: {e}")
        return None
        
    finally:
        driver.quit()

if __name__ == "__main__":
    result = scrape_upwork("chatbot")
    if result:
        print("Profiles section found!")
        print(result)
    else:
        print("No profiles section found")
