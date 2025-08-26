# -*- coding: utf-8 -*-
"""
File:        app.py
Description: Creates a streamlit dashboard using the scraped housing data
Author:      Yuseof
Created:     2025-07-24
Modified:    2025-08-22
Usage:       --
"""

import math
import folium
import numpy as np
import pandas as pd
import geopandas as gpd
import streamlit as st
from pyairtable import Api
from streamlit_folium import st_folium
from config import (
    PATH_TO_ZIP_SHAPEFILE,
    HOUSE_TABLE_NAME,
    ZIP_TABLE_NAME,
    BASE_ID,
    AIRTABLE_ACCESS_TOKEN

)

st.set_page_config(page_title="🏠 Housing Affordability Explorer")

#####################
# HELPERS AND CACHING
#####################

# NOTE: caching prevents flickering in streamlit UI since results are stored rather than 
# code rerunning / resources realoading every time


@st.cache_data
def load_zip_analysis(): 
    
    # load data
    api = Api(AIRTABLE_ACCESS_TOKEN)
    table = api.table(BASE_ID, ZIP_TABLE_NAME)
    rows = table.all()
    df = pd.json_normalize(r["fields"] for r in rows)
    
    # zip as str for join
    df["Zipcode"] = df["Zipcode"].astype(str).apply(lambda x: x.strip())
    
    # round PIR to one decimal
    df["PIR"] = df["PIR"].apply(lambda x: round(x, 1))
    
    # include formatted median income field for map viz
    df["Household_Median_Income_Formatted"] = df[
        "Household_Median_Income"
    ].apply(lambda x: "$" + format(x, ","))
    
    return df


@st.cache_data
def load_house_listings():
    
    # load data
    api = Api(AIRTABLE_ACCESS_TOKEN)
    table = api.table(BASE_ID, HOUSE_TABLE_NAME)
    rows = table.all()
    df = pd.json_normalize(r["fields"] for r in rows)
    
    # fields for mapping
    df['Affordable_Color'] = np.where(df['Affordability_Gap'] < 0, "red", "green")
    df['Is_Affordable'] = np.where(df['Affordability_Gap'] < 0, False, True)

    return df
    

@st.cache_data
def load_zip_shapes(path=PATH_TO_ZIP_SHAPEFILE):
    
    # load data
    gdf = gpd.read_file(path)
    
    # remove any null geometries
    gdf = gdf[gdf["geometry"].notnull()].copy()
    
    # format zip col
    gdf.rename(columns={'GEOID20':'Zipcode'}, inplace=True)
    gdf["Zipcode"] = gdf["Zipcode"].astype(str)
    
    return gdf

    
###########
# LOAD DATA
###########

df_zip_analysis = load_zip_analysis()
df_house_analysis = load_house_listings()
gdf_zip_shapes = load_zip_shapes()

###############
# PREPROCESSING
###############

# TODO: figure out how to cache this so UI runs smoother
#@st.cache_date
#def preprocess_dfs(df_zip_analysis, ):
    
# merge zip affordability metrics with zip gdf
gdf_zip_analysis = df_zip_analysis.merge(
    gdf_zip_shapes, how="left", on="Zipcode"
)

# select only relevant columns
gdf_zip_map = gdf_zip_analysis[
    ["Zipcode", "PIR", "geometry", "Household_Median_Income_Formatted"]
].copy()

geojson_map = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": geom.__geo_interface__,
            "properties": {
                "Zipcode": row.Zipcode,
                "PIR": row.PIR,
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

st.title("🏠 Housing Affordability Explorer")
st.markdown(
    """
    <div style='text-align: center'>
    Visualizing the gap between affordable home prices and current market rates.<br>
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

# ------- FILTERS -------

st.sidebar.header("Filters")

# space
st.sidebar.write("")

# house type filters
show_affordable = st.sidebar.checkbox("Show Affordable Homes", value=True)
show_unaffordable = st.sidebar.checkbox("Show Unaffordable Homes", value=True)

# space
st.sidebar.write("")

# house price filter
min_price, max_price = int(df_house_analysis.Price.min()), int(df_house_analysis.Price.max())
price_range = st.sidebar.slider("Price Range",
                                min_value=min_price, 
                                max_value=max_price,
                                value=(min_price, max_price), step=10000
                                )
# space
st.sidebar.write("")

# zip filter
zip_options = sorted(df_zip_analysis['Zipcode'].unique().tolist())
selected_zips = st.sidebar.multiselect("Select Zipcode(s)", zip_options)

# ------- APPLY FILTERS -------

df_houses_filtered = df_house_analysis.copy()

# price filter
df_houses_filtered = df_houses_filtered[
    (df_houses_filtered['Price'] >= price_range[0]) &
    (df_houses_filtered['Price'] <= price_range[1])
]

# zip filter
if selected_zips:
    df_houses_filtered = df_houses_filtered[df_houses_filtered.Zipcode.isin(int(selected_zips))]

if show_unaffordable == False:
    df_houses_filtered = df_houses_filtered[df_houses_filtered.Is_Affordable == True]
    
if show_affordable == False:
    df_houses_filtered = df_houses_filtered[df_houses_filtered.Is_Affordable == False]
    
# --------- MAP ---------

# create folium map
map = folium.Map(location=[42.9159281, -78.7487142], zoom_start=11)

# create custom bins for the gradient colors for the choropleth
custom_bins = [x for x in range(math.ceil(df_zip_analysis.PIR.max()) + 2)]

# choropleth layer
folium.Choropleth(
    geo_data=geojson_map,
    name="Affordability by ZIP",
    data=df_zip_analysis,
    columns=["Zipcode", "PIR"],
    key_on="feature.properties.Zipcode",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Price to Income Ratio (Affordability Measure)",
    threshold_scale=custom_bins,
).add_to(map)

# Add tooltips to ZIPs
folium.GeoJson(
    geojson_map,
    name="Zipcode Tooltips",
    tooltip=folium.GeoJsonTooltip(
        fields=["Zipcode", "PIR", "Household_Median_Income_Formatted"],
        aliases=["Zipcode", "PIR", "Median Income"],
    ),
    style_function=lambda x: {"fillOpacity": 0, "color": "transparent"},
).add_to(map)

# Add house pins
for _, row in df_houses_filtered.iterrows():

   # only show if filter toggle is set accordingly
   #if (row.Is_Affordable and show_affordable) or (not row.Is_Affordable and show_unaffordable):

    folium.Marker(
        location=[row["Lat"], row["Lng"]],
        tooltip=(
            f"<b>{row['Address']}</b><br>"
            f"<div style='line-height:2'></div>"
            f"<b><i>Price:</i></b> ${int(row['Price']):,}<br>"
            f"<b><i>Affordable Price:</i></b> ${int(row['Affordable_Price']):,}<br>"
            f"<b><i>Affordability Gap:</i></b> ${int(row['Affordability_Gap']):,}"
        ),
        icon=folium.Icon(color=row['Affordable_Color'], icon="home", prefix="fa"),
    ).add_to(map)

# show map in streamlit
with tab1:
        
    # kpi columns
    col1, col2, col3, col4 = st.columns([1.5,2,2,1])
    col1.metric("Total Homes", len(df_houses_filtered))
    col2.metric("Median Home Price", f"${int(df_houses_filtered['Price'].median()):,}")
    col3.metric(
        "Median Affordability Gap",
        f"${int(df_houses_filtered['Affordability_Gap'].median()):,}",
    )
    col4.metric("% Affordable",
                f"{math.trunc((len(df_houses_filtered[df_houses_filtered.Affordability_Gap == 0]) / len(df_houses_filtered)) * 100)}%")
    
    
    # map and summary cards placed in same container to avoid massive spacing between them
    map_container = st.container()
    
    with map_container:
    
        st_folium(map, width=800, height=600)
            
        # summary cols
        most_aff, least_aff = st.columns(2)
        
        with most_aff:
            
            # least affordable neighborhoods (Recc: These neighborhoods Need pricing support)
            df_most_aff = df_zip_analysis.sort_values('PIR').head(3)[['Zipcode', 'PIR']]
            
            insights_html = """
            <div style="
                padding:15px;
                background-color:#007506;
                border-radius:10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                color: white;
            ">
                <h4 style="margin-top:0;">⬆️ Most Affordable Areas</h4>
                <ul style="padding-left:20px; margin:0;">
            """
        
            for _, row in df_most_aff.iterrows():
                insights_html += f"<li><b>Zip {row.Zipcode}</b> — Price Income Ratio = {row.PIR:,.0f}</li>"
            
            insights_html += """
                </ul>
            </div>
            """
            
            st.markdown(insights_html, unsafe_allow_html=True)
            
        with least_aff:
            
            # least affordable neighborhoods (Recc: These neighborhoods Need pricing support)
            df_least_aff = df_zip_analysis.sort_values('PIR').tail(3)[['Zipcode', 'PIR']]
            
            insights_html = """
            <div style="
                padding:15px;
                background-color:#B30000;
                border-radius:10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                color: white;
            ">
                <h4 style="margin-top:0;">⬇️ Least Affordable Areas</h4>
                <ul style="padding-left:20px; margin:0;">
            """
        
            for _, row in df_least_aff.iterrows():
                insights_html += f"<li><b>Zip {row.Zipcode}</b> — Price Income Ratio = {row.PIR:,.0f}</li>"
        
            insights_html += """
                </ul>
            </div>
            """
            
            st.markdown(insights_html, unsafe_allow_html=True)
        
        # padding under summary cards
        st.markdown('</div>', unsafe_allow_html=True)

# st.markdown("<br>", unsafe_allow_html=True)  # Add some vertical space
# st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

# ------- FOOTER -------

with st.expander("ℹ️ About this dashboard"):
    st.markdown(
        """
    Affordability is determined using the median household income of each zipcode (sourced from US Census). 

    - **Affordable Price** = Median Income x 3
    - **Affordability Gap** = House Price - Affordable Price
    - **PIR** (Price to Income Ratio) = Median House Price / Median Income
    - **Red Pins** indicate unaffordable homes.
    - **Green Pins** indicate affordable homes.

    Data is updated weekly.
    """
    )
    
# Display last refreshed timestamp at top of page
last_updated = df_house_analysis['Created'].iloc[0][:-5]
last_updated  = last_updated.replace("T", " ")
st.markdown(
    f"""
            <div style='text-align: right'>
                🕒 **Data Last Updated:** {last_updated}
            </div>
            """,
    unsafe_allow_html=True,
)

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
