# -*- coding: utf-8 -*-
"""
File:        main.py
Description: Scrape housing listings and calculate affordability metrics.
Author:      Yuseof
Created:     2025-07-24
Modified:    2025-07-24
Usage:       python main.py
"""

import pandas as pd
from scraper import scrape_listings, process_listing_data
from affordability_analysis import calculate_affordability_metrics
from config import HOUSING_URL, MAX_LISTINGS, PATH_TO_LISTINGS_OUTPUT, PATH_TO_INCOME_DATA, PATH_TO_OUTPUT_ZIP_METRICS, PATH_TO_OUTPUT_INDIVIDUAL_METRICS


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
    df_zip_level_analysis, df_individual_level_analysis = calculate_affordability_metrics(df_listings, df_income)
    print("Affordability Calculations successful!")
    
    # output results
    print("Saving data...")
    df_zip_level_analysis.to_csv(PATH_TO_OUTPUT_ZIP_METRICS, index=False)
    df_individual_level_analysis.to_csv(PATH_TO_OUTPUT_INDIVIDUAL_METRICS, index=False)
    print("Script completed successfully!")
    

if __name__ == "__main__":
    main() 