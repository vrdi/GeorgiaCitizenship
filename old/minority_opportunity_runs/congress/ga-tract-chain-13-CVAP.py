#!/usr/bin/env python
# coding: utf-8

# In[1]:


# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 10:59:39 2019

@author: Katherine, Ki Wan
"""

import csv
import os
from functools import partial
import json
import numpy as np
import geopandas as gpd
import matplotlib

import matplotlib.pyplot as plt
#import seaborn as sns
import networkx as nx
import random


from gerrychain import (
    Election,
    Graph,
    MarkovChain,
    Partition,
    accept,
    constraints,
    updaters,
)
from gerrychain.metrics import efficiency_gap, mean_median, partisan_gini
from gerrychain.proposals import recom, propose_random_flip
from gerrychain.updaters import cut_edges
from gerrychain.tree import recursive_tree_part
from gerrychain.accept import always_accept


# In[2]:


num_districts = 13
output_dirname = "Run_1"

newdir = "./Outputs/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")
    
graph = Graph.from_json("./data/ga_tract.json")
df = gpd.read_file("./data/ga_2012_tract.gpkg")


# In[3]:


# SUMMING DATA WE WANT IN THE DATAFRAME
import pandas as pd 

new_cols = ['CPOP', 'VAP', 'BVAP', 'nBVAP', 'CVAP', 'BCVAP', 'nBCVAP']

VAP_cols = ['MVAPTotal', 'FVAPTotal']
BVAP_cols = ['MVAPBLACK', 'FVAPBLACK']
CVAP_cols = ['MNativeBornVAPTotal', 'MNaturalizedVAPTotal', 'FNativeBornVAPTotal', 'FNaturalizedVAPTotal']
BCVAP_cols = ['MNativeBornVAPBLACK', 'MNaturalizedVAPBLACK', 'FNativeBornVAPBLACK', 'FNaturalizedVAPBLACK']

df['CPOP'] = pd.to_numeric(df['TOTPOP']-df['NCPOP'])
df['VAP'] = pd.to_numeric(df[VAP_cols].sum(axis=1))
df['BVAP'] = pd.to_numeric(df[BVAP_cols].sum(axis=1))
df['nBVAP'] = df['VAP'] - df['BVAP']
df['CVAP'] = pd.to_numeric(df[CVAP_cols].sum(axis=1))
df['BCVAP'] = pd.to_numeric(df[BCVAP_cols].sum(axis=1))
df['nBCVAP'] = df['CVAP'] - df['BCVAP']


# In[4]:


# ADD NEW DATA TO GRAPH 

graph.add_data(df, columns=new_cols)


# In[9]:


graph.nodes[1]['CVAP']


# In[5]:


# INITIAL PARTITION ASSIGNMENT USING RECURSIVE TREE PARTITION

starts = []

for i in range(1):
    starts.append(recursive_tree_part(graph,range(num_districts),df['CVAP'].sum()/num_districts, "CVAP", .001, 1))
    #starts.append(recursive_tree_part(graph,range(num_districts),df['TOTPOP'].sum()/num_districts, "TOTPOP", .001, 1))


# In[6]:


updater = {
    "population": updaters.Tally("TOTPOP", alias="population"),
    "cut_edges": cut_edges,
    "BVAP":Election("BVAP",{"BVAP":"BVAP","nBVAP":"nBVAP"}),
    "BCVAP":Election("BCVAP",{"BCVAP":"BCVAP","nBCVAP":"nBCVAP"})
}

initial_partitions = []
proposals = []
compactness_bounds = []
chains=[]

for i in range(1):
    initial_partitions.append(Partition(graph,starts[i], updater))
    print("initial partition is made")

    proposals.append(partial(
        recom, pop_col="CVAP", pop_target=df['CVAP'].sum()/num_districts, epsilon=0.01, node_repeats=1 # e = .02
    ))
        #recom, pop_col="TOTPOP", pop_target=df['TOTPOP'].sum()/num_districts, epsilon=0.01, node_repeats=1 # e = .02
    #))

    compactness_bounds.append(constraints.UpperBound(
        lambda p: len(p["cut_edges"]), 2 * len(initial_partitions[i]["cut_edges"])
    ))

    chains.append(MarkovChain(
        proposal=proposals[i],
        constraints=[
            constraints.within_percent_of_ideal_population(initial_partitions[i], .01), compactness_bounds[i] # e = .05
          #constraints.single_flip_contiguous#no_more_discontiguous 
        #constraints.within_percent_of_ideal_population(initial_partitions[i], .3)
        ],
        accept=always_accept,
        initial_state=initial_partitions[i],
        total_steps=10000
    ))


# In[7]:


cuts=[[],[],[],[]]
BVAPS=[[],[],[],[]]
BCVAPS=[[],[],[],[]]

#37 to 55 is opportunity district BVAP range in VA

subdir = "./Outputs/Tract_13Districts_VAP_CVAP/"
os.makedirs(os.path.dirname(subdir + "init.txt"), exist_ok=True)
with open(subdir + "init.txt", "w") as f:
    f.write("Created Folder")

for i in range(1):
    t = 0
    for part in chains[i]:
        cuts[i].append(len(part["cut_edges"]))
        BVAPS[i].append(sorted(part["BVAP"].percents("BVAP")))
        BCVAPS[i].append(sorted(part["BCVAP"].percents("BCVAP")))
        t+=1
    
        if t%100 ==0:
            print("chain",i,"step",t)
            
            df["current"]=df.index.map(dict(part.assignment))
        
            df.plot(column="current",cmap="jet")
            plt.savefig(subdir+"plot"+str(t)+".png")
            plt.close()

            with open(subdir+"assignment"+str(t)+".json", 'w') as jf1:
                json.dump(dict(part.assignment), jf1)
    
    print(f"finished chain {i}")

df["final"]=df.index.map(dict(part.assignment))

df.plot(column="final",cmap="jet")
plt.savefig(subdir+"final.png")
plt.close()


# In[38]:


# Note:
#
# The "enacted plan" is taken from the 2012 congressional district data for 13 districts
# because GA gained a seat iin 2012 to have 14 seats in 2013. 
# 

cd_df = gpd.read_file("./data/ga_2012_CD.shp")


# In[41]:


new_cols = ['CPOP', 'VAP', 'BVAP', 'nBVAP', 'CVAP', 'BCVAP', 'nBCVAP']

VAP_cols = ['MVAPTOT', 'FVAPTOT']
BVAP_cols = ['MVAPBLK', 'FVAPBLK']
CVAP_cols = ['MNVVAPTOT', 'MNLVAPTOT', 'FNVVAPTOT', 'FNLVAPTOT']
BCVAP_cols = ['MNVVAPBLK', 'MNLVAPBLK', 'FNVVAPBLK', 'FNLVAPBLK']

cd_df['CPOP'] = pd.to_numeric(cd_df['TOTPOP']-cd_df['NCPOP'])
cd_df['VAP'] = pd.to_numeric(cd_df[VAP_cols].sum(axis=1))
cd_df['BVAP'] = pd.to_numeric(cd_df[BVAP_cols].sum(axis=1))
cd_df['nBVAP'] = cd_df['VAP'] - cd_df['BVAP']
cd_df['CVAP'] = pd.to_numeric(cd_df[CVAP_cols].sum(axis=1))
cd_df['BCVAP'] = pd.to_numeric(cd_df[BCVAP_cols].sum(axis=1))
cd_df['nBCVAP'] = cd_df['CVAP'] - cd_df['BCVAP']


# In[48]:


enacted_CD112_BCVAP = sorted(cd_df['BCVAP']/cd_df['CVAP'])


# In[46]:


enacted_CD112_BVAP = sorted(cd_df['BVAP']/cd_df['VAP'])


# In[52]:


# PLOT SORTED DISTRICTS OVER BVAP %

c='k'

#37 to 55 is opportunity district BVAP range in VA

plt.figure()
plt.boxplot(
            np.array(BVAPS[0]),
            whis=[1, 99],
            showfliers=False,
            patch_artist=True,
            boxprops=dict(facecolor="None", color=c),
            capprops=dict(color=c),
            whiskerprops=dict(color=c),
            flierprops=dict(color=c, markeredgecolor=c),
            medianprops=dict(color=c),
)

plt.plot([1,2,3,4,5,6,7,8,9,10,11,12,13], enacted_CD112_BVAP, 'o', color="hotpink", label="Enacted (2012)",markersize=10)

plt.axhline(y=.4,color='r',label="40%",linewidth=5)

plt.axhline(y=.45,color='y',label="45%",linewidth=5)

plt.axhline(y=.5,color='g',label="50%",linewidth=5)
plt.plot([],[],color='k',label="ReCom Ensemble")
plt.xlabel("Sorted Districts")
plt.ylabel("BVAP%")

plt.legend()

plt.show()


# PLOT SORTED DISTRICTS OVER CBVAP %

plt.figure()
plt.boxplot(
            np.array(BCVAPS[0]),
            whis=[1, 99],
            showfliers=False,
            patch_artist=True,
            boxprops=dict(facecolor="None", color=c),
            capprops=dict(color=c),
            whiskerprops=dict(color=c),
            flierprops=dict(color=c, markeredgecolor=c),
            medianprops=dict(color=c),
)

plt.plot([1,2,3,4,5,6,7,8,9,10,11,12,13], enacted_CD112_BCVAP, 'o', color="hotpink", label="Enacted (2012)",markersize=10)

plt.axhline(y=.4,color='r',label="40%",linewidth=5)

plt.axhline(y=.45,color='y',label="45%",linewidth=5)

plt.axhline(y=.5,color='g',label="50%",linewidth=5)
plt.plot([],[],color='k',label="ReCom Ensemble")
plt.xlabel("Sorted Districts")
plt.ylabel("BCVAP%")

plt.legend()

plt.show()


# In[ ]:




