from dataclasses import dataclass
import os
from typing import Optional

@dataclass
class ScraperConfig:
    # Timeouts
    page_load_timeout: int = 10  # Timeout for page loads (used in WebDriverWait)
    profile_delay: int = 2       # Delay between profile scrapes
    page_delay: int = 5         # Delay between page scrapes
    
    # Chrome settings
    chrome_path: Optional[str] = None
    headless: bool = False
    
    @classmethod
    def from_env(cls):
        """Creates config from environment variables"""
        return cls(
            page_load_timeout=int(os.getenv('SCRAPER_PAGE_LOAD_TIMEOUT', 10)),
            profile_delay=int(os.getenv('SCRAPER_PROFILE_DELAY', 2)),
            page_delay=int(os.getenv('SCRAPER_PAGE_DELAY', 5)),
            chrome_path=os.getenv('CHROME_PATH'),
            headless=os.getenv('SCRAPER_HEADLESS', '').lower() == 'true'
        ) 