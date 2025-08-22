# -*- coding: utf-8 -*-
"""
File:        main.py
Description: Scrape housing listings and calculate affordability metrics.
Author:      Yuseof
Created:     2025-07-24
Modified:    2025-07-24
Usage:       python main.py
"""

import ast
import argparse
import pandas as pd
from util import address_to_lat_lng, upload_to_airtable
from affordability_analysis import calculate_affordability_metrics
from scraper import scrape_listings, process_listing_data, instantiate_driver
from config import (
    HOUSING_URL,
    MAX_LISTINGS,
    PATH_TO_INCOME_DATA,
    #PATH_TO_OUTPUT_ZIP_METRICS,
    #PATH_TO_OUTPUT_HOUSE_METRICS,
    HOUSE_TABLE_NAME,
    ZIP_TABLE_NAME,
    BASE_ID,
    AIRTABLE_ACCESS_TOKEN,
)


def main(headless=True):
    
    # scrape, process, and output listing data
    print("Initiating webdriver...")
    driver = instantiate_driver(headless)
    print("Webdriver created successfully!")

    # scrape, process, and output listing data
    print("Scraping initiated...")
    listing_data = scrape_listings(driver, HOUSING_URL, MAX_LISTINGS)
    df_listings = process_listing_data(listing_data)
    print("Scraping successful!")

    # calculate affordability
    print("Affordability Calculations initiated...")
    df_income = pd.read_csv(PATH_TO_INCOME_DATA, header=1)
    df_zip_level_analysis, df_house_level_analysis = calculate_affordability_metrics(
        df_listings, df_income
    )
    print("Affordability Calculations successful!")

    print("Performing geolocation...")
    df_house_level_analysis["Lat_Lng"] = df_house_level_analysis[
        "Parsed_Address"
    ].apply(lambda x: address_to_lat_lng(x))
    # TODO: fix this later instead of removing
    df_house_level_analysis = df_house_level_analysis[
        df_house_level_analysis["Lat_Lng"].apply(lambda x: isinstance(x, list))
    ]
    df_house_level_analysis["Lat"] = (
        df_house_level_analysis["Lat_Lng"].apply(lambda x: x[0]).copy()
    )
    df_house_level_analysis["Lng"] = (
        df_house_level_analysis["Lat_Lng"].apply(lambda x: x[1]).copy()
    )
    df_house_level_analysis.drop(columns=["Lat_Lng"], inplace=True)
    print("Geolocation successful!")

    # output results
    # print("Saving data locally...")
    # df_zip_level_analysis.to_csv(PATH_TO_OUTPUT_ZIP_METRICS, index=False)
    # df_house_level_analysis.to_csv(PATH_TO_OUTPUT_HOUSE_METRICS, index=False)
    # print("Saved successfully!")

    print("Uploading house-level data to Airtable...")
    df_house_level_analysis.drop(columns=["Parsed_Address"], inplace=True)
    upload_to_airtable(
        AIRTABLE_ACCESS_TOKEN, BASE_ID, HOUSE_TABLE_NAME, df_house_level_analysis
    )
    print("Upload Successful!")
    
    print("Uploading zip-level data to Airtable...")
    upload_to_airtable(
        AIRTABLE_ACCESS_TOKEN, BASE_ID, ZIP_TABLE_NAME, df_zip_level_analysis
    )
    print("Upload Successful!")

    print("Script completed successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", type=bool, default=True)
    args = parser.parse_args()
    main(headless=args.headless)
