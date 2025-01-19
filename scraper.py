import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

class Scraper:
    """
    Main class that orchestrates the scraping process.
    Manages the Chrome driver and coordinates different scraping operations.
    """
    def __init__(self, config):
        self.config = config
        self.options = uc.ChromeOptions()
        
        if config.headless:
            self.options.add_argument('--headless')
            # Options nécessaires pour le mode headless
            self.options.add_argument('--no-sandbox')
            self.options.add_argument('--disable-gpu')
            self.options.add_argument('--disable-dev-shm-usage')
            self.options.add_argument('--window-size=1920,1080')
            # User agent Chrome standard
            self.options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36')
            
        if config.chrome_path and os.path.exists(config.chrome_path):
            self.options.binary_location = config.chrome_path
            
        self.driver = None
        self.page_scraper = None
        self.profile_scraper = None
    
    def start(self):
        """Initializes the Chrome driver and scraping components."""
        self.driver = uc.Chrome(options=self.options)
        self.page_scraper = PageScraper(self.driver, self.config)
        self.profile_scraper = ProfileScraper(self.driver, self.config)
    
    def stop(self):
        """Stops the Chrome driver and cleans up resources."""
        if self.driver:
            self.driver.quit()
    
    def scrape_upwork(self, keyword, num_pages, on_page_complete=None):
        """
        Orchestrates the scraping of Upwork search results.
        
        Args:
            keyword (str): The keyword to search for on Upwork
            num_pages (int): Number of pages to scrape
            on_page_complete (callable): Optional callback function called after each page
                with (page_results, page_number) as arguments
                
        Returns:
            list[dict]: List of profile data
        """
        if not self.driver:
            self.start()
            
        profiles_data = []
        base_url = f"https://www.upwork.com/nx/search/talent/?nbs=1&q={keyword}"
        
        for page in range(1, num_pages + 1):
            logging.info(f"[INFO] Scraping page {page}")
            page_results = []
            
            try:
                # Get profile URLs from current page
                profiles = self.page_scraper.extract_profile_links(base_url, page)
                
                # Scrape each profile
                for profile_url in profiles:
                    try:
                        logging.info(f"[INFO] Scraping profile {profile_url}")
                        profile_data = self.profile_scraper.scrape_profile(profile_url)
                        logging.info(f"  - Completed")
                        
                        profile_data['profile_url'] = profile_url
                        profiles_data.append(profile_data)
                        page_results.append(profile_data)
                        
                        # Delay between profiles
                        time.sleep(self.config.profile_delay)
                        
                    except Exception as e:
                        logging.error(f"Error scraping profile {profile_url}: {e}")
                        continue
                
                # Call callback with page results if provided
                if on_page_complete and page_results:
                    on_page_complete(page_results, page)
                
            except Exception as e:
                logging.error(f"Error scraping page {page}: {e}")
                continue
            
            finally:
                # Delay between pages (even if there was an error)
                if page < num_pages:
                    time.sleep(self.config.page_delay)
        
        return profiles_data if profiles_data else None

class PageScraper:
    """
    Class responsible for scraping Upwork search result pages.
    Extracts information from the profile list on a given page.
    """
    def __init__(self, driver, config):
        """
        Args:
            driver: Chrome driver instance to use for scraping
        """
        self.driver = driver
        self.config = config
        
    def extract_profile_links(self, base_url, page_number):
        """
        Extracts profile links from an Upwork search results page.
        
        Args:
            base_url (str): The base URL of the search
            page_number (int): The page number to scrape
            
        Returns:
            list[str]: List of profile URLs found on the page
        """
        url = f"{base_url}&page={page_number}"
        self.driver.get(url)
        
        # Wait with configured timeout
        WebDriverWait(self.driver, self.config.page_load_timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "profiles-list"))
        )
        
        # Find all profile links
        profile_links = self.driver.find_elements(By.CSS_SELECTOR, "a.profile-link")
        
        # Extract and return unique profile URLs
        unique_urls = set()
        for link in profile_links:
            href = link.get_attribute('href')
            if href and '/freelancers/' in href:
                unique_urls.add(href)
                
        return list(unique_urls)

class ProfileScraper:
    """
    Class responsible for scraping individual profile pages.
    Extracts detailed information from Upwork freelancer profiles.
    """
    def __init__(self, driver, config):
        """
        Args:
            driver: Chrome driver instance to use for scraping
        """
        self.driver = driver
        self.config = config

    def scrape_profile(self, profile_url):
        """
        Main method to scrape all information from a profile page.
        
        Args:
            profile_url (str): URL of the profile to scrape
            
        Returns:
            dict: All extracted profile information
        """
        self.driver.get(profile_url)
        
        # Wait with configured timeout
        WebDriverWait(self.driver, self.config.page_load_timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "profile-container"))
        )

        # Get all profile data
        profile_data = {
            'basic_info': self._extract_basic_info(),
            'availability': self._extract_availability_info(),
            'offer_details': self._extract_offer_details(),
            'consultation_rate': self._extract_consultation_rate(),
            'work_history': self._extract_work_history(),
            'skills': self._extract_skills(),
            'project_catalog': self._extract_project_catalog(),
            'testimonials': self._extract_testimonials()
        }
        
        return profile_data

    def _extract_basic_info(self):
        """
        Extracts basic profile information.
        """
        try:
            # Get name
            name = self.driver.find_element(
                By.CSS_SELECTOR, 
                "h2[itemprop='name']"
            ).text.strip()
            
            # Get title (specialized in...)
            title = self.driver.find_element(
                By.CSS_SELECTOR,
                "div.d-flex.align-items-center.justify-space-between h2.mb-0"
            ).text.strip()
            
            # Get description (the long text)
            description = self.driver.find_element(
                By.CSS_SELECTOR,
                "div.text-body.text-light-on-inverse span.text-pre-line"
            ).text.strip()
            
            # Get job success score with fallback selectors
            job_success = None
            job_success_selectors = [
                "div.is-animated span[data-v-1a549d04]:first-child",
                "span[data-test='job-success-score'] span",
                "div.up-skill-badge span:first-child"
            ]
            
            for selector in job_success_selectors:
                try:
                    job_success_text = self.driver.find_element(
                        By.CSS_SELECTOR, 
                        selector
                    ).text.strip()
                    job_success = float(job_success_text.replace('%', ''))
                    if job_success:
                        break
                except:
                    continue
            
            # Get total jobs and hours with fallback selectors
            total_jobs = None
            total_hours = None
            stats_selectors = [
                "div.stat-amount.h5 span",  # New version
                "div.flex-grow-1 h4",       # Old version
                "[class*='stat'] span:first-child"  # Generic fallback
            ]
            
            for selector in stats_selectors:
                try:
                    stats = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(stats) >= 2:
                        total_jobs = int(stats[0].text)
                        total_hours = int(stats[1].text)
                        break
                except:
                    continue
            
            return {
                'name': name,
                'title': title, 
                'description': description,
                'job_success': job_success,
                'total_jobs': total_jobs,
                'total_hours': total_hours
            }
        except Exception as e:
            print(f"Error extracting basic info: {e}")
            return {
                'name': None,
                'title': None,
                'description': None,
                'job_success': None,
                'total_jobs': None,
                'total_hours': None
            }

    def _extract_offer_details(self):
        """
        Extracts information about the freelancer's offer.
        
        Returns:
            dict: Offer details including:
                - hourly_rate: Hourly rate as float
                - title: Profile title/headline
                - description: Full profile description
        """
        try:
            # Extract hourly rate
            rate_element = self.driver.find_element(
                By.CSS_SELECTOR, 
                "h3.h5.nowrap span"
            )
            hourly_rate = float(rate_element.text.strip().replace('$', '').replace('/hr', ''))
            
            # Extract title
            title = self.driver.find_element(
                By.CSS_SELECTOR, 
                "h2.mb-0.pt-lg-2x.h4"
            ).text.strip()
            
            # Extract description
            description = self.driver.find_element(
                By.CSS_SELECTOR, 
                "div.text-body.text-light-on-inverse span.text-pre-line"
            ).text.strip()
            
            return {
                'hourly_rate': hourly_rate,
                'title': title,
                'description': description
            }
        except:
            return {
                'hourly_rate': None,
                'title': None,
                'description': None
            }

    def _extract_consultation_rate(self):
        """
        Extracts the consultation rate if available.
        
        Returns:
            dict: Consultation information containing:
                - rate: Rate as float
                - duration: Duration in minutes
                - type: Type of consultation (e.g., 'Zoom meeting')
        """
        try:
            rate_text = self.driver.find_element(
                By.CSS_SELECTOR, 
                "p.m-0.text-light-on-muted"
            ).text.strip()
            
            # Parse "$30 per 30 min Zoom meeting"
            parts = rate_text.split()
            rate = float(parts[0].replace('$', ''))
            duration = int(parts[2])
            type = ' '.join(parts[4:])  # "Zoom meeting"
            
            return {
                'rate': rate,
                'duration': duration,
                'type': type
            }
        except:
            return {
                'rate': None,
                'duration': None,
                'type': None
            }

    def _extract_work_history(self):
        """
        Extracts the work history including ratings, job titles, and client feedback.
        
        Returns:
            list[dict]: List of past jobs with their details containing:
                - title: Job title
                - rating: Rating as float
                - dates: Dict with start and end dates
                - feedback: Client feedback text
        """
        jobs = []
        
        try:
            # Find all job items
            job_items = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "div.assignments-item.assignments-item-hoverable"
            )
            
            for job in job_items:
                try:
                    # Extract job title
                    title = job.find_element(
                        By.CSS_SELECTOR, 
                        "h5.align-items-center.mb-2x"
                    ).text.strip()
                    
                    # Extract rating
                    try:
                        rating = float(job.find_element(
                            By.CSS_SELECTOR, 
                            "strong.text-body-sm"
                        ).text.strip())
                    except:
                        rating = None
                    
                    # Extract dates
                    try:
                        dates_text = job.find_element(
                            By.CSS_SELECTOR, 
                            "span.text-base-sm.text-stone"
                        ).text.strip()
                        # Split "Feb 18, 2023 - Feb 21, 2023"
                        start_date, end_date = dates_text.split(" - ")
                    except:
                        start_date = None
                        end_date = None
                    
                    # Extract feedback
                    try:
                        feedback = job.find_element(
                            By.CSS_SELECTOR, 
                            "span.air3-truncation span[tabindex='-1'] span[id^='air3-truncation-']"
                        ).text.strip()
                    except:
                        feedback = None
                    
                    jobs.append({
                        'title': title,
                        'rating': rating,
                        'dates': {
                            'start': start_date,
                            'end': end_date
                        },
                        'feedback': feedback
                    })
                    
                except Exception as e:
                    print(f"Error extracting job details: {e}")
                    continue
                
            return jobs
            
        except Exception as e:
            print(f"Error extracting work history: {e}")
            return []

    def _extract_availability_info(self):
        """
        Extracts availability information.
        """
        try:
            # Find hours per week using text content directly
            hours_elements = self.driver.find_elements(
                By.XPATH,
                "//*[contains(text(), 'hrs/week')]"
            )
            hours_section = next((el.text.strip() for el in hours_elements if 'hrs/week' in el.text), None)
            
            # Get response time if available (using text content)
            try:
                response_elements = self.driver.find_elements(
                    By.XPATH,
                    "//*[contains(text(), 'response time')]"
                )
                response_time = next((el.text.strip() for el in response_elements if 'response time' in el.text), None)
            except:
                response_time = None
            
            # Check if open to contract to hire (using text content)
            try:
                c2h_elements = self.driver.find_elements(
                    By.XPATH,
                    "//*[contains(text(), 'contract to hire')]"
                )
                contract_to_hire = any('Open to contract to hire' in el.text for el in c2h_elements)
            except:
                contract_to_hire = False
            
            return {
                'hours_per_week': hours_section,
                'response_time': response_time,
                'contract_to_hire': contract_to_hire
            }
        except Exception as e:
            print(f"Error extracting availability info: {e}")
            return {
                'hours_per_week': None,
                'response_time': None,
                'contract_to_hire': False
            }

    def _extract_skills(self):
        """
        Extracts skills and expertise, both categorized and uncategorized.
        
        Returns:
            dict: Skills information containing:
                - categories: Dict of skill categories with their skills
                - other_skills: List of uncategorized skills
        """
        skills = {
            'categories': {},
            'other_skills': []
        }
        
        try:
            # Get all skill categories
            categories = self.driver.find_elements(
                By.CSS_SELECTOR,
                "[data-v-6bddd6fe]"
            )
            
            for category in categories:
                try:
                    category_name = category.find_element(
                        By.CSS_SELECTOR,
                        "h3.skills-group-list-title"
                    ).text.strip()
                    
                    category_skills = [
                        skill.text.strip() for skill in category.find_elements(
                            By.CSS_SELECTOR,
                            "span.skill-name"
                        )
                    ]
                    
                    if category_skills:
                        skills['categories'][category_name] = category_skills
                except:
                    continue
            
            # Get other skills
            try:
                other_skills_section = self.driver.find_element(
                    By.CSS_SELECTOR,
                    "[data-v-3dfc0d73]"
                )
                skills['other_skills'] = [
                    skill.text.strip() for skill in other_skills_section.find_elements(
                        By.CSS_SELECTOR,
                        "span.skill-name"
                    )
                ]
            except:
                pass
            
            return skills
            
        except Exception as e:
            print(f"Error extracting skills: {e}")
            return {
                'categories': {},
                'other_skills': []
            }

    def _extract_project_catalog(self):
        """
        Extracts project catalog offerings with their prices and delivery times.
        
        Returns:
            list[dict]: List of projects containing:
                - title: Project title
                - price: Dict with amount and type (fixed/from)
                - delivery: Dict with duration and unit
        """
        projects = []
        
        try:
            # Find all project items
            project_items = self.driver.find_elements(
                By.CSS_SELECTOR,
                "section[data-v-404f92c0] div.pp-hover"
            )
            
            for project in project_items:
                try:
                    # Extract title
                    title = project.find_element(
                        By.CSS_SELECTOR,
                        "h4.mb-0.mt-0"
                    ).text.strip()
                    
                    # Extract price
                    price_text = project.find_element(
                        By.CSS_SELECTOR,
                        "div.air3-token.product-price-start"
                    ).text.strip()
                    
                    # Parse "From $50" or "$50" or "$6,000"
                    is_from = price_text.startswith('From')
                    amount_str = price_text.replace('From ', '').replace('$', '').replace(',', '')
                    amount = float(amount_str)
                    
                    # Extract delivery time
                    delivery_text = project.find_element(
                        By.CSS_SELECTOR,
                        "div.delivery-days"
                    ).text.strip()
                    
                    # Parse "1 day delivery"
                    delivery_parts = delivery_text.split()
                    duration = int(delivery_parts[0])
                    unit = delivery_parts[1]  # "day" or "days"
                    
                    projects.append({
                        'title': title,
                        'price': {
                            'amount': amount,
                            'type': 'from' if is_from else 'fixed'
                        },
                        'delivery': {
                            'duration': duration,
                            'unit': unit
                        }
                    })
                    
                except Exception as e:
                    print(f"Error extracting project details: {e}")
                    continue
                
            return projects
                
        except Exception as e:
            print(f"Error extracting project catalog: {e}")
            return []

    def _extract_testimonials(self):
        """
        Extracts client testimonials with author info and dates.
        
        Returns:
            list[dict]: List of testimonials containing:
                - text: Testimonial content
                - author: Dict with name and position/title
                - date: Date of testimonial
                - verified: Boolean indicating if testimonial is verified
        """
        testimonials = []
        
        try:
            # Find all testimonial items
            testimonial_items = self.driver.find_elements(
                By.CSS_SELECTOR,
                "section.testimonial-item"
            )
            
            for item in testimonial_items:
                try:
                    # Extract testimonial text
                    text = item.find_element(
                        By.CSS_SELECTOR,
                        "p.mb-6x"
                    ).text.strip()
                    
                    # Extract author info
                    author_info = item.find_element(
                        By.CSS_SELECTOR,
                        "p.text-base"
                    )
                    
                    # Get author name and position
                    author_text = author_info.find_element(
                        By.CSS_SELECTOR,
                        "strong"
                    ).text.strip()
                    
                    # Split "Alonso C. | CEO" into name and position
                    if '|' in author_text:
                        author_name, author_position = [
                            part.strip() for part in author_text.split('|')
                        ]
                    else:
                        author_name = author_text
                        author_position = None
                    
                    # Get date
                    date = author_info.find_element(
                        By.CSS_SELECTOR,
                        "span.vertical-align-middle.pr-3x"
                    ).text.strip()
                    
                    # Check if verified
                    try:
                        item.find_element(
                            By.CSS_SELECTOR,
                            "span.text-light-on-inverse"
                        )
                        verified = True
                    except:
                        verified = False
                    
                    testimonials.append({
                        'text': text,
                        'author': {
                            'name': author_name,
                            'position': author_position
                        },
                        'date': date,
                        'verified': verified
                    })
                    
                except Exception as e:
                    print(f"Error extracting testimonial details: {e}")
                    continue
                
            return testimonials
            
        except Exception as e:
            print(f"Error extracting testimonials: {e}")
            return []
