import argparse
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from scraper import Scraper
from config import ScraperConfig

def save_temp_results(results, keyword, page_num):
    """Save temporary results for a specific page"""
    # Create temp directory if it doesn't exist
    temp_dir = Path('temp_results')
    temp_dir.mkdir(exist_ok=True)
    
    # Save results for this page
    filename = f"temp_results/{keyword.replace(' ', '_')}_page_{page_num}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Scrape Upwork profiles based on keyword')
    parser.add_argument('keyword', help='Keyword to search for')
    parser.add_argument('num_pages', type=int, help='Number of pages to scrape')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--no-temp', action='store_true', help='Disable temporary saves')
    
    args = parser.parse_args()
    
    # Create config from env variables with CLI headless override
    config = ScraperConfig.from_env()
    config.headless = args.headless
    
    scraper = Scraper(config)
    all_results = []
    
    try:
        result = scraper.scrape_upwork(
            args.keyword, 
            args.num_pages,
            lambda page_results, page_num: None if args.no_temp else save_temp_results(page_results, args.keyword, page_num)
        )
        
        if result:
            print(f"Successfully scraped {len(result)} profiles")
            with open('result.json', 'w') as f:
                json.dump(result, f, indent=2)
        else:
            print("No profiles found")
    finally:
        scraper.stop()

if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    main()
