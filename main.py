import argparse
from scraper import Scraper

def main():
    parser = argparse.ArgumentParser(description='Scrape Upwork profiles based on keyword')
    parser.add_argument('keyword', help='Keyword to search for')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    
    args = parser.parse_args()
    
    scraper = Scraper(headless=args.headless)
    
    try:
        result = scraper.scrape_upwork(args.keyword)
        if result:
            print("Profiles section found!")
            print(result)
        else:
            print("No profiles section found")
    finally:
        scraper.stop()

if __name__ == "__main__":
    main()
