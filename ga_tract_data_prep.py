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
get_vars=[]
for i in range(23):
    if i <= 8:
        if i+1 == 9 or i+1 ==6 or i+1==4:
            get_vars.append("B05003I" + "_00" + str(i+1) +"E")
    else:
        if i+1 in [11, 22, 20, 16, 17]:
            get_vars.append("B05003I" + "_0" + str(i+1) + "E")

col_names = ["H Male Native u18", "H Male Naturalized u18", "H Male Native o18", "H Male Naturalized o18",
             "H Female Native u18", "H Female Naturalized u18", "H Female Native o18", "H Female Naturalized o18",
            "state", "county", "tract"]

# Improve CVAP downloads (WIP)

# race_groups=["A","B","C","D","E","F","G","H","I"] 
# #A-G correspond to races. H and I classify non-hispanic white (H) and hispanic(I).

# names= [9, 11, 20, 22]
# get_var2 = ["B05003" + race_group + [str(name).zfill(3) + "E" for name in names] for race_group in race_groups ]
# #get_vars3 =["B05003" + race_group[h] if race_group[h] == "I" + "_0" + str(name[i]) for i in name] 
# get_var2



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