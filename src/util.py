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

import numpy as np
from selenium.webdriver.common.by import By


def format_price(price_string):
    '''
    Converts price string from scraped data to float, and handles conversion if 
    necessary (e.g. 5k -> 5000).
    
    Parameters
    ----------
    price_string : str

    Returns
    -------
    formatted price as float

    '''
    price_string = price_string.strip().replace('$', '')
    if 'K' in price_string:
        return float(price_string.replace('K', '')) * 1_000
    elif 'M' in price_string:
        return float(price_string.replace('M', '')) * 1_000_000
    return float(price_string.replace(',', ''))


def extract_data(scraped_listings):
    '''
    Given all home listings in a HomeCardContainer, parses each listing one
    by one to get all necessary fields

    Parameters
    ----------
    scraped_listings : list of WebElements

    Returns
    -------
    parsed_listing_data : list of dicts
    '''
    
    # extract desired fields from each listing
    parsed_listing_data = []
    for listing in scraped_listings:
        
        # reset description scraped flag
        description_scraped = True
        
        try:
            price = listing.find_element(By.CLASS_NAME, "bp-Homecard__Price--value").text
            specs = listing.find_element(By.CLASS_NAME, "bp-Homecard__Stats").text
            address = listing.find_element(By.CLASS_NAME, "bp-Homecard__Address").text
            listed_by = listing.find_element(By.CLASS_NAME, "bp-Homecard__Attribution").text
            # TODO: URL = listing.find_element(By.CLASS_NAME, "bp-Homecard__Price--value").text
            #TODO: there were also coordinates that are scrapeable
            
            try:
                description = listing.find_element(By.CLASS_NAME, "bp-Homecard__ContentExtension").text
            except Exception as e:
                #TODO: put this in an error logs file, its printing alot of errors to console
                #print(f"Failed while scraping description. Error: {e}")
                description_scraped = False
            
            if description_scraped:
                parsed_listing_data.append({
                    "Price": price,
                    "Address": address,
                    "Specs": specs,
                    "Description": description,
                    "Listed_By": listed_by
                    #"URL": link
                })  
            else:
                parsed_listing_data.append({
                    "Price": price,
                    "Address": address,
                    "Specs": specs,
                    "Description": np.nan,
                    "Listed_By": listed_by
                    #"URL": link
                })
        
        except Exception as e:
            print("Skipping this listing due to the following error: ", e)
         
    print(f"Scraped {len(parsed_listing_data)} / {len(scraped_listings)} total listings")
    
    return parsed_listing_data