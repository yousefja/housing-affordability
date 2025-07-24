# -*- coding: utf-8 -*-

"""
File:        scraper.py
Description: Scrapes redfin for property listings in Buffalo, NY
Author:      Yuseof
Created:     2025-07-24
Modified:    2025-07-24
Usage:       python scraper.py
"""

import time
import numpy as np
import pandas as pd
from selenium import webdriver
from util import extract_data
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# constants
PATH_TO_CITY_LISTINGS = "https://www.redfin.com/city/2832/NY/Buffalo"
PATH_TO_LISTINGS_OUTPUT = "../output/scraped_listings.csv"
MAX_LISTINGS = 300

###############
# DATA SCRAPING
###############

# instantiate chrome driver and options
options = webdriver.ChromeOptions()
#options.add_argument("--headless")  # run without opening browser window
driver = webdriver.Chrome(options=options)

# open property listings url
driver.get(PATH_TO_CITY_LISTINGS)

# pull and parse up to <MAX_LISTINGS> number of homes
master_listing_data = []
while len(master_listing_data) <MAX_LISTINGS:
        
    # find listings on webpage
    scraped_listings = driver.find_elements(By.CLASS_NAME, "HomeCardContainer")
    
    # process the scraped listings
    parsed_data = extract_data(scraped_listings)
    
    # add parsed listings to master 
    master_listing_data.extend(parsed_data)
        
    # click next page button to load more listings
    driver.find_element(By.CLASS_NAME
                        , "PageArrow__direction--next").click()
    
    # wait for page to load before scraping next set of listings
    time.sleep(2)
    
print(f"Scraped and extracted {len(master_listing_data)} total listings")

#################
# POST-PROCESSING
#################
     
# convert scraped data to df
df_listings = pd.DataFrame(master_listing_data)

# convert specs column to seperate component columns
df_listings[['Bedrooms', 'Bathrooms', 'SqFt']] = df_listings['Specs'].str.split('\n').tolist()

# remove 'Listing by" substring
df_listings['Listed_By'] = df_listings['Listed_By'].apply(lambda x: x.split("Listing by")[1].strip())

# seperate listing agency from phone number
df_listings[['Listing_Agency', 'Agency_Contact']] = df_listings['Listed_By'].str.split('(').tolist()
df_listings['Agency_Contact'] = df_listings['Agency_Contact'].apply(lambda x: "(" + x)

# get zip code column
df_listings['Zipcode'] = df_listings['Address'].apply(lambda x: x.split()[-1])

# reorder columns and remove unneeded columns
df_listings = df_listings[['Price',
                            'Address',
                            'Zipcode',
                            'Description',
                            'Bedrooms',
                            'Bathrooms',
                            'SqFt',
                            'Listing_Agency',
                            'Agency_Contact'
                            ]]

# export scraped data
df_listings.to_csv(PATH_TO_LISTINGS_OUTPUT, index=False)

# close browser
driver.quit()