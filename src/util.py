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

import time
import random
import traceback
import requests
import numpy as np
import pandas as pd
from pyairtable import Api
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

    except Exception:
        print(f"Unrecognized address format: {address_str}")
        return None

    return [street, city, county, state, postalcode]


def address_to_lat_lng(parsed_address):
    """
    Use parsed address to get the corresponding latitude and longitude using
    open maps api (i.e. goecoding)

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
        time.sleep(1) # wait 1 sec bw api calls as per openstreemaps policy
        if data:
            return [data[0]["lat"], data[0]["lon"]]
        else:
            print(f"No results for address: {params}")
            return None
    except Exception:
        print(f"Error retrieving coordinates for adress: {parsed_address}")
        print(traceback.format_exc())
        time.sleep(1) # wait 1 sec bw api calls as per openstreemaps policy
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
    
    if not access_token or not base_id:
        raise Exception("Airtable secrets not set")

    api = Api(access_token)
    table = api.table(base_id, table_name)

    # get df in format expected by airtable
    if "House" in table_name:
        df["Lat"] = pd.to_numeric(df["Lat"], errors="coerce")
        df["Lng"] = pd.to_numeric(df["Lng"], errors="coerce")
    df.replace([np.nan], None, inplace=True)
    records = [{"fields": row} for row in df.to_dict(orient="records")]

    # upload to airtable
    _ = table.batch_upsert(records, key_fields=[df.columns[0], df.columns[1]])
