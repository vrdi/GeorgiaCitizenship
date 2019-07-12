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

tracts = tracts.to_crs(precincts.crs)

assignment = maup.assign(precincts, tracts)

precincts["TRACT"] = assignment

assignment.head()


variables = ["ID","FIPS2", "PRES16D", "PRES16R", "PRES16L", "SEN16D", "SEN16R", "SEN16L",]             

#"DISTRICT", "PRECINCT_I", "PRECINCT_N", "CTYNAME","HDIST", "SENDIST" 
for x in precincts.columns:
    if x in variables:
        precincts[x] = precincts[x].astype(int)


pieces = maup.intersections(tracts, precincts)

weights = pieces.area / pieces.index.get_level_values("source").map(tracts.area)

tracts[variables] = maup.prorate(
        pieces,
        precincts[variables],
        weights.iloc[weights.nonzero()[0]]
        )

precincts.to_file("ga_2012_tract_precinct")

