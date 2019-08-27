"""
ga_partisan_chain.py:
    this program takes two arguments, the population column on which to balance 
    and the map which to redistrict.  It then runs a chain of 10000 iterations 
    and saves the resulting number of republican seats with respect to the 2016
    senate and presidential elections.

"""


import argparse
from gerrychain import Graph, GeographicPartition, Partition, Election, accept
from gerrychain.updaters import Tally, cut_edges
from gerrychain import MarkovChain
from gerrychain.proposals import recom
from gerrychain.accept import always_accept
from gerrychain import constraints
import geopandas as gpd
import numpy as np
from functools import partial
from gerrychain.tree import recursive_tree_part
import pickle

# from gerrychain.random import random
# from gerrychain.constraints import single_flip_contiguous
# from gerrychain.metrics import polsby_popper
# from gerrychain.constraints import no_vanishing_districts
# from collections import defaultdict, Counter
# from itertools import combinations_with_replacement
# import matplotlib.pyplot as plt
# import networkx as nx
# import pandas
# import math



## Read in 
parser = argparse.ArgumentParser(description="GA Partisan chain run", 
                                 prog="ga_partisan_chain.py")
parser.add_argument("popcol", metavar="population column", type=str,
                    choices=["TOTPOP", "VAP", "CPOP", "CVAP"],
                    help="the population column by which to balance redistricting")
parser.add_argument("map", metavar="map", type=str,
                    choices=["congress", "state_house", "state_senate"],
                    help="the map to redistrict")
args = parser.parse_args()

num_districts_in_map = {"congress" : 14,
                        "state_senate" : 56,
                        "state_house" : 180}

POP_COL = args.popcol
NUM_DISTRICTS = num_districts_in_map[args.map]
ITERS = 10000


## Setup graph, updaters, elections, and initial partition

print("Reading in Data/Graph")

shapefile = "../data/maupped_ga_2016_precincts/maupped_ga_2016_precincts.shp"
df = gpd.read_file(shapefile)

variables = ["ID","FIPS2", "PRES16D", "PRES16R", "PRES16L", "SEN16D", "SEN16R", 
             "SEN16L"]
for x in df.columns:
   if x in variables:
       df[x] = df[x].astype(int)

df["CPOP"] = df["TOTPOP"]-df["NCPOP"]
df["CVAP"] = df["MNVVAPTOT"]+df["MNLVAPTOT"]+df["FNVVAPTOT"]+df["FNLVAPTOT"]

uid = "ID"

# graph = Graph.from_geodataframe(df, ignore_errors=True)
# graph.add_data(df,list(df))
# graph = nx.relabel_nodes(graph, df[uid])
# pickle.dump(graph, open("../data/GA_graph_maupped_precincts.p", "wb"))
# exit(0)

graph = pickle.load(open("../data/GA_graph_maupped_precincts.p", "rb"))


my_updaters = {"population" : Tally(POP_COL, alias="population"),
               "TOTPOP": Tally("TOTPOP", alias="TOTPOP"),
               "VAP": Tally("VAP", alias="VAP"),
               "CPOP": Tally("CPOP", alias="CPOP"),
               "CVAP": Tally("CVAP", alias="CVAP"),
               "cut_edges": cut_edges}
# my_updaters.update(election_updaters)


print("Creating seed plan")

total_pop = sum(df[POP_COL])
ideal_pop = total_pop / NUM_DISTRICTS

cddict = recursive_tree_part(graph=graph, parts=range(NUM_DISTRICTS), 
                             pop_target=ideal_pop, pop_col=POP_COL, epsilon=0.02)

init_partition = Partition(graph,assignment=cddict,updaters=my_updaters)


## Setup chain

proposal = partial(recom, pop_col=POP_COL, pop_target=ideal_pop, epsilon=0.01, 
                   node_repeats=1)

compactness_bound = constraints.UpperBound(lambda p: len(p["cut_edges"]), 
                                             2*len(init_partition["cut_edges"]))

chain = MarkovChain(
        proposal,
        constraints=[
            constraints.within_percent_of_ideal_population(init_partition, 0.02),
            compactness_bound],
        accept=accept.always_accept,
        initial_state=init_partition,
        total_steps=ITERS)


## Run chain

print("Starting Markov Chain")

chain_results = {"cutedges": np.zeros(ITERS),
                 "TOTPOP": np.zeros((ITERS, NUM_DISTRICTS)),
                 "VAP": np.zeros((ITERS, NUM_DISTRICTS)),
                 "CPOP": np.zeros((ITERS, NUM_DISTRICTS)),
                 "CVAP": np.zeros((ITERS, NUM_DISTRICTS))}

for i, part in enumerate(chain):
    chain_results["cutedges"][i] = len(part["cut_edges"])
    chain_results["TOTPOP"][i] = sorted(part["TOTPOP"])
    chain_results["VAP"][i] = sorted(part["VAP"])
    chain_results["CPOP"][i] = sorted(part["CPOP"])
    chain_results["CVAP"][i] = sorted(part["CVAP"])

    if i % 100 == 0:
        print("*", end="", flush=True)
print()


## Save results

print("Saving results")

output = "../data/pop_imbalance_runs/{}_{}_pop_imbalance_chain_results.p".format(POP_COL, args.map)

with open(output, "wb") as f_out:
    pickle.dump(chain_results, f_out)