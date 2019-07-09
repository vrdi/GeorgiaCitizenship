#!/usr/bin/env python
# coding: utf-8

# In[32]:


import requests
import pandas as pd

HOST = "https://api.census.gov/data"
year = "2012"
dataset = "acs/acs5"
base_url = "/".join([HOST, year, dataset])

# Build the list of variables to request - iterated over variables

get_vars = []
for i in range(21):
        if i <= 8:
            get_vars.append("B03002" +"_00"+ str(i+1) + "E" )
        else:
            get_vars.append("B03002" +"_0"+ str(i+1) + "E" )

# join into a string added to the end of the API call
predicates = {}
predicates["get"] = ",".join(get_vars)
predicates["for"] = "tract:*"
predicates["in"] = "state:13"
# predicates["key"] = "YOUR_CENSUS_API_KEY"

r = requests.get(base_url, params=predicates)


# In[33]:


print(get_vars)


# In[34]:


print(r.url)


# In[36]:


col_names = ["total", "not_hisp_total","not_hisp_white","not_hisp_black","not_hisp_native", "not_hisp_asian","not_hisp_hawaiian", "not_hisp_other", "not_hisp_multiple", "not_hisp_multiple_other","not_hisp_multiple_excl_other","hisp_total","hisp_white","hisp_black","hisp_native", "hisp_asian", "hisp_hawaiian", "hisp_other", "hisp_multiple", "hisp_multiple_other","hisp_multiple_excl_other", "state","county","tract"]
ga_tract_hisp = pd.DataFrame(columns = col_names, data = r.json()[1:])
ga_tract_hisp[col_names] = ga_tract_hisp[col_names].astype(int)

ga_tract_hisp.to_pickle("ga_tract_hisp.pickle")


# In[37]:


ga_tract_hisp


# In[ ]:




