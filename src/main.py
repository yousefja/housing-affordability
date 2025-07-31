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
import pandas as pd
from util import address_to_lat_lng, upload_to_airtable
from scraper import scrape_listings, process_listing_data
from affordability_analysis import calculate_affordability_metrics
from config import (
    HOUSING_URL,
    MAX_LISTINGS,
    PATH_TO_LISTINGS_OUTPUT,
    PATH_TO_INCOME_DATA,
    PATH_TO_OUTPUT_ZIP_METRICS,
    PATH_TO_OUTPUT_HOUSE_METRICS,
    TABLE_NAME,
    BASE_ID,
    AIRTABLE_ACCESS_TOKEN,
)


def main():

    # scrape, process, and output listing data
    print("Scraping initiated...")
    listing_data = scrape_listings(HOUSING_URL, MAX_LISTINGS)
    process_listing_data(listing_data, PATH_TO_LISTINGS_OUTPUT)
    print("Scraping successful!")

    # calculate affordability
    print("Affordability Calculations initiated...")
    df_listings = pd.read_csv(PATH_TO_LISTINGS_OUTPUT)
    df_income = pd.read_csv(PATH_TO_INCOME_DATA, header=1)
    df_zip_level_analysis, df_house_level_analysis = calculate_affordability_metrics(
        df_listings, df_income
    )
    print("Affordability Calculations successful!")

    print("Performing geolocation...")
    # first ensure parsed address list is of type list and not string, then geolocate
    df_house_level_analysis["Parsed_Address"] = df_house_level_analysis[
        "Parsed_Address"
    ].apply(lambda x: ast.literal_eval(x.strip()))
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
    print("Saving data locally...")
    df_zip_level_analysis.to_csv(PATH_TO_OUTPUT_ZIP_METRICS, index=False)
    df_house_level_analysis.to_csv(PATH_TO_OUTPUT_HOUSE_METRICS, index=False)
    print("Saved successfully!")

    print("Uploading data to Airtable...")
    df_house_level_analysis.drop(columns=["Parsed_Address"], inplace=True)
    upload_to_airtable(
        AIRTABLE_ACCESS_TOKEN, BASE_ID, TABLE_NAME, df_house_level_analysis
    )
    print("Upload Successful!")

    print("Script completed successfully!")


if __name__ == "__main__":
    main()
