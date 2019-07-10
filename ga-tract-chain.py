# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 10:59:39 2019

@author: Katherine
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



num_districts = 14
output_dirname = "Run_1"

newdir = "./Outputs/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")
    
# Dual graph: https://github.com/vrdi/vrdi-graphs/blob/master/utah.json
# Precinct shp: MGGG-states repo
graph = Graph.from_json("./data/ga_tract.json")
df = gpd.read_file("./data/ga_tract.shp")



starts = []
tot_pop = df['TOTPOP'].sum() 
print(tot_pop)
graph.nodes[0]['TOTPOP']

for i in range(1):
    starts.append(recursive_tree_part(graph,range(num_districts),tot_pop/num_districts, "TOTPOP", .001, 1))


#election = Election(
   # "2016 Senate", {"Democratic": "SEN16D", "Republican": "SEN16R"}, alias="2016_Sen")

updater = {
    "population": updaters.Tally("TOTPOP", alias="population"),
    "cut_edges": cut_edges,
}

initial_partitions = []
proposals = []
compactness_bounds = []
chains=[]

for i in range(1):
    initial_partitions.append(Partition(graph,starts[i], updater))
    print("initial partition is made")

    proposals.append(partial(
        recom, pop_col="TOTPOP", pop_target=tot_pop/num_districts, epsilon=0.01, node_repeats=1 # e = .02
    ))

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
        total_steps=100
    ))


cuts=[[],[],[],[]]
BVAP_percents=[[],[],[],[]]
BVAPS=[[],[],[],[]]
nBVAPS=[[],[],[],[]]


#37 to 55 is opportunity district BVAP range 

for i in range(1):
    t = 0
    for part in chains[i]:
        cuts[i].append(len(part["cut_edges"]))
      
        t+=1
    
        if t%100 ==0:
            print("chain",i,"step",t)
            
            df["current"]=df.index.map(dict(part.assignment))
        
            df.plot(column="current",cmap="jet")
            #plt.savefig(newdir+"/Benchmarks/"+"plot"+str(t)+".png")
            plt.close()

            with open(newdir+"/Benchmarks/"+"assignment"+str(t)+".json", 'w') as jf1:
                json.dump(dict(part.assignment), jf1)
    
    print(f"finished chain {i}")

df["final"]=df.index.map(dict(part.assignment))

df.plot(column="final",cmap="jet")
plt.savefig(newdir+"final.png")
plt.close()


# In[ ]:


#print(PGs[0])
len(PGs[0])
minPG = np.min(PGs[0])
print("min: ", minPG)
print("index: ", PGS[0].index(minPG))


# In[75]:


colors = ['hotpink','goldenrod','green','purple']
labels= ['Block Group','COUSUB','Tract','County']
#colors = ['green']
#labels= ['Block Group']
plt.figure()
for i in range(1):
    sns.distplot(PGs[0],kde=False, color=colors[i],label='Precinct')
plt.legend()
plt.ylabel("Frequency")
plt.xlabel("Partisan Gini values")
plt.show()


# In[104]:


#have no idea what this was doing
#plt.figure()
#plt.hist(cuts)
#plt.show()
c='k'

#37 to 55 is opportunity district BVAP range 

plt.figure()
plt.boxplot(
            np.array(BVAP_percents[0]),
            whis=[1, 99],
            showfliers=False,
            patch_artist=True,
            boxprops=dict(facecolor="None", color=c),
            capprops=dict(color=c),
            whiskerprops=dict(color=c),
            flierprops=dict(color=c, markeredgecolor=c),
            medianprops=dict(color=c),
)

plt.plot([1,2,3,4,5,6,7],[.233,.268,.268,.297,.322,.337,.621], 'o', color="hotpink", label="Enacted",markersize=10)

plt.axhline(y=.4,color='r',label="40%",linewidth=5)

plt.axhline(y=.45,color='y',label="45%",linewidth=5)

plt.axhline(y=.5,color='g',label="50%",linewidth=5)
plt.plot([],[],color='k',label="ReCom Ensemble")
plt.xlabel("Sorted Districts")
plt.ylabel("BVAP%")

plt.legend()

plt.show()


# In[158]:


def plot_partition(partition, geom_df, geom_id_col="GEOID10"):
    import pandas as pd
    print (str(x) for x in list(partition.assignment))
    color_df = pd.DataFrame({#geom_id_col+"_tmp": [str(x) for x in list(partition.assignment)],
                         "part":list(initial_partitions[0].assignment.values())})
    #geom_df[geom_id_col+"_tmp"] = geom_df.index.tolist()
    asg = initial_partitions[0].assignment
    geom_df["part"] = [asg[x] for x in sorted(asg)]
    geom_df.plot(column="part")
    
len(BG_df)


# In[159]:


with open("./Data/Outputs/BG_CD_10000/assignment10000.json") as json_file:
    final_json = json.load(json_file)

final_assignment = {}
for k, v in final_json.items():
    final_assignment[int(k)] = v


final_part = Partition(BG_graph, final_assignment)
plot_partition(final_part, BG_df)

BG_graph.nodes()
#BG_df.head()


# In[105]:



matrix = np.reshape(np.array(BVAPS[0]),(7,int(len(BVAPS[0])/7)))

import pandas as pd

mydf = pd.DataFrame(matrix.transpose())
mydf


#df.merge(assignment dict) bc its keyed on nodes! ! 


# In[ ]: