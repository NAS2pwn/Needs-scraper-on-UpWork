# Upwork Profile Scraper

A powerful tool to extract detailed information from Upwork freelancer profiles, including client testimonials, success metrics, and work history. This scraper helps you understand which freelancers are successfully closing clients and what type of clients they work with.

## Features

- Extract comprehensive profile information:
  - Basic info (name, title, description)
  - Success metrics (job success score, total jobs, hours)
  - Availability and response time
  - Hourly rates and consultation fees
  - Work history with client feedback
  - Skills and expertise
  - Project catalog offerings
  - Client testimonials

- Robust error handling and recovery
- Temporary results saved by page to prevent data loss
- Configurable delays and timeouts
- Headless mode support

## Installation

1. Clone this repository
2. Create and activate a virtual environment
3. Install dependencies

## Configuration

Create a .env file in the project root with the following settings:

- SCRAPER_PAGE_LOAD_TIMEOUT: Seconds to wait for page elements (default: 10)
- SCRAPER_PROFILE_DELAY: Seconds between profile scrapes (default: 2)
- SCRAPER_PAGE_DELAY: Seconds between page scrapes (default: 5)
- CHROME_PATH: Optional path to Chrome binary
- SCRAPER_HEADLESS: Run in headless mode (true/false)

## Usage

Basic command structure:
python main.py "keyword" num_pages

Example to scrape 3 pages of Python developers:
python main.py "python developer" 3

Options:
- keyword: Search term to find relevant profiles
- num_pages: Number of search result pages to scrape
- --headless: Run in headless mode (no visible browser)
- --no-temp: Disable temporary saves

## Output

The scraper generates two types of output:

1. Temporary results (in temp_results/ directory):
   - One JSON file per scraped page
   - Named as keyword_page_N.json
   - Useful for recovering data if scraping is interrupted

2. Final results (result.json):
   - Complete dataset with all scraped profiles
   - Includes all profile details and metrics

## Use Cases

- Market Research: Analyze successful freelancers in your niche
- Client Analysis: Understand what types of clients work with top performers
- Service Development: Identify gaps and opportunities in the market
- Competitive Analysis: Study pricing and service offerings

## Notes

- Respect Upwork's terms of service and rate limits
- Use reasonable delays between requests
- The scraper may need updates if Upwork's website structure changes

## License

MIT License - feel free to use and modify as needed.
