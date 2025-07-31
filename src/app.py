# -*- coding: utf-8 -*-
"""
File:        app.py
Description: Creates a streamlit dashboard using the scraped housing data
Author:      Yuseof
Created:     2025-07-24
Modified:    2025-07-29
Usage:       --
"""

import math
import folium
import numpy as np
import pandas as pd
import pydeck as pdk
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium
from config import (
    PATH_TO_OUTPUT_HOUSE_METRICS,
    PATH_TO_OUTPUT_ZIP_METRICS,
    PATH_TO_ZIP_SHAPEFILE,
)
from datetime import datetime


###########
# LOAD DATA
###########

df_zip_analysis = pd.read_csv(PATH_TO_OUTPUT_ZIP_METRICS)
df_house_analysis = pd.read_csv(PATH_TO_OUTPUT_HOUSE_METRICS)
gdf_zip_shapes = gpd.read_file(PATH_TO_ZIP_SHAPEFILE)

###############
# PREPROCESSING
###############

# round hpi to one decimal
df_zip_analysis["HPI"] = df_zip_analysis["HPI"].apply(lambda x: round(x, 1))

# add commas to prices

# merge zip affordability metrics with zip gdf
df_zip_analysis["Zipcode"] = (
    df_zip_analysis["Zipcode"].astype(str).apply(lambda x: x.strip())
)
gdf_zip_analysis = df_zip_analysis.merge(
    gdf_zip_shapes, how="left", left_on="Zipcode", right_on="GEOID20"
)

# remove any null geometries
gdf_zip_analysis = gdf_zip_analysis[gdf_zip_analysis["geometry"].notnull()].copy()

# TODO: flatten this instead of removing it
# gdf_zip_analysis.drop(19, inplace=True)

# include formatted median income field for map viz
gdf_zip_analysis["Household_Median_Income_Formatted"] = gdf_zip_analysis[
    "Household_Median_Income"
].apply(lambda x: "$" + format(x, ",")[:-2])

# select only relevant columns
gdf_zip_map = gdf_zip_analysis[
    ["Zipcode", "GEOID20", "HPI", "geometry", "Household_Median_Income_Formatted"]
].copy()
geojson_map = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": geom.__geo_interface__,
            "properties": {
                "Zipcode": row.Zipcode,
                "HPI": row.HPI,
                "GEOID20": row.GEOID20,
                "Household_Median_Income_Formatted": row.Household_Median_Income_Formatted,
            },
        }
        for idx, row in gdf_zip_map.iterrows()
        for geom in (
            [row.geometry]
            if row.geometry.geom_type != "MultiPolygon"
            else row.geometry.geoms
        )
    ],
}

##############
# STREAMLIT UI
##############

# ------- HEADER -------

st.set_page_config(page_title="🏠 Housing Affordability Explorer")
st.title("🏠 Housing Affordability Explorer")
st.markdown(
    """
    <div style='text-align: center'>
    Visualizing the gap between affordable home prices and market rates.<br>
    Use the map below to explore affordability and house prices by zipcode. 
    <div>
    """,
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)  # Add some vertical space
st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🗺 Map View", "📊 Charts", "📋 Data Table"])

# st.sidebar.header("Filter Options")
# selected_zip = st.sidebar.selectbox("Choose a ZIP Code", options=df_house_analysis["Zipcode"].unique())
# min_price = st.sidebar.slider("Minimum Price", 0, int(df_house_analysis["Price"].max()), 100000)


# ------- MAP -------

# create folium map
map = folium.Map(location=[42.9159281, -78.7487142], zoom_start=11)

# create custom bins for the gradient colors for the choropleth
custom_bins = [x for x in range(math.ceil(df_zip_analysis.HPI.max()) + 2)]

# choropleth layer
folium.Choropleth(
    geo_data=geojson_map,
    name="Affordability by ZIP",
    data=df_zip_analysis,
    columns=["Zipcode", "HPI"],
    key_on="feature.properties.Zipcode",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="HPI Ratio",
    threshold_scale=custom_bins,
).add_to(map)

# Add tooltips to ZIPs
folium.GeoJson(
    geojson_map,
    name="Zipcode Tooltips",
    tooltip=folium.GeoJsonTooltip(
        fields=["Zipcode", "HPI", "Household_Median_Income_Formatted"],
        aliases=["Zipcode", "HPI", "Median Income"],
    ),
    style_function=lambda x: {"fillOpacity": 0, "color": "transparent"},
).add_to(map)

# Add house pins
for _, row in df_house_analysis.iterrows():

    # color house pins red if house is unaffordable
    color = "red" if row["Affordability_Gap"] < 0 else "green"

    folium.Marker(
        location=[row["Lat"], row["Lng"]],
        tooltip=(
            f"<b>{row['Address']}</b><br>"
            f"<div style='line-height:2'></div>"
            f"<b><i>Price:</i></b> ${int(row['Price']):,}<br>"
            f"<b><i>Affordable Price:</i></b> ${int(row['Affordable_Price']):,}<br>"
            f"<b><i>Affordability Gap:</i></b> ${int(row['Affordability_Gap']):,}"
        ),
        icon=folium.Icon(color=color, icon="home", prefix="fa"),
    ).add_to(map)

# show map in streamlit
with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Homes", len(df_house_analysis))
    col2.metric("Median Price", f"${int(df_house_analysis['Price'].median()):,}")
    col3.metric(
        "Median Affordability Gap",
        f"${int(df_house_analysis['Affordability_Gap'].median()):,}",
    )
    st_folium(map, width=800, height=600)

# st.markdown("<br>", unsafe_allow_html=True)  # Add some vertical space
# st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

# ------- FOOTER -------

with st.expander("ℹ️ About this dashboard"):
    st.markdown(
        """
    Affordability is determined using the median household income of each zipcode (sourced from US Census). 

    - **Affordable Price** = Median Income x 3
    - **Affordability Gap** = House Price - Affordable Price
    - **Red Pins** indicate unaffordable homes.
    - **Green Pins** indicate affordable homes.

    Data is updated weekly.
    """
    )

# Display last refreshed timestamp at top of page
st.markdown(
    f"""
            <div style='text-align: right'>
                🕒 **Last Refreshed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
            """,
    unsafe_allow_html=True,
)

if st.button("🔁 Refresh Now"):
    st.rerun()

# st.markdown("""<hr style="margin-top: 50px;">""", unsafe_allow_html=True)
# st.markdown("Built by Yousef J. | 📫 [Contact](mailto:your@email.com)", unsafe_allow_html=True)


# select zipcode
# zipcodes = sorted(df_zip_analysis.Zipcode.unique())
# selected_zip = st.selectbox("Select Zipcode", zipcodes)

# filter for selected zip
# zip_data = df_zip_analysis[df_zip_analysis.Zipcode == selected_zip]

# st.subheader(f"Affordability Metrics for Zipcode {selected_zip}")

# st.write(zip_data)
#'''
