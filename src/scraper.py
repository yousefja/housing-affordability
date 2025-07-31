# -*- coding: utf-8 -*-
"""
File:        scraper.py
Description: Scrapes redfin for property listings in Buffalo, NY
Author:      Yuseof
Created:     2025-07-24
Modified:    2025-07-24
"""

import sys
import time
import pandas as pd
from selenium import webdriver
from util import extract_data, parse_address
from selenium.webdriver.common.by import By


###############
# DATA SCRAPING
###############


def scrape_listings(housing_listings_url, max_listings):

    # instantiate chrome driver and options
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # run without opening browser window
    driver = webdriver.Chrome(options=options)

    # open property listings url
    driver.get(housing_listings_url)

    # pull and parse up to <MAX_LISTINGS> number of homes
    master_listing_data = []
    while len(master_listing_data) < max_listings:

        try:
            # find listings on webpage
            scraped_listings = driver.find_elements(By.CLASS_NAME, "HomeCardContainer")

        except Exception as e:
            print("Error when locating HomeCardContainer")
            print(f"Error message: {e}")
            driver.quit()
            sys.exit(1)

        # process the scraped listings
        parsed_data = extract_data(scraped_listings)

        # add parsed listings to master
        master_listing_data.extend(parsed_data)

        try:
            # click next page button to load more listings
            driver.find_element(By.CLASS_NAME, "PageArrow__direction--next").click()
        except Exception as e:
            print("Error when locating Next Button")
            print(f"Error message: {e}")
            driver.quit()
            sys.exit(1)

        # wait for page to load before scraping next set of listings
        time.sleep(2)

    print(f"Scraped and extracted {len(master_listing_data)} total listings")

    # close browser
    driver.quit()

    return master_listing_data


#################
# POST-PROCESSING
#################


def process_listing_data(listing_data, output_path):

    # convert scraped data to df
    df_listings = pd.DataFrame(listing_data)

    # convert specs column to seperate component columns
    df_listings[["Bedrooms", "Bathrooms", "SqFt"]] = (
        df_listings["Specs"].str.split("\n").tolist()
    )

    # remove 'Listing by" substring
    df_listings["Listed_By"] = df_listings["Listed_By"].apply(
        lambda x: x.split("Listing by")[1].strip()
    )

    # seperate listing agency from phone number
    df_listings[["Listing_Agency", "Agency_Contact"]] = (
        df_listings["Listed_By"].str.split("(").tolist()
    )
    df_listings["Agency_Contact"] = df_listings["Agency_Contact"].apply(
        lambda x: "(" + x
    )

    # get zip code column
    df_listings["Zipcode"] = df_listings["Address"].apply(lambda x: x.split()[-1])

    # get only numeric portion of the Bedroom, Bathroom, and SqFt column values
    df_listings[["Bedrooms", "Bathrooms", "SqFt"]] = x = df_listings[
        ["Bedrooms", "Bathrooms", "SqFt"]
    ].map(lambda x: x.split()[0])

    # parse address for geolocation
    df_listings["Parsed_Address"] = df_listings["Address"].apply(
        lambda x: parse_address(x)
    )

    # reorder columns and remove unneeded columns
    df_listings = df_listings[
        [
            "Price",
            "Address",
            "Zipcode",
            "Description",
            "Bedrooms",
            "Bathrooms",
            "SqFt",
            "Listing_Agency",
            "Agency_Contact",
            "Parsed_Address",
        ]
    ]

    # export scraped data
    df_listings.to_csv(output_path, index=False)
