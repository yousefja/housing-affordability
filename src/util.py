# -*- coding: utf-8 -*-
"""
File:        util.py
Description: Provides utility functions to the real estate scraping / housing 
                affordability project.    
Author:      Yuseof
Created:     2025-07-24
Modified:    2025-07-24
Usage:       --
"""

import ast
import traceback
import requests
import numpy as np
import pandas as pd
from pyairtable import Api
from selenium.webdriver.common.by import By
from config import OPEN_MAPS_API_URL


def format_price(price_string):
    """
    Converts price string from scraped data to float, and handles conversion if
    necessary (e.g. 5k -> 5000).

    Parameters
    ----------
    price_string : str

    Returns
    -------
    formatted price as float

    """
    price_string = price_string.strip().replace("$", "")
    if "K" in price_string:
        return float(price_string.replace("K", "")) * 1_000
    elif "M" in price_string:
        return float(price_string.replace("M", "")) * 1_000_000
    return float(price_string.replace(",", ""))


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

        # reset description scraped flag
        description_scraped = True

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
                description_scraped = False

            if description_scraped:
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
            else:
                parsed_listing_data.append(
                    {
                        "Price": price,
                        "Address": address,
                        "Specs": specs,
                        "Description": np.nan,
                        "Listed_By": listed_by,
                        # "URL": link
                    }
                )

        except Exception as e:
            if verbose:
                print("Skipping this listing due to the following error: ", e)
            else:
                continue

    print(f"Scraped {len(parsed_listing_data)} / {len(scraped_listings)} listings")

    return parsed_listing_data


def parse_address(address_str):
    """
    Parse individual address fields from an address string

    NOTE: THIS ONLY WORKS BECAUSE ADDRESSES ARE IN THE SAME FORMAT -- DO NOT USE FOR GENERAL DATE PARSING
    (ex. '157 Roosevelt Ave, Buffalo, NY 14215')
    """

    # Split address into separate parts
    address_str = address_str.split(",")

    try:
        # Parse fields
        postalcode = address_str[-1].split()[1]
        state = address_str[-1].split()[0]
        city = address_str[1]
        county = ""
        street = address_str[0]

    except Exception as e:
        print(f"Unrecognized address format: {address_str}")
        return None

    return [street, city, county, state, postalcode]


def address_to_lat_lng(parsed_address):
    """
    Use either the parsed address to get the corresponding latitude and longitude using
    open maps api

    Parameters
    ----------
    parsed_address : list
        list containing address fields

    Returns
    -------
    list or None
        [latitude, longitude, source] or None if failed.
    """

    params = {
        "street": parsed_address[0].strip(),
        "city": parsed_address[1].strip(),
        "county": parsed_address[2].strip(),
        "state": parsed_address[3].strip(),
        "postalcode": parsed_address[4].strip(),
        "format": "json",
        "limit": 1,
    }

    headers = {"User-Agent": "MyRealEstateApp/1.0 (your_email@example.com)"}

    try:
        response = requests.get(
            OPEN_MAPS_API_URL, params=params, headers=headers, timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data:
            return [data[0]["lat"], data[0]["lon"]]
        else:
            print(f"No results for address: {params}")
            return None
    except Exception:
        print(f"Error retrieving coordinates for adress: {parsed_address}")
        print(traceback.format_exc())
        return None


def upload_to_airtable(access_token, base_id, table_name, df):
    """
    Helper function to upload rows to Airtable. Keeps main.py clean
    """

    """
    access_token = AIRTABLE_ACCESS_TOKEN
    base_id = BASE_ID
    table_name = TABLE_NAME
    df=df_house_level_analysis.copy()
    """

    api = Api(access_token)
    table = api.table(base_id, table_name)

    # get df in format expected by airtable
    df.replace([np.nan], None, inplace=True)
    df["Lat"] = pd.to_numeric(df["Lat"], errors="coerce")
    df["Lng"] = pd.to_numeric(df["Lng"], errors="coerce")
    records = [{"fields": row} for row in df.to_dict(orient="records")]

    # upload to airtable
    _ = table.batch_upsert(records, key_fields=["Price", "Address"])
