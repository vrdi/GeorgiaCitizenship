#!/usr/bin/env python
# coding: utf-8

# In[22]:


import requests
import pandas as pd

HOST = "https://api.census.gov/data"
year = "2012"
dataset = "acs/acs5"
base_url = "/".join([HOST, year, dataset])

# Build the list of variables to request - iterated over variables

get_vars = []
for i in range(10):
    if i <= 8:
        get_vars.append("B02001" +"_00"+ str(i+1) + "E" )
    else:
        get_vars.append("B02001" +"_0"+ str(i+1) + "E" )

# join into a string added to the end of the API call
predicates = {}
predicates["get"] = ",".join(get_vars)
predicates["for"] = "tract:*"
predicates["in"] = "state:13"
# predicates["key"] = "YOUR_CENSUS_API_KEY"

r = requests.get(base_url, params=predicates)


# In[23]:


get_vars


# In[26]:


print(r.url
    )


# In[44]:


col_names = ["totpop", "white_pop", "black_pop","native_pop", "asian_pop", "hawaiian_pop","race_other","race_multiple","race_multiple_other", "race_multiple_excl_other","state","county","tract"]
ga_tract_race = pd.DataFrame(columns = col_names, data = r.json()[1:])
ga_tract_race[col_names] = ga_tract_race[col_names].astype(int)

ga_tract_race.to_pickle("ga_tract_race.pickle")


# In[45]:


ga_tract_race


# In[ ]:




