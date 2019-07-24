# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 10:24:50 2019

@author: Katherine
"""

import maup
import geopandas as gpd
import matplotlib.pyplot as plt

precincts = gpd.read_file("./GA_precincts16/GA_precincts16.shp")
tracts = gpd.read_file("./data/ga_2012_tract.shp")

year = "2010"
fips = "13"

  # Download Census Blocks- TigerLine File for requested state and year    
tiger_fn = "tabblock" + year + "_" + fips +"_"+"pophu"
try:
    geo_blocks = gpd.read_file("data/" + tiger_fn + ".shp")
except:
    print("Downloading shapefile from Census")
    geo_blocks = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER" + year + "BLKPOPHU/" + tiger_fn + ".zip")
    #geo_tract.to_file("data/" + tiger_fn + ".gpkg", driver="GPKG") 
    geo_blocks.to_file("data/" + tiger_fn + ".shp")
else:
    print("Reading shapefile from cache")
tracts = tracts.to_crs(precincts.crs)
geo_blocks = geo_blocks.to_crs(precincts.crs)
assignment = maup.assign(precincts, tracts)

precincts["TRACT"] = assignment

assignment.head()


variables = ["ID","FIPS2", "PRES16D", "PRES16R", "PRES16L", "SEN16D", "SEN16R", "SEN16L",]             

#"DISTRICT", "PRECINCT_I", "PRECINCT_N", "CTYNAME","HDIST", "SENDIST" 
for x in precincts.columns:
    if x in variables:
        precincts[x] = precincts[x].astype(int)


pieces = maup.intersections(tracts, precincts)
 # Weight by prorated population from blocks
weights = geo_blocks["POP10"].groupby(maup.assign(geo_blocks, pieces)).sum()
# Normalize the weights so that votes are allocated according to their
# share of population in the old_precincts
weights = maup.normalize(weights, level=0)


tracts[variables] = maup.prorate(
        pieces,
        precincts[variables],
        weights.iloc[weights.nonzero()[0]]
        )

tracts.to_file("ga_2012_tract_precinct")

