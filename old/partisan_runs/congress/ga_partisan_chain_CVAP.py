# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 10:19:41 2019

@author: Katherine
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 16:35:30 2019

@author: Katherine
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 11:18:24 2019

@author: Katherine
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 15:06:44 2019

@author: Katherine
"""

# Imports

import os
import json
from gerrychain import Graph, GeographicPartition, Partition, Election, accept
from gerrychain.updaters import Tally, cut_edges
import geopandas as gpd
import numpy as np
from gerrychain.random import random
import copy

from gerrychain import MarkovChain
from gerrychain.constraints import single_flip_contiguous
from gerrychain.proposals import propose_random_flip, recom
from gerrychain.accept import always_accept
from gerrychain.metrics import polsby_popper
from gerrychain import constraints
from gerrychain.constraints import no_vanishing_districts

from collections import defaultdict, Counter
from itertools import combinations_with_replacement


import matplotlib.pyplot as plt

import networkx as nx

import pandas

import math

#from IPython.display import clear_output

from functools import partial

from gerrychain.tree import recursive_tree_part
# setup -- SLOW

#shapefile = "https://github.com/mggg-states/NC-shapefiles/raw/master/NC_VTD.zip"
shapefile = "./maupped_ga_2016_precincts/maupped_ga_2016_precincts.shp"
df = gpd.read_file(shapefile)

#county_col = "County"
#pop_col = "PL10AA_TOT"
#uid = "VTD"
variables = ["ID","FIPS2", "PRES16D", "PRES16R", "PRES16L", "SEN16D", "SEN16R", "SEN16L",]
for x in df.columns:
   if x in variables:
       df[x] = df[x].astype(int)
#county_col = "COUNTYFP10"
pop_col = "TOTPOP"

df["CPOP"] = df["TOTPOP"]-df["NCPOP"]
ccol = "CPOP"
uid = "ID"
df["CVAP"]= df["MNVVAPTOT"]+df["MNLVAPTOT"]+df["FNVVAPTOT"]+df["FNLVAPTOT"]
CVAP = "CVAP"
num_districts = 14



graph = Graph.from_geodataframe(df,ignore_errors=True)
graph.add_data(df,list(df))
graph = nx.relabel_nodes(graph, df[uid])

elections = [
        Election("PRES16",{"Democratic": "PRES16D","Republican":"PRES16R" }),
        Election("SEN16",{"Democratic": "SEN16D","Republican":"SEN16R" })]

#my_updaters = {"population" : updaters.Tally("TOTPOP", alias="population")}
my_updaters = {"population" : Tally(pop_col, alias="population"), "CVAP": Tally(CVAP, alias="CVAP"), "cpop": Tally(ccol, alias="cpop"),
            "cut_edges": cut_edges}
election_updaters = {election.name: election for election in elections}
my_updaters.update(election_updaters)

tot_pop_col = 0
tot_ccol = 0
tot_CVAP = 0
#for tallying over CVAP:
for n in graph.nodes():
    graph.node[n][CVAP] = int(graph.node[n][CVAP])
    tot_CVAP += graph.node[n][CVAP]

cddict = recursive_tree_part(graph,range(num_districts),tot_CVAP/num_districts,CVAP,0.01,1)

starting_partition = Partition(graph,assignment=cddict,updaters=my_updaters)



#-------------------------------------------------------------------------------------------

#CHAIN FOR TOTPOP
proposal = partial(
        recom, pop_col=CVAP, pop_target=tot_CVAP/num_districts, epsilon=0.02, node_repeats=1
   )

compactness_bound = constraints.UpperBound(
        lambda p: len(p["cut_edges"]), 2 * len(starting_partition["cut_edges"])
    )

chain = MarkovChain(
        proposal,
         constraints=[
            constraints.within_percent_of_ideal_population(starting_partition, 0.14),compactness_bound
          #constraints.single_flip_contiguous#no_more_discontiguous
        ],
        accept=accept.always_accept,
        initial_state=starting_partition,
        total_steps=10000
    )


t = 0
SENwins_list = []
PRESwins_list = []
cutedges_list = []
for part in chain:
    SENwins_list.append(part["SEN16"].wins("Republican"))
    PRESwins_list.append(part["PRES16"].wins("Republican"))
    cutedges_list.append(len(part["cut_edges"]))
    t += 1
    if t % 100 == 0:
        print("finished chain " + str(t))
        
outputdir = './Outputs/'
obj = {"CVAP_based_Rseats_sen" : list(SENwins_list)}

with open(outputdir+"CD14_CVAP_based_Rseats_sen.json", 'w') as jf1:
    json.dump(dict(obj), jf1)

outputdir = './Outputs/'
obj = {"CVAP_based_Rseats_pres" : list(PRESwins_list)}

with open(outputdir+"CD14_CVAP_based_Rseats_pres.json", 'w') as jf1:
    json.dump(dict(obj), jf1)
    
plt.figure()
plt.style.use('seaborn-deep')

colors = ['green', 'goldenrod']
labels= ['TOTPOP SEN16', 'CVAP SEN16']

plt.hist([TOTPOP_SENwins_list, CVAP_SENwins_list],label=labels, color=colors)
plt.legend(loc='upper right')
plt.show()

 
#CHANGE
plt.figure()
plt.hist(SENwins_list)
plt.title("Histogram of Republican Seats (based on Senate 2016)")
plt.xlabel("Seats")
#plt.savefig("PA_hist_symmetric_entropy_5000.png")
plt.show()

plt.figure()
plt.hist(PRESwins_list)
plt.title("Histogram of Republican Seats (based on Pres 2016)")
plt.xlabel("Seats")
#plt.savefig("PA_hist_symmetric_entropy_5000.png")
plt.show()

plt.figure()
plt.hist(cutedges_list)
plt.title("Histogram of Cut Edges")
plt.xlabel("Cut Edges")
#plt.savefig("PA_hist_symmetric_entropy_5000.png")
plt.show()


#print(moon_score(starting_partition))
#print(list(starting_partition.assignment.keys()))
#print([n for n in graph.nodes if n not in starting_partition.assignment])
#print(df["VTD"])
#print(starting_partition["cut_edges"])


#d = county_splits_dict(starting_partition)
#print(cut_edges_in_county(starting_partition))
#print(cut_edges_in_district(starting_partition))
#sum( [ len([ dd for dd  in [dict(v) for v in d.values()] if k in dd.keys()]) > 1 for k in counties]    )