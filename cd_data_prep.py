# IMPORTS
import geopandas as gpd
import pandas as pd
import requests
from fips import state_fips

HOST = "https://api.census.gov/data"


def cd_data_prep(st, year, cache = True):
    
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
    col_names_2 = "NCPOP"
    
    col_names.append(col_names_2)
    
    # Hispanic/Latino Origin Data
    
    for i in range(1,21):
        get_vars.append("B03002_" +str(i+1).zfill(3) + "E" )
           
    col_names_1 = ["NHISP","NH_WHITE","NH_BLACK","NH_AMIN", "NH_ASIAN","NH_NHPI", "NH_OTHER", "NH_2MORE", "NH_2MOREOTHER","NH_3MORE","HISP","H_WHITE","H_BLACK","H_AMIN", "H_ASIAN", "H_NHPI", "H_OTHER", "H_2MORE", "H_2MOREOTHER","H_3MORE", "state","congressional district"]
    col_names.extend(col_names_1)
    
    
    #predicates
    predicates = {}
    predicates["get"] = ",".join(get_vars)
    predicates["for"] = "congressional district:*"
    predicates["in"] = "state:" + state_fips[st]
    # predicates["key"] = "YOUR_CENSUS_API_KEY"
    
    r = requests.get(base_url, params=predicates)
    
    df = pd.DataFrame(columns=col_names, data=r.json()[1:])
    data_cols = col_names[:-3]
    df[data_cols] = df[data_cols].astype(int)
    #fix column data types string -> int
    # Citizenship Voting-Age Population
        
    races = ["",
             #"A",
             "B",
             "C", 
             "D", 
             #"E",
             #"F",
             #"G", 
             "H",
             "I"]   
        
    races_names = {"":"TOT","B":"BLK","C":"AMIN","D":"AS","H":"NHW", "I":"HISP"}
    
    #Loop over races to get CVAP counts and append to a dataframe. 
    get_var=[]
    df_col_names = ["MU18","MNVU18","MNLU18","MVAP", "MNVVAP", "MNLVAP", "FU18","FNVU18","FNLU18","FVAP","FNVVAP","FNLVAP"]
    geoid_col_names = ['state', 'congressional district']
    # ga_tract = pd.DataFrame(columns = geoid_col_names) # Assigned but not used?
        
    for race in races:
        get_var= ["B05003" + str(race) + "_" + str(i+1).zfill(3) 
                  + "E" for i in range(23) if i+1 in [3,4,6,8, 9, 11,14,15,17, 19, 20, 22] ]
        print(get_var)
    
        predicates = {}
        predicates["get"] = ",".join(get_var)
        predicates["for"] = "congressional district:*"
        predicates["in"] = "state:" + state_fips[st]
        # predicates["key"] = "YOUR_CENSUS_API_KEY"
        print("made predicates")
        
        r = requests.get(base_url, params=predicates)
        print("made request")
        
        current_col_names =[]

        for i in df_col_names:
            current_col_names.append(i + races_names[race])
        print(current_col_names)    

        current_col_names.extend(geoid_col_names)

        df_1 = pd.DataFrame(columns=current_col_names, data=r.json()[1:])
        int_cols = current_col_names[:-3]
        df_1[int_cols] = df_1[int_cols].astype(int)
        
        ## Not clear that ga_tract is being used later - LH
        # ga_tract['state'] = df_1['state']
        # ga_tract['county'] = df_1['county']
        # ga_tract['tract'] = df_1['tract']
        #
        # ga_tract[str(race + '_CVAP' )] = df_1.sum(axis=1)
    
    
        # MERGE df and df_1
        df = pd.merge(df , df_1, on = ["state", "congressional district"])    
    
    # Save to file
    df.to_pickle("data/df_" + st + "_" + year + ".pickle")    
    
    # Download Census Congressional District- TigerLine File for requested state and year    
    tiger_fn = "tl_" + year + "_us_cd112"
    try:
        geo_cd = gpd.read_file("data/" + tiger_fn + ".shp")
    except:
        print("Downloading shapefile from Census")
        geo_cd = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER" + year + "/CD/" + tiger_fn + ".zip")
        #geo_tract.to_file("data/" + tiger_fn + ".gpkg", driver="GPKG") 
        geo_cd.to_file("data/" + tiger_fn + ".shp")
    else:
        print("Reading shapefile from cache")

    # JOIN DEMOGRAPHIC DATA TO TRACT GEODATAFRAME
    geo = pd.merge(geo_cd, df, left_on = ["STATEFP", "CD112FP"], right_on = ["state", "congressional district"])
    # EXPORT SHAPEFILE FOR CHAIN
    #geo.to_file("data/" + st + "_" + year + "_CD.gpkg", driver="GPKG")
    geo.to_file("data/" + st + "_" + year + "_CD.shp")

if __name__ == "__main__":
    cd_data_prep('GA', 2012)
