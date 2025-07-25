# -*- coding: utf-8 -*-
"""
File:        config.py
Description: Constant values, including file paths, to be used for data scraping and analysis.
Author:      Yuseof
Created:     2025-07-24
Modified:    2025-07-24
"""

# for scraper
HOUSING_URL = "https://www.redfin.com/city/2832/NY/Buffalo"
PATH_TO_LISTINGS_OUTPUT = "../data/output/scraped_listings.csv"
MAX_LISTINGS = 50

# for affordability analaysis
PATH_TO_INCOME_DATA = "../data/input/ACSST5Y2023.S1901_2025-07-24T192912/ACSST5Y2023.S1901-Data.csv"

# for main.py
PATH_TO_OUTPUT_ZIP_METRICS = "../data/output/zip_metrics.csv"
PATH_TO_OUTPUT_INDIVIDUAL_METRICS = "../data/output/individual_metrics.csv"