# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 10:43:20 2019

@author: Brian
"""

# imports

import requests
import pandas as pd
import numpy as np




def huntington_hill(series, total_seats, name="seats"):
    """
    Runs the Huntington-Hill apportionment algorithm (the algorithm currently used by the U.S. Congress for reapportionment after the decennial census).
    Returns a Pandas Series object with the same index as the input whose entries are the number of seats apportioned to each index.
    Formula based on https://www.census.gov/topics/public-sector/congressional-apportionment/about/computing.html
    
    Arguments:
    series -- a Pandas Series object whose indices are entities to receive apportioned seats (e.g. states) and whose entries are the population numbers on which the apportionment is to be based (total population, CVAP, or something else)
    total_seats -- the total number of seats to apportion (e.g. 435 for the U.S. House of Representatives)
    name -- name for the output series, "seats" by default
    """
    if len(series) > total_seats:
        raise ValueError("Too few seats (%d) for every series index (of which there are %d) to receive a seat" % (total_seats,len(series)))
    seats = pd.Series(data = 1, index = series.index, name = name)
    priorities = series/np.sqrt(2) #initialize all of the priorities
    for i in range(total_seats-len(series)):
        idx = priorities.idxmax() #finds the state with the highest priority; this is the state that will get another seat
        priorities[idx] *= np.sqrt(seats[idx]/(seats[idx]+2)) #updates the priority of the chosen state, equivalent to the formulation described on the census.gov site
        seats[idx] += 1 #add a seat to that state's seat count
    if seats.sum() != total_seats:
        raise Exception("Number of seats allocated (%d) was different from total_seats (%d)" % (seats.sum(),total_seats))
    return seats





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


# ====== Download data from Census API ======

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


# ====== Convert data to Pandas DataFrame ======

col_names = [
        "name","tot_pop", #total population
        "male_minor_native", "male_minor_naturalized", "male_minor_noncitizen",
        "male_over_18_native", "male_over_18_naturalized", "male_over_18_noncitizen",
        "female_minor_native", "female_minor_naturalized", "female_minor_noncitizen",
        "female_over_18_native", "female_over_18_naturalized", "female_over_18_noncitizen",
        "state"
        ]
pop_cit_data = pd.DataFrame(columns=col_names, data=r.json()[1:])

#convert numerical columns from strings to integers
for name in col_names[1:len(col_names)]:
    pop_cit_data[name] = pd.to_numeric(pop_cit_data[name])


# ====== Make new columns, clean up table ======

#pop_cit_data["minor_citizen"] = pop_cit_data["male_minor_native"] + pop_cit_data["male_minor_naturalized"] + pop_cit_data["female_minor_native"] + pop_cit_data["female_minor_naturalized"]
#pop_cit_data["minor_noncitizen"] = pop_cit_data["male_minor_noncitizen"] + pop_cit_data["female_minor_noncitizen"]
#pop_cit_data["over_18_citizen"] = pop_cit_data["male_over_18_native"] + pop_cit_data["male_over_18_naturalized"] + pop_cit_data["female_over_18_native"] + pop_cit_data["female_over_18_naturalized"]
#pop_cit_data["over_18_noncitizen"] = pop_cit_data["male_over_18_noncitizen"] + pop_cit_data["female_over_18_noncitizen"]

#citizen population
pop_cit_data["cit_pop"] = \
    pop_cit_data["male_minor_native"] + pop_cit_data["male_minor_naturalized"] + pop_cit_data["female_minor_native"] + pop_cit_data["female_minor_naturalized"] \
    + pop_cit_data["male_over_18_native"] + pop_cit_data["male_over_18_naturalized"] + pop_cit_data["female_over_18_native"] + pop_cit_data["female_over_18_naturalized"]
#voting-age population (18 and over)
pop_cit_data["VAP"] = \
    pop_cit_data["male_over_18_native"] + pop_cit_data["male_over_18_naturalized"] + pop_cit_data["female_over_18_native"] + pop_cit_data["female_over_18_naturalized"] \
    + pop_cit_data["male_over_18_noncitizen"] + pop_cit_data["female_over_18_noncitizen"]
#citizen voting-age population
pop_cit_data["CVAP"] = \
    pop_cit_data["male_over_18_native"] + pop_cit_data["male_over_18_naturalized"] + pop_cit_data["female_over_18_native"] + pop_cit_data["female_over_18_naturalized"]

pop_cit_data = pop_cit_data.drop(columns=col_names[2:len(col_names)-1]) #drop the original data columns
pop_cit_data = pop_cit_data.drop([8,51]) #drop the District of Columbia and Puerto Rico from the table
pop_cit_data = pop_cit_data.set_index("state")


# ====== Run apportionment algorithm ======

#run the Huntington-Hill algorithm on the states under four different population counts upon which to base an apportionment
#each column of seat_counts gives the number of seats that a given state would get if we apportioned based on the total population, the citizen population, the voting-age population, or the citizen voting-age population
seat_counts = pd.concat(
        [pop_cit_data["name"]] + [huntington_hill(pop_cit_data[col],435,"seats_"+col) for col in [
                "tot_pop","cit_pop","VAP","CVAP"
                ]],
        axis = 1
        )

print(seat_counts)

# ====== Get states' shares of the total US state population under different methods of counting population ======

pop_percents = pd.concat(
        [pop_cit_data["name"]] + [100*pop_cit_data[col]/pop_cit_data[col].sum() for col in [
                "tot_pop","cit_pop","VAP","CVAP"
                ]],
        axis = 1
        )

print(pop_percents)