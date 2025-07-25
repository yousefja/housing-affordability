# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 18:26:00 2025

@author: youse
"""

import ast
import numpy as np
import pandas as pd
from util import format_price


PATH_TO_HOUSING_DATA = '../output/scraped_listings.csv'
PATH_TO_INCOME_DATA = "../data/ACSST5Y2023.S1901_2025-07-24T192912/ACSST5Y2023.S1901-Data.csv"
# BUFFALO_ZIPS = "14201, 14202, 14203, 14204, 14206, 14207, 14208, 14209, 14210, 14211, 14212, 14213, 14214, 14215, 14216, 14218, 14220, 14222, 14223, 14225, 14226, 14227, 14221, 14224, 14228, 14217, 14425, 14219"


df_housing = pd.read_csv(PATH_TO_HOUSING_DATA)
df_income = pd.read_csv(PATH_TO_INCOME_DATA, header=1)

###############
# PREPROCESSING
###############

# format housing columns
df_housing['Price'] = df_housing['Price'].apply(format_price)
df_housing['Bedrooms'] = pd.to_numeric(df_housing['Bedrooms'], errors='coerce')
df_housing['Bathrooms'] = pd.to_numeric(df_housing['Bathrooms'], errors='coerce')
df_housing['SqFt'] = df_housing['SqFt'].replace('[,]', '', regex=True).astype(float)

# calculate cost of house by sqft
df_housing['Price_Per_SqFt'] = df_housing['Price'] / df_housing['SqFt']

# get zip code from geography col
df_income['Zipcode'] = df_income['Geographic Area Name'].apply(lambda x: int(x.split()[-1].strip()))

# get buffalo zips as list of ints
# buffalo_zips = list(map(int, ast.literal_eval(BUFFALO_ZIPS)))

# no longer needed, filtering happens when joining to the scraped listing data
# filter census income data for buffalo zips
# df_income = df_income[df_income.Zipcode.isin(buffalo_zips)]
# assert(len(df_income) == len(buffalo_zips))

# select only columns of interest from income data
df_income = df_income[['Estimate!!Households!!Median income (dollars)',
                       #'Margin of Error!!Households!!Median income (dollars)',
                       'Zipcode']]

# rename median income column
df_income.rename(columns={'Estimate!!Households!!Median income (dollars)':'Household_Median_Income'}, inplace=True)

# convert median income to float
df_income['Household_Median_Income'] = df_income['Household_Median_Income'].astype(float)

###################
# MERGE INCOME DATA
###################

# join income data to housing data
df_housing['Zipcode'] = df_housing['Zipcode'].astype(int)
df_analysis = df_housing.merge(df_income, on='Zipcode', how='left')

# TODO:maybe don't filter by buffalo and just have the join to the scraped listing data do the filtering?
# get rows from df_housing that didn't join
# df_no_join = df_analysis[df_analysis['Estimate!!Households!!Median income (dollars)'].isna()]
# df_no_join.Zipcode.unique() # get missing zip codes from listings

#######################
# AFFORDABILITY METRICS
#######################

# INDIVIDUAL LEVEL METRICS

# 30% rule
'''
Affordable housing is generally defined as housing where the gross housing costs 
(including utilities, taxes, and insurance for homeowners, or contract rent plus utilities for renters) 
do not exceed 30% of a household's gross income. This threshold is established by organizations
 like the U.S. Department of Housing and Urban Development (HUD) and is a key factor in determining 
 eligibility for various housing assistance programs. 
'''

# gap between affordable price and actual price
df_analysis['Affordable_Price'] = df_analysis.Household_Median_Income * 3.0
df_analysis['Affordability_Gap'] = df_analysis.Price - df_analysis.Affordable_Price 


'''
5. Home Value vs. Area Median Income (AMI) Benchmarks
Example classification:

Affordable to ≤80% AMI → "affordable housing"

Affordable to ≤50% AMI → "very low income housing"
'''



# ZIP LEVEL METRICS


def zipcode_aggregates(df, df_income):
    '''
    HPI divides the median house price by the median household income. 
    While a good HPI is generally considered to be between 2 and 3, this can vary significantly 
    based on local economic conditions and housing availability.
    '''
    
    # get min, max, and median house price per zipcode
    df_zip_agg = df.groupby('Zipcode').agg(
        Min_Price=('Price', 'min'),
        Max_Price=('Price', 'max'),
        Median_Price=('Price', 'median'),
    ).reset_index()

    # get zip median income 
    df_zip_agg = df_zip_agg.merge(df_income,
                                  how='left',
                                  on='Zipcode')
    
    # calculate HPI per zip
    df_zip_agg['HPI'] = df_zip_agg.Median_Price / df_zip_agg.Household_Median_Income
    
    # flag zips where lowest house price is > 3x the median income
    df_zip_agg['Unaffordable'] = df_zip_agg.Min_Price > df_zip_agg.Household_Median_Income*3
    
    return df_zip_agg


df_zip_level_analysis = zipcode_aggregates(df_analysis, df_income)


'''
IF I WANT TO EXPAND LATER -- FOR FURTHER INDIVIDUAL LEVEL AFFORDABILITY METRICS 

# Example: Single home and AMI
home_price = 250000
ami = 60000  # Area Median Income

# Assumptions
interest_rate = 0.06      # 6% annual mortgage interest
loan_term_years = 30
tax_insurance_rate = 0.012  # 1.2% of home value annually

# Function to calculate monthly mortgage payment
def monthly_mortgage(P, r, n_years):
    r_monthly = r / 12
    n_months = n_years * 12
    return P * (r_monthly * (1 + r_monthly)**n_months) / ((1 + r_monthly)**n_months - 1)

# Function to check affordability at a given % of AMI
def is_affordable(home_price, income, interest_rate, loan_term, tax_ins_rate, threshold=0.3):
    monthly_income = income / 12
    mortgage_payment = monthly_mortgage(home_price, interest_rate, loan_term)
    taxes_insurance = (home_price * tax_ins_rate) / 12
    total_housing_cost = mortgage_payment + taxes_insurance
    return total_housing_cost <= monthly_income * threshold

# Evaluate affordability at different income thresholds
for level, pct in [('Extremely Low Income', 0.3), ('Very Low Income', 0.5), 
                   ('Low Income', 0.8), ('Median Income', 1.0)]:
    income = ami * pct
    affordable = is_affordable(home_price, income, interest_rate, loan_term_years, tax_insurance_rate)
    print(f"{level} (AMI {int(pct*100)}%): {'Affordable' if affordable else 'Not Affordable'}")
'''