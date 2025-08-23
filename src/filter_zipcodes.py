# -*- coding: utf-8 -*-
"""
File:        filter_zipcodes.py
Description: Used to filter census zipcode shapefile (which contains all US zips)
             to only zip codes that might show up in the housing listings. This 
             is done to reduce the size of the shapefile so that it can be 
             uploaded to github and used by streamlit for mapping. 
Author:      Yuseof
Created:     2025-08-22
Modified:    2025-08-22
Usage:       --
"""

import geopandas as gpd
from config import ERIE_COUNTY_ZIPS, CENSUS_ZIP_SHAPEFILE_PATH, PATH_TO_ZIP_SHAPEFILE


def filter_zipcodes():
    
    # load census shapefile
    gdf = gpd.read_file(CENSUS_ZIP_SHAPEFILE_PATH)
    
    # filter for erie county zips
    gdf.GEOID20 = gdf.GEOID20.astype(int)
    gdf = gdf[gdf.GEOID20.isin(ERIE_COUNTY_ZIPS)]
    
    # output filtered shapefile 
    gdf.to_file(PATH_TO_ZIP_SHAPEFILE, driver='ESRI Shapefile')
    

#gdf_zip_analysis = gdf_zip_shapes.merge(
#    df_zip_analysis[["Zipcode"]], how="right", on="Zipcode"
#)

#gdf_zip_analysis.to_file("../data/input/zip_shapefile_filtered.shp", driver='ESRI Shapefile')

# ---------------------------------------------------------------------------------------------------------------


def load_zip_shapes(path=PATH_TO_ZIP_SHAPEFILE):
    
    # load data
    gdf = gpd.read_file(path)
    
    # remove any null geometries
    gdf = gdf[gdf["geometry"].notnull()].copy()
    
    # format zip col
    gdf.rename(columns={'GEOID20':'Zipcode'}, inplace=True)
    gdf["Zipcode"] = gdf["Zipcode"].astype(str)
    
    
    
    make sure to change function for loading gdf to 
    if geoid in cols, change name, otherwise use zipcode 