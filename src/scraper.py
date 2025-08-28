# -*- coding: utf-8 -*-
"""
File:        scraper.py
Description: Scrapes redfin for property listings in Buffalo, NY
Author:      Yuseof
Created:     2025-07-24
Modified:    2025-08-22
"""

import time
import random
import numpy as np
import pandas as pd
from util import parse_address
from selenium.webdriver.common.by import By
from selenium import webdriver
import undetected_chromedriver as uc
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

###############
# DATA SCRAPING
###############


def human_scroll(driver, step=200, delay=0.5, up_chance=0.15, timeout=30):
    """
    Scrolls down smoothly with jitter, occasionally scrolling up.

    step: average px per scroll
    delay: average delay between steps
    up_chance: probability to scroll up instead of down
    timeout: max time (seconds) to keep scrolling
    """
    total_height = driver.execute_script("return document.body.scrollHeight") or 3000
    current = 0
    start_time = time.time()

    while current < total_height:
        # stop if we hit timeout
        if time.time() - start_time > timeout:
            print("⏱️ Timeout reached, stopping scroll.")
            break

        if random.random() < up_chance:
            # Scroll up a bit
            up_step = random.randint(100, 300)
            driver.execute_script(f"window.scrollBy(0, {-up_step});")
            current = max(0, current - up_step)
        else:
            # Smooth scroll down with jitter
            jitter_step = step + random.randint(-50, 50)
            driver.execute_script(f"window.scrollBy(0, {jitter_step});")
            current += jitter_step

        # Randomized delay for more natural behavior
        time.sleep(random.uniform(delay * 0.5, delay * 1.5))


def instantiate_driver(headless=True):
    """
    Handles creation of webdriver

    Parameters
    ----------
    headless : TYPE, optional
        whether or not to run chrome driver in headless mode

    Returns
    -------
    driver : chrome webdriver
    """

    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    )

    # set driver configurations
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")  # headless in container
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=en-US,en;q=0.9")

    # instantiate driver
    """
    try:
        # if running in container, this env variable will be set
        chrome_driver_path = os.getenv("CHROME_PATH")
        #driver = webdriver.Chrome(service=Service(chrome_driver_path), options=options)
        driver = uc.Chrome(options=options)
        print("Driver instantiated from env var path.")
    except Exception:
        # if running locally, auto detect chrome driver
        print("No path found for chrome driver, trying auto detect.")
    """

    ############
    # TODO: Does this work no matter what?
    ############
    driver = uc.Chrome(options=options)

    # apply stealth to driver
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    return driver


def scrape_listings(driver, housing_listings_url, max_listings, timeout=20):
    """
    Scrape property listings in a human-like way to avoid bot detection

    Parameters
    ----------
    driver : ChromeDriver
    housing_listings_url : str
    max_listings : int

    Returns
    -------
    listing_data : dict
    """

    # open property listings url
    driver.get(housing_listings_url)

    # check whether the web page was properly loaded
    print("Current page title:", driver.title)
    print("Current URL:", driver.current_url)

    # human wait before interacting with page
    time.sleep(random.uniform(1.5, 3.0))

    # initiate loop tools
    master_listing_data = []
    page_num = 0

    # pull and parse up to <MAX_LISTINGS> number of homes
    while len(master_listing_data) < max_listings:

        page_num = page_num + 1

        # instantiate human-like movement object (once per page)
        actions = webdriver.ActionChains(driver)

        try:
            # find listings on webpage
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, "HomeCardContainer"))
            )
            scraped_listings = driver.find_elements(By.CLASS_NAME, "HomeCardContainer")

        except Exception as e:
            print("Error when locating HomeCardContainer")
            print(f"Error message: {e}")
            break

        # scrape data from listings
        parsed_data = extract_data(scraped_listings)
        print(
            f"Scraped {len(parsed_data)} / {len(scraped_listings)} listings from page {page_num}"
        )

        # add parsed listings to master
        master_listing_data.extend(parsed_data)

        # gentle scroll to simulate reading
        print("Performing human-like scroll")
        human_scroll(driver)

        # simulate human-like next button click
        try:
            next_btn = driver.find_element(By.CLASS_NAME, "PageArrow__direction--next")
            # scroll to next button before clicking
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                next_btn,
            )
            # wait after scrolling
            time.sleep(random.uniform(0.5, 1.5))

            # click button with human-like behavior
            actions.move_to_element(next_btn).pause(
                random.uniform(0.1, 0.5)
            ).click().perform()

        except Exception as e:
            print(f"No more pages, or error locating next button: {e}")
            break

        # random wait before next scrape
        time.sleep(random.uniform(1.5, 3.5))

    print(f"Scraped and extracted {len(master_listing_data)} total listings")

    # close browser
    driver.quit()

    return master_listing_data


def extract_data(scraped_listings, verbose=False):
    """
    Given all home listings in a HomeCardContainer, parses each listing one
    by one to get all necessary fields

    Parameters
    ----------
    scraped_listings : list of WebElements

    Returns
    -------
    parsed_listing_data : list of dicts
    """

    # extract desired fields from each listing
    parsed_listing_data = []
    for listing in scraped_listings:

        # parse listing attributes
        try:
            price = listing.find_element(
                By.CLASS_NAME, "bp-Homecard__Price--value"
            ).text
            specs = listing.find_element(By.CLASS_NAME, "bp-Homecard__Stats").text
            address = listing.find_element(By.CLASS_NAME, "bp-Homecard__Address").text
            listed_by = listing.find_element(
                By.CLASS_NAME, "bp-Homecard__Attribution"
            ).text
            # TODO: URL = listing.find_element(By.CLASS_NAME, "bp-Homecard__Price--value").text
            # TODO: there were also coordinates that are scrapeable

            try:
                description = listing.find_element(
                    By.CLASS_NAME, "bp-Homecard__ContentExtension"
                ).text
            except Exception as e:
                # TODO: put this in an error logs file, its printing alot of errors to console
                # print(f"Failed while scraping description. Error: {e}")
                description = np.nan

            # add parsed listing data to master list
            parsed_listing_data.append(
                {
                    "Price": price,
                    "Address": address,
                    "Specs": specs,
                    "Description": description,
                    "Listed_By": listed_by,
                    # "URL": link
                }
            )

        except Exception as e:
            if verbose:
                print("Skipping this listing due to the following error: ", e)
            else:
                continue

        # small random delay to mimic human behavior
        time.sleep(random.uniform(0.05, 0.15))

    return parsed_listing_data


#################
# POST-PROCESSING
#################


def process_listing_data(listing_data):

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
    df_listings[["Bedrooms", "Bathrooms", "SqFt"]] = df_listings[
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

    # return scraped data
    return df_listings
