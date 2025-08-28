# -*- coding: utf-8 -*-
"""
File:        config.py
Description: Constant values, including file paths, to be used for data scraping and analysis.
Author:      Yuseof
Created:     2025-07-24
Modified:    2025-08-22
"""

import os

# for scraper
CHROME_STABLE_VERSION = "116.0.5845.140"
HOUSING_URL = "https://www.redfin.com/city/2832/NY/Buffalo"
# PATH_TO_LISTINGS_OUTPUT = "../data/output/scraped_listings.csv"
MAX_LISTINGS = 400

# for affordability analaysis
PATH_TO_INCOME_DATA = (
    "../data/input/ACSST5Y2023.S1901_2025-07-24T192912/ACSST5Y2023.S1901-Data.csv"
)

# for main.py
# PATH_TO_OUTPUT_ZIP_METRICS = "../data/output/zip_metrics.csv"
# PATH_TO_OUTPUT_HOUSE_METRICS = "../data/output/house_metrics.csv"

# for airtable upload
HOUSE_TABLE_NAME = "House Listings"
ZIP_TABLE_NAME = "Zip Metrics"
BASE_ID = os.getenv("AIRTABLE_BASE_NAME")
AIRTABLE_ACCESS_TOKEN = os.getenv("AIRTABLE_ACCESS_TOKEN")

# for streamlit app
PATH_TO_ZIP_SHAPEFILE = "data/input/zip_shapefile_filtered/zip_shapefile_filtered.shp"

# for geolocation
OPEN_MAPS_API_URL = "https://nominatim.openstreetmap.org/search"

# for zip filtering
CENSUS_ZIP_SHAPEFILE_PATH = "data/input/tl_2022_us_zcta520/tl_2022_us_zcta520.shp"
NY_COUNTY_ZIPS = [
    #Erie County
    14001, 14004, 14006, 14010, 14025, 14026, 14027, 14030,
    14031, 14032, 14033, 14034, 14035, 14037, 14038, 14043,
    14047, 14051, 14052, 14055, 14057, 14059, 14061, 14068,
    14069, 14070, 14072, 14075, 14080, 14081, 14085, 14086,
    14091, 14102, 14110, 14111, 14112, 14127, 14134, 14139,
    14140, 14141, 14145, 14150, 14151, 14169, 14170, 14201,
    14202, 14203, 14204, 14205, 14206, 14207, 14208, 14209,
    14210, 14211, 14212, 14213, 14214, 14215, 14216, 14217,
    14218, 14219, 14220, 14221, 14222, 14223, 14224, 14225,
    14226, 14227, 14228, 14231, 14240, 14280, 14204, 14201,
    14202, 14203,
    
    #Niagara County
    14001, 14008, 14012, 14028, 14067, 14092, 14094, 14095,
    14105, 14107, 14108, 14109, 14120, 14126, 14131, 14132,
    14144, 14172, 14174, 14228, 14301, 14302, 14303, 14304,
    14305,
    
    # Genesee County
    14001, 14005, 14011, 14013, 14020, 14021, 14036, 14040,
    14054, 14056, 14058, 14103, 14105, 14125, 14143, 14416,
    14422, 14428, 14482, 14525, 14557, 14591,
    
    # Orleans County
    14058, 14098, 14103, 14105, 14411, 14416, 14420,
    14429, 14452, 14470, 14476, 14477, 14479, 14571,
    
    #Wyoming County
    14004, 14009, 14011, 14024, 14030, 14037, 14039, 14040,
    14054, 14066, 14082, 14083, 14113, 14130, 14145, 14167,
    14427, 14481, 14525, 14530, 14536, 14549, 14550, 14569,
    14591, 14735  
]
