# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 10:43:20 2019

@author: Brian
"""

# imports

import requests
import pandas as pd
import numpy as np


# =============================================================================
# 
# HOST = "https://api.census.gov/data"
# year = "2010"
# dataset = "dec/sf1"
# base_url = "/".join([HOST, year, dataset])
# 
# # Build the list of variables to request
# get_vars = ["NAME"] + ["P005" + str(i + 1).zfill(3) for i in range(17)]
# 
# predicates = {}
# predicates["get"] = ",".join(get_vars)
# predicates["for"] = "county:*"
# predicates["in"] = "state:13"
# # predicates["key"] = "YOUR_CENSUS_API_KEY"
# 
# r = requests.get(base_url, params=predicates)
# 
# # Examine the response
# print(r.text)
# 
# =============================================================================


HOST = "https://api.census.gov/data"
year = "2012"
dataset = "acs/acs5"
base_url = "/".join([HOST, year, dataset])

# Build the list of variables to request
get_vars = ["NAME"] + ["B05003_" + str(i).zfill(3) +"E" for i in [
        1,
        4,6,7,
        9,11,12,
        15,17,18,
        20,22,23
        ]]


predicates = {}
predicates["get"] = ",".join(get_vars)
predicates["for"] = "state:*"
# predicates["in"] = "state:13"
# predicates["key"] = "YOUR_CENSUS_API_KEY"

r = requests.get(base_url, params=predicates)

# Examine the response
# print(r.text)

col_names = [
        "name","total_population",
        "male_minor_native", "male_minor_naturalized", "male_minor_noncitizen",
        "male_over_18_native", "male_over_18_naturalized", "male_over_18_noncitizen",
        "female_minor_native", "female_minor_naturalized", "female_minor_noncitizen",
        "female_over_18_native", "female_over_18_naturalized", "female_over_18_noncitizen",
        "state"
        ]
pop_cit_data = pd.DataFrame(columns=col_names, data=r.json()[1:])
## ALERT ALERT ALERT this table includes Puerto Rico and D.C. We probably don't want that?


for name in col_names[1:len(col_names)]:
    pop_cit_data[name] = pd.to_numeric(pop_cit_data[name])

#pop_cit_data["minor_citizen"] = pop_cit_data["male_minor_native"] + pop_cit_data["male_minor_naturalized"] + pop_cit_data["female_minor_native"] + pop_cit_data["female_minor_naturalized"]
#pop_cit_data["minor_noncitizen"] = pop_cit_data["male_minor_noncitizen"] + pop_cit_data["female_minor_noncitizen"]
#pop_cit_data["over_18_citizen"] = pop_cit_data["male_over_18_native"] + pop_cit_data["male_over_18_naturalized"] + pop_cit_data["female_over_18_native"] + pop_cit_data["female_over_18_naturalized"]
#pop_cit_data["over_18_noncitizen"] = pop_cit_data["male_over_18_noncitizen"] + pop_cit_data["female_over_18_noncitizen"]

pop_cit_data["citizen_pop"] = \
    pop_cit_data["male_minor_native"] + pop_cit_data["male_minor_naturalized"] + pop_cit_data["female_minor_native"] + pop_cit_data["female_minor_naturalized"] \
    + pop_cit_data["male_over_18_native"] + pop_cit_data["male_over_18_naturalized"] + pop_cit_data["female_over_18_native"] + pop_cit_data["female_over_18_naturalized"]
pop_cit_data["VAP"] = \
    pop_cit_data["male_over_18_native"] + pop_cit_data["male_over_18_naturalized"] + pop_cit_data["female_over_18_native"] + pop_cit_data["female_over_18_naturalized"] \
    + pop_cit_data["male_over_18_noncitizen"] + pop_cit_data["female_over_18_noncitizen"]
pop_cit_data["CVAP"] = \
    pop_cit_data["male_over_18_native"] + pop_cit_data["male_over_18_naturalized"] + pop_cit_data["female_over_18_native"] + pop_cit_data["female_over_18_naturalized"]


pop_cit_data = pop_cit_data.drop(columns=col_names[2:len(col_names)-1])
pop_cit_data = pop_cit_data.drop([8,51]) #drop the District of Columbia and Puerto Rico from the table
pop_cit_data = pop_cit_data.set_index("state")



def huntington_hill(series, total_seats):
    """
    Runs the Huntington-Hill apportionment algorithm (the algorithm currently used by the U.S. Congress for reapportionment after the decennial census).
    Returns a Pandas Series object with the same index as the input whose entries are the number of seats apportioned to each index.
    
    Arguments:
    series -- a Pandas Series object whose indices are entities to receive apportioned seats (e.g. states) and whose entries are the population numbers on which the apportionment is to be based (total population, CVAP, or something else)
    total_seats -- the total number of seats to apportion (e.g. 435 for the U.S. House of Representatives)
    """
    if len(series) > total_seats:
        raise ValueError("Too few seats (%d) for every series index (of which there are %d) to receive a seat" % (total_seats,len(series)))
    seats = pd.Series(data = 1, index = series.index)
    priorities = series/np.sqrt(2)
    # TODO finish this