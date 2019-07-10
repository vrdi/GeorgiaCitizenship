# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import geopandas
import pandas as pd
import matplotlib.pyplot as plt
import requests
import numpy as np

#Zip download from https://www.census.gov/programs-surveys/decennial-census/about/voting-rights/cvap.html
cvap = "BlockGr.csv"
data =pd.read_csv(cvap)

data['georgia'] = data.GEONAME.apply(lambda s: "Georgia" in s)
#Filter for georgia
ga_data = data.loc[data['georgia']]


#filter for all races that are not 2 or more
ga_data = ga_data[~ga_data["lntitle"].isin(['American Indian or Alaska Native and White', 'Asian and White', 'Black or African American and White',
                                            'American Indian or Alaska Native and Black or African American',
                                            'Remainder of Two or More Race Responses'])]
print(ga_data)

#rename classifications in lntitle series to match our naming conventions
race_dict = {'Total': 'TOT', 'Not Hispanic or Latino': 'NH', 'American Indian or Alaska Native Alone':'AIAN_Alone', 
             'Asian Alone':'NH_ASIAN', 'Black or African American Alone':'NH_BLACK', 
             'Native Hawaiian or Other Pacific Islander Alone':'NH_NHPI', 'White Alone':'NH_WHITE',
              'American Indian or Alaska Native and White': 'NH_2MORE', 'Asian and White': 'NH_2MORE', 'Black or African American and White': 'NH_2MORE',
             'American Indian or Alaska Native and Black or African American': 'NH_2MORE', 'Remainder of Two or More Race Responses':'NH_2MORE', 
             'Hispanic or Latino': 'HISP'}
ga_data.replace(to_replace =race_dict, 
                 inplace = True ) 
ga_data = ga_data.pivot(index='geoid', columns='lntitle', values = ['CIT_EST', 'CVAP_EST']).reset_index()
ga_data.columns = [' '.join(col).strip() for col in ga_data.columns.values]


#strip the first characters to match with the shapefile geoid.
ga_data['geoid'] = ga_data['geoid'].map(lambda x: str(x)[7:])


#attach to the shapefile 

df = geopandas.read_file("C:/Users/jasmi/VRDI/Georgia/GeorgiaCitizenship/tl_2010_13_bg10/tl_2010_13_bg10.shp")


geo = pd.merge(left=ga_data, right = df, left_on= ['geoid'], right_on =['GEOID10'])