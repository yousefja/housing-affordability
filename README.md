# real-estate-trends

WRITE-UP REMINDER:


    policy write-up for real-estate:
    keep in mind, this is median income, so this means half of the people in this zip code literally cannot afford these homes.
    
    Pivot this:
    % of residents who could afford these houses ->
    
    Show with a chart, a narrative, and a map that people are likely going to be priced out of their neighborhoods. 
    
    Affordable housing is generally defined as housing where the gross housing costs (including utilities, taxes, and insurance for homeowners, or contract rent plus utilities for renters) do not exceed 30% of a household's gross income. This threshold is established by organizations like the U.S. Department of Housing and Urban Development (HUD) and is a key factor in determining eligibility for various housing assistance programs. 
    
    When housing costs outpace income in a ZIP code, it typically means the area is unaffordable for the average resident. This can drive housing insecurity, gentrification, and economic displacement, and may signal the need for policy intervention, such as affordable housing development, rent controls, or income supports.


🏡 Project Title:

    "Neighborhood Snapshot: Real Estate Trends in [Your City]"
    A data scraping + mapping dashboard for housing insights


✅ Project Goal:

    Practice web scraping, data enrichment, visualization, and dashboarding
    Show potential clients how you turn public data into market-ready insights


⏱️ Timeline: 1–2 Days

    Day 1 (Core):

        Scrape property listings (10–50 items)
        Enrich with census data by ZIP
        Visualize on map + bar charts

    Day 2 (Optional Upgrades):

        Add filtering (Streamlit dashboard)
        Calculate price/sqft trends
        Add simple predictive model or time series trendline


🔧 Step-by-Step Plan

    🧩 Step 1: Scrape Property Listings (2–3 hrs)
        
        Pick 1 public site (some allow scraping):

            Zillow (caution: hard to scrape)
            ✅ Realtor.com – HTML content, no login required
            ✅ Redfin – scrape via search URL (e.g. https://www.redfin.com/city/30749/CA/San-Francisco)
            Craigslist Housing – great alternative!

        Fields to extract:

            Price
            Address or ZIP
            Bedrooms
            Bathrooms
            Sqft
            Listing Date
            URL
            Description (optional, for NLP/sentiment)

        Tools: requests, BeautifulSoup, pandas
        (Use Selenium or Playwright if site loads dynamically)

    📍 Step 2: Enrich with Public Data (1–2 hrs)
    
        Use Census API or public ZIP-to-income datasets:

            Census API: B19013: median household income by ZIP
            Or use static ZIP income CSV like from https://www.incomebyzipcode.com/

        Merge scraped data with:

            Median income
            Median home value (optional)

        Optional:

            Use Zillow Research CSVs for region-wide trends → https://www.zillow.com/research/data/

    📊 Step 3: Visualize (2 hrs)

        Use plotly, seaborn, or folium.

        Suggested Visuals:

            Heatmap: Average home price by ZIP code (use folium choropleth)
            Bar Chart: Price per sqft by neighborhood or ZIP
            Scatter Plot: Sqft vs Price
            Line chart: Number of listings by date (if you scrape across time)

    🖥️ Step 4 (Optional): Build a Streamlit App (2 hrs)

        Dropdown to filter by ZIP or price
        Histogram of price distribution
        Map of properties with tooltips
        streamlit run app.py


🎁 Final Deliverable

    📊 real_estate_scraper.ipynb: does the scraping + visualization
    💾 listings.csv: exported cleaned data
    📍 app.py: interactive dashboard (optional)
    📄 README.md: brief description + example screenshots
    📷 Screenshots or Loom for Upwork portfolio


🧠 Bonus Upgrade (for Day 2 or Job Proposals)

    Add sentiment analysis on property descriptions
    Build regression model: predict price based on sqft, ZIP, bedrooms
    Use geopandas to create ZIP-level shapefiles for advanced mapping
