#!/usr/bin/env python
# coding: utf-8

# In[1]:


# IMPORTS

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import requests

# SET UP API CALLS

HOST = "https://api.census.gov/data"
year = "2012"
dataset = "acs/acs5"
base_url = "/".join([HOST, year, dataset])

# SPECIFY VARIABLES FOR DOWNLOAD
# Race Data
get_vars = []
for i in range(10):
    if i <= 8:
        get_vars.append("B02001" +"_00"+ str(i+1) + "E" )
    else:
        get_vars.append("B02001" +"_0"+ str(i+1) + "E" )
col_names = ["totpop", "white_pop", "black_pop","native_pop", "asian_pop", "hawaiian_pop","race_other","race_multiple","race_multiple_other", "race_multiple_excl_other","state","county","tract"]

# Hispanic/Latino Origin Data
get_vars = []
for i in range(21):
        if i <= 8:
            get_vars.append("B03002" +"_00"+ str(i+1) + "E" )
        else:
            get_vars.append("B03002" +"_0"+ str(i+1) + "E" )
col_names = ["total", "not_hisp_total","not_hisp_white","not_hisp_black","not_hisp_native", "not_hisp_asian","not_hisp_hawaiian", "not_hisp_other", "not_hisp_multiple", "not_hisp_multiple_other","not_hisp_multiple_excl_other","hisp_total","hisp_white","hisp_black","hisp_native", "hisp_asian", "hisp_hawaiian", "hisp_other", "hisp_multiple", "hisp_multiple_other","hisp_multiple_excl_other", "state","county","tract"]

# Citizenship Voting-Age Population

races = [#"A",
         "B",
         "C", 
         "D", 
         #"E",
         #"F",
         #"G", 
         "H",
         "I"]   



#Loop over races to get CVAP counts and append to a dataframe. 
get_var=[]
df_col_names = ["MNative", "MNat", "FNative","FNat", "state", 'county', "tract"]
ga_col_names= ['state', 'county', 'tract']
ga_tract = pd.DataFrame(columns=ga_col_names)


for race in races:
    get_var= ["B05003" + str(race) + "_" + str(i+1).zfill(3) 
              + "E" for i in range(23) if i+1 in [9, 11,20,22] ]
    print(get_var)

    predicates = {}
    predicates["get"] = ",".join(get_var)
    predicates["for"] = "tract:*"
    predicates["in"] = "state:13"
    # predicates["key"] = "YOUR_CENSUS_API_KEY"
    print("made predicates")
    
    r = requests.get(base_url, params=predicates)
    print("made request")
    
    # Examine the response
    r.text
    
    df = pd.DataFrame(columns=df_col_names, data=r.json()[1:])
    int_cols = df_col_names[1:-3]
    df[int_cols] = df[int_cols].astype(int)
    
    ga_tract['state'] = df['state']
    ga_tract['county'] = df['county']
    ga_tract['tract'] = df['tract']
    
    ga_tract[str(race + '_CVAP' )] = df.sum(axis=1)

# Save to file
ga_tract.to_pickle("ga_tract.pickle")    



# REQUEST VARIABLES

# NOTE: How many variables? If <= 50, can do in one API call
# If more than 50, download multiple and join

predicates = {}
predicates["get"] = ",".join(get_vars)
predicates["for"] = "tract:*"
predicates["in"] = "state:13"
# predicates["key"] = "YOUR_CENSUS_API_KEY"

r = requests.get(base_url, params=predicates)
df1 = pd.DataFrame(columns=col_names, data=r.json()[1:])


int_cols = col_names[:-3]
df1[int_cols] = df1[int_cols].astype(int)






ga_tract_race = pd.DataFrame(columns = col_names, data = r.json()[1:])
ga_tract_race[col_names] = ga_tract_race[col_names].astype(int)




# Download 2012 Census Tract- TigerLine File for Georgia

geo_tract = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2012/TRACT/tl_2012_13_tract.zip")

# JOIN DEMOGRAPHIC DATA TO TRACT GEODATAFRAME

# EXPORT SHAPEFILE FOR CHAIN


# In[ ]:




