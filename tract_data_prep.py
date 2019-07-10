# IMPORTS
import geopandas as gpd
import pandas as pd
import requests
from fips import state_fips

HOST = "https://api.census.gov/data"

def tract_data_prep(st, year, cache = True):
    
    st = st.lower()
    year = str(year)
    
    if st not in state_fips:
        raise Exception("You attempted to prepare data for '{}', which is not a valid state postal code.".format(st))
        
    # SET UP API CALLS
    dataset = "acs/acs5"
    base_url = "/".join([HOST, year, dataset])
    
    # SPECIFY VARIABLES FOR DOWNLOAD
    # Race Data
    get_vars = []
    for i in range(10):
            get_vars.append("B02001_" + str(i+1).zfill(3) + "E" )
    col_names = ["TOTPOP", "WPOP", "BPOP","AMINPOP", "ASIANPOP", "NHPIPOP","OTHERPOP","2MOREPOP", "2MOREOTHERPOP", "3MOREPOP"]
    
    # Non citizenship data
    get_vars.append("B05001_006E")
    col_names_2 = "NCVAP"
    
    col_names.append(col_names_2)
    
    # Hispanic/Latino Origin Data
    
    for i in range(1,21):
        get_vars.append("B03002_" +str(i+1).zfill(3) + "E" )
           
    col_names_1 = ["NHISP","NH_WHITE","NH_BLACK","NH_AMIN", "NH_ASIAN","NH_NHPI", "NH_OTHER", "NH_2MORE", "NH_2MOREOTHER","NH_3MORE","HISP","H_WHITE","H_BLACK","H_AMIN", "H_ASIAN", "H_NHPI", "H_OTHER", "H_2MORE", "H_2MOREOTHER","H_3MORE", "state","county","tract"]
    col_names.extend(col_names_1)
    
    
    #predicates
    predicates = {}
    predicates["get"] = ",".join(get_vars)
    predicates["for"] = "tract:*"
    predicates["in"] = "state:" + state_fips[st]
    # predicates["key"] = "YOUR_CENSUS_API_KEY"
    
    r = requests.get(base_url, params=predicates)
    
    df = pd.DataFrame(columns=col_names, data=r.json()[1:])
    data_cols = col_names[:-3]
    df[data_cols] = df[data_cols].astype(int)
    #fix column data types string -> int
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
    # geoid_col_names = ['state', 'county', 'tract'] # Assigned but not used?
    # ga_tract = pd.DataFrame(columns = geoid_col_names) # Assigned but not used?
    
    
    
    for race in races:
        get_var= ["B05003" + str(race) + "_" + str(i+1).zfill(3) 
                  + "E" for i in range(23) if i+1 in [9, 11,20,22] ]
        print(get_var)
    
        predicates = {}
        predicates["get"] = ",".join(get_var)
        predicates["for"] = "tract:*"
        predicates["in"] = "state:" + state_fips[st]
        # predicates["key"] = "YOUR_CENSUS_API_KEY"
        print("made predicates")
        
        r = requests.get(base_url, params=predicates)
        print("made request")
        
        # Examine the response
        r.text
        
        df_1 = pd.DataFrame(columns=df_col_names, data=r.json()[1:])
        int_cols = df_col_names[:-3]
        df_1[int_cols] = df_1[int_cols].astype(int)
        
        ## Not clear that ga_tract is being used later - LH
        # ga_tract['state'] = df_1['state']
        # ga_tract['county'] = df_1['county']
        # ga_tract['tract'] = df_1['tract']
        #
        # ga_tract[str(race + '_CVAP' )] = df_1.sum(axis=1)
    
    
    # MERGE df and df_1
    df_final = pd.merge(df , df_1, on = ["tract" , "county", "state"])    
    
    # Save to file
    df_final.to_pickle("data/df_final.pickle")    
    
    # Download Census Tract- TigerLine File for requested state and year    
    tiger_fn = "tl_" + year + "_" + state_fips[st] +"_tract"
    try:
        geo_tract = gpd.read_file("data/" + tiger_fn + ".shp")
    except:
        print("Downloading shapefile from Census")
        geo_tract = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER" + year + "/TRACT/" + tiger_fn + ".zip")
        geo_tract.to_file("data/" + tiger_fn + ".shp")        
    else:
        print("Reading shapefile from cache")

    # JOIN DEMOGRAPHIC DATA TO TRACT GEODATAFRAME
    geo = pd.merge(geo_tract, df_final, left_on = ["STATEFP", "COUNTYFP","TRACTCE"], right_on = ["state", "county", "tract"])
    # EXPORT SHAPEFILE FOR CHAIN
    geo.to_file("data/" + st + "_tract.shp")
    