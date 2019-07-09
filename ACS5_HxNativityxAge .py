#!/usr/bin/env python
# coding: utf-8

# In[20]:


# imports
import requests
import pandas as pd

HOST = "https://api.census.gov/data"
year = "2010"
dataset = "acs/acs5"
base_url = "/".join([HOST, year, dataset])


# In[51]:


# Build the list of variables to request
get_vars=[]
for i in range(23):
    if i <= 8:
        if i+1 == 9 or i+1 ==6 or i+1==4:
            get_vars.append("B05003I" + "_00" + str(i+1) +"E")
    else:
        if i+1 in [11, 22, 20, 16, 17]:
            get_vars.append("B05003I" + "_0" + str(i+1) + "E")

get_vars


# In[27]:


# race_groups=["A","B","C","D","E","F","G","H","I"] 
# #A-G correspond to races. H and I classify non-hispanic white (H) and hispanic(I).

# names= [9, 11, 20, 22]
# get_var2 = ["B05003" + race_group + [str(name).zfill(3) + "E" for name in names] for race_group in race_groups ]
# #get_vars3 =["B05003" + race_group[h] if race_group[h] == "I" + "_0" + str(name[i]) for i in name] 
# get_var2


# In[57]:


predicates = {}
predicates["get"] = ",".join(get_vars)
predicates["for"] = "tract:*"
predicates["in"] = "state:13"
# predicates["key"] = "YOUR_CENSUS_API_KEY"

r = requests.get(base_url, params=predicates)


# In[58]:


print(r.url)


# In[59]:


# Examine the response
print(r.text)


# In[71]:


col_names = ["H Male Native u18", "H Male Naturalized u18", "H Male Native o18", "H Male Naturalized o18",
             "H Female Native u18", "H Female Naturalized u18", "H Female Native o18", "H Female Naturalized o18",
            "state", "county", "tract"]


# In[89]:


ga_tract = pd.DataFrame(columns=col_names, data=r.json()[1:])
ga_tract


# In[90]:


int_cols = col_names[:-3]
ga_tract[int_cols] = ga_tract[int_cols].astype(int)


# In[91]:


ga_tract["Hispanic Citizen Total"] = ga_tract.sum(axis =1)


# In[87]:


# Save to file
ga_county.to_pickle("ga_county.pickle")


# In[92]:


ga_tract


# In[ ]:




