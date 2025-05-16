#!/usr/bin/env python
# coding: utf-8

# In[77]:


pip install selenium pandas openpyxl


# In[90]:


import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# In[91]:


# Define the path to the ChromeDriver
chrome_driver_path = r"C:\Users\pooja\olx_scraper_project\chromedriver.exe"


# In[92]:


# Set up Chrome options - NOT using headless mode to avoid detection
chrome_options = Options()
# Removing headless mode as it might be causing detection issues
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Helps avoid detection
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")


# In[93]:


# Add experimental options to avoid detection
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)


# In[94]:


# Create a new Chrome service
service = Service(executable_path=chrome_driver_path)


# In[95]:


# Initialize the driver
driver = webdriver.Chrome(service=service, options=chrome_options)


# In[96]:


# This helps mask selenium's presence
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


# In[97]:


# Lists to store scraped data
titles = []
prices = []
locations = []
dates = []
links = []


# In[99]:


# Number of pages to scrape
num_pages = 5
base_url = "https://www.olx.in/items/q-car-cover"

print("Starting to scrape OLX for car covers...")

try:
    for page in range(1, num_pages + 1):
        url = f"{base_url}?page={page}"
        print(f"Scraping page {page}: {url}")
        
        # Navigate to the page
        driver.get(url)
        
        # Wait longer for the page to load (increased from 10 to 20 seconds)
        wait = WebDriverWait(driver, 20)
        
        # Scroll down to load more content
        for scroll in range(5):
            driver.execute_script("window.scrollBy(0, 500)")
            time.sleep(1)
        
        try:
            # First, wait for the page to load completely
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            print("Page body loaded")
            
            # Try different XPaths as the structure might have changed
            selectors = [
                '//li[@data-aut-id="itemBox"]',
                '//li[contains(@class, "EIR5N")]',
                '//li[contains(@class, "_1DNjI")]',
                '//div[contains(@class, "IKo3_")]',
                '//div[contains(@class, "_2Gr5")]',
                '//a[contains(@class, "_2KuW")]'
            ]
            
            listings = []
            for selector in selectors:
                try:
                    time.sleep(3)  # Give extra time for dynamic content to load
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        print(f"Found elements with selector: {selector}")
                        listings = elements
                        break
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
            
            if not listings:
                # If no selectors worked, try to get the page source to debug
                print("Could not find listings with predefined selectors.")
                print("Taking a screenshot for debugging...")
                screenshot_file = f"olx_page_{page}.png"
                driver.save_screenshot(screenshot_file)
                print(f"Screenshot saved as {screenshot_file}")
                
                # Let's try one more generic approach - find all clickable items
                clickable_items = driver.find_elements(By.TAG_NAME, 'a')
                product_links = [item for item in clickable_items if 'item/' in item.get_attribute('href') or '/p/' in item.get_attribute('href')]
                
                if product_links:
                    print(f"Found {len(product_links)} product links")
                    
                    for link_element in product_links:
                        try:
                            link = link_element.get_attribute('href')
                            
                            # Try to find title, might be within the link or nearby
                            try:
                                title_element = link_element.find_element(By.XPATH, './/span[contains(@class, "title")] | .//div[contains(@class, "title")]')
                                title = title_element.text.strip()
                            except:
                                try:
                                    # Try to get any text in the link that might be a title
                                    title = link_element.text.strip()
                                    if not title:
                                        title = "Title not found"
                                except:
                                    title = "Title not found"
                            
                            # Try to find price nearby
                            try:
                                price_element = link_element.find_element(By.XPATH, './/..//span[contains(@class, "price")] | .//..//div[contains(@class, "price")]')
                                price = price_element.text.strip()
                            except:
                                price = "Price not found"
                            
                            # Try to find location
                            try:
                                location_element = link_element.find_element(By.XPATH, './/..//span[contains(@class, "location")] | .//..//div[contains(@class, "location")]')
                                location = location_element.text.strip()
                            except:
                                location = "Location not found"
                            
                            # Date is usually harder to find reliably
                            date = "Date not available"
                            
                            # Add to our lists
                            titles.append(title)
                            prices.append(price)
                            locations.append(location)
                            dates.append(date)
                            links.append(link)
                            
                            print(f"Scraped from link: {title} - {price}")
                        except Exception as e:
                            print(f"Error processing a product link: {e}")
                
            else:
                print(f"Found {len(listings)} listings on page {page}")
                
                # Extract details from each listing
                for listing in listings:
                    try:
                        # Try different approaches to get the title
                        title = "Title not found"
                        for title_selector in ['.//span[@data-aut-id="itemTitle"]', './/span[contains(@class, "title")]', './/div[contains(@class, "title")]']:
                            try:
                                title_element = listing.find_element(By.XPATH, title_selector)
                                title = title_element.text.strip()
                                if title:
                                    break
                            except:
                                continue
                        
                        # Price - try multiple selectors
                        price = "Price not available"
                        for price_selector in ['.//span[@data-aut-id="itemPrice"]', './/span[contains(@class, "price")]', './/div[contains(@class, "price")]']:
                            try:
                                price_element = listing.find_element(By.XPATH, price_selector)
                                price = price_element.text.strip()
                                if price:
                                    break
                            except:
                                continue
                        
                        # Location - try multiple selectors
                        location = "Location not available"
                        for loc_selector in ['.//span[@data-aut-id="item-location"]', './/span[contains(@class, "location")]', './/div[contains(@class, "location")]']:
                            try:
                                location_element = listing.find_element(By.XPATH, loc_selector)
                                location = location_element.text.strip()
                                if location:
                                    break
                            except:
                                continue
                        
                        # Date - try multiple selectors
                        date = "Date not available"
                        for date_selector in ['.//span[@data-aut-id="item-date"]', './/span[contains(@class, "date")]', './/div[contains(@class, "date")]']:
                            try:
                                date_element = listing.find_element(By.XPATH, date_selector)
                                date = date_element.text.strip()
                                if date:
                                    break
                            except:
                                continue
                        
                        # Link - always try to get this
                        link = "Link not available"
                        try:
                            link_element = listing.find_element(By.XPATH, './/a')
                            link = link_element.get_attribute('href')
                        except:
                            # If direct link not found, the listing itself might be clickable
                            try:
                                link = listing.get_attribute('href')
                            except:
                                pass
                        
                        # Append to lists only if we found a title (basic validation)
                        if title != "Title not found":
                            titles.append(title)
                            prices.append(price)
                            locations.append(location)
                            dates.append(date)
                            links.append(link)
                            
                            print(f"Scraped: {title} - {price}")
                        
                    except Exception as e:
                        print(f"Error scraping a listing: {e}")
                        continue
            
            print(f"Completed page {page}, found {len(titles) - sum([1 for t in titles if 'not found' in t or 'not available' in t])} valid listings so far")
            
        except TimeoutException as e:
            print(f"Timed out waiting for page {page} to load: {e}")
            # Take a screenshot to debug
            driver.save_screenshot(f"timeout_page_{page}.png")
            continue
        except Exception as e:
            print(f"Error processing page {page}: {e}")
            continue
        
        # Wait between pages to avoid being blocked - random delay
        delay = 3 + (page % 3)  # 3-5 seconds
        print(f"Waiting {delay} seconds before next page...")
        time.sleep(delay)
    
    print(f"All pages processed. Found {len(titles)} total items.")
    
    # Check if we found any data
    if len(titles) == 0:
        print("No data was scraped. This could be due to website structure changes or anti-scraping measures.")
        print("Taking a final screenshot for debugging...")
        driver.save_screenshot("final_page.png")
    else:
        # Create a DataFrame
        data = {
            'Title': titles,
            'Price': prices,
            'Location': locations,
            'Date': dates,
            'Link': links
        }
        
        df = pd.DataFrame(data)
        
        # Save to CSV
        output_file = 'olx_car_covers.csv'
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        # Also save to Excel for better formatting
        excel_file = 'olx_car_covers.xlsx'
        df.to_excel(excel_file, index=False)
        
        print(f"Scraping completed! Found {len(titles)} car covers.")
        print(f"Data saved to {output_file} and {excel_file}")

except Exception as e:
    print(f"An error occurred during scraping: {e}")
    driver.save_screenshot("error_screenshot.png")
    print("Screenshot saved as error_screenshot.png")

finally:
    # Always close the driver
    driver.quit()
    print("WebDriver closed.")


# In[ ]:





# In[ ]:





# In[ ]:




