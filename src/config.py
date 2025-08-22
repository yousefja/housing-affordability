# -*- coding: utf-8 -*-
"""
File:        config.py
Description: Constant values, including file paths, to be used for data scraping and analysis.
Author:      Yuseof
Created:     2025-07-24
Modified:    2025-07-24
"""

import os

# for scraper
CHROME_STABLE_VERSION = "116.0.5845.140"
HOUSING_URL = "https://www.redfin.com/city/2832/NY/Buffalo"
PATH_TO_LISTINGS_OUTPUT = "../data/output/scraped_listings.csv"
MAX_LISTINGS = 20

# for affordability analaysis
PATH_TO_INCOME_DATA = (
    "../data/input/ACSST5Y2023.S1901_2025-07-24T192912/ACSST5Y2023.S1901-Data.csv"
)

# for main.py
PATH_TO_OUTPUT_ZIP_METRICS = "../data/output/zip_metrics.csv"
PATH_TO_OUTPUT_HOUSE_METRICS = "../data/output/house_metrics.csv"

# for airtable upload
HOUSE_TABLE_NAME = "House Listings"
ZIP_TABLE_NAME = "Zip Metrics"
BASE_ID = os.getenv("AIRTABLE_BASE_NAME")
AIRTABLE_ACCESS_TOKEN = os.getenv("AIRTABLE_ACCESS_TOKEN")

# for streamlit app
PATH_TO_ZIP_SHAPEFILE = "../data/input/tl_2022_us_zcta520/tl_2022_us_zcta520.shp"
OPEN_MAPS_API_URL = "https://nominatim.openstreetmap.org/search"
