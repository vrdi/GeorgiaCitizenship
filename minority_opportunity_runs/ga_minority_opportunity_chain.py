"""
ga_minority_opportunity_chain.py:
    this program takes two arguments, the population column on which to balance 
    and the map which to redistrict.  It then runs a chain of 10000 iterations 
    and saves the resulting data about Black minority-opportunity districts and
    Black-Hispanic collation minority-opportunity districts.

    In particular, it save a pickle of a dictionary that contains the number of
    cut edges and the sorted district percentages of BPOP, BVAP, BCPOP, BCVAP,
    BHPOP, BHVAP, BHCPOP, and BHCVAP for each step in the chain.

"""


import argparse
from gerrychain import Graph, GeographicPartition, Partition, Election, accept
from gerrychain.updaters import Tally, cut_edges
import geopandas as gpd
import pandas as pd
import numpy as np
from gerrychain import MarkovChain
from gerrychain.proposals import recom
from gerrychain.accept import always_accept
from gerrychain import constraints
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
# import math



## Read in 
parser = argparse.ArgumentParser(description="GA Minority Opportunity chain run", 
                                 prog="ga_minority_opportunity_chain.py")
parser.add_argument("popcol", metavar="population column", type=str,
                    choices=["TOTPOP", "VAP", "CPOP", "CVAP"],
                    help="the population column by which to balance redistricting")
parser.add_argument("map", metavar="map", type=str,
                    choices=["congress", "congress_2010",
                             "state_house", "state_senate"],
                    help="the map to redistrict")
args = parser.parse_args()

num_districts_in_map = {"congress" : 14,
                        "congress_2010" : 13,
                        "state_senate" : 56,
                        "state_house" : 180}

POP_COL = args.popcol
NUM_DISTRICTS = num_districts_in_map[args.map]
ITERS = 10000


## Setup graph, updaters, elections, and initial partition

print("Reading in Data/Graph")

# shapefile = "../data/maupped_ga_2016_precincts/maupped_ga_2016_precincts.shp"
df = gpd.read_file("../data/ga_2012_tract.shp")
graph = Graph.from_json("../data/ga_tract.json")

new_cols = ["CPOP", "VAP", "BVAP", "nBVAP", "CVAP", "BCVAP", "nBCVAP",
            "BHVAP", "nBHVAP", "BHCVAP", "nBHCVAP", "BHPOP", "nBHPOP"]

BCPOP_cols = ["MNVVAPBLK", "MNLVAPBLK", "FNVVAPBLK", "FNLVAPBLK", 
              "MNVU18BLK", "MNLU18BLK", "FNVU18BLK", "FNLU18BLK"]
VAP_cols = ["MVAPTOT", "FVAPTOT"]
BVAP_cols = ["MVAPBLK", "FVAPBLK"]
CVAP_cols = ["MNVVAPTOT", "MNLVAPTOT", "FNVVAPTOT", "FNLVAPTOT"]
BCVAP_cols = ["MNVVAPBLK", "MNLVAPBLK", "FNVVAPBLK", "FNLVAPBLK"]

HCPOP_cols = ["MNVVAPHISP", "MNLVAPHISP", "FNVVAPHISP", "FNLVAPHISP", 
              "MNVU18HISP", "MNLU18HISP", "FNVU18HISP", "FNLU18HISP"]
HVAP_cols = ["MVAPHISP", "FVAPHISP"]
HCVAP_cols = ["MNVVAPHISP", "MNLVAPHISP", "FNVVAPHISP", "FNLVAPHISP"]


df["BHPOP"] = df["BPOP"] + df["HISP"]
df["nBHPOP"] = df["TOTPOP"] - df["BHPOP"]
df["nBPOP"] = df["TOTPOP"] - df["BPOP"]

df["CPOP"] = pd.to_numeric(df["TOTPOP"]-df["NCPOP"])
df["BCPOP"] = pd.to_numeric(df[BCPOP_cols].sum(axis=1))
df["nBCPOP"] = df["CPOP"] - df["BCPOP"]

df["VAP"] = pd.to_numeric(df[VAP_cols].sum(axis=1))
df["BVAP"] = pd.to_numeric(df[BVAP_cols].sum(axis=1))
df["nBVAP"] = df["VAP"] - df["BVAP"]

df["CVAP"] = pd.to_numeric(df[CVAP_cols].sum(axis=1))
df["BCVAP"] = pd.to_numeric(df[BCVAP_cols].sum(axis=1))
df["nBCVAP"] = df["CVAP"] - df["BCVAP"]

df["BHCPOP"] = pd.to_numeric(df["BCPOP"] + df[HCPOP_cols].sum(axis=1))
df["nBHCPOP"] = df["CPOP"] - df["BHCPOP"]

df["BHVAP"] = pd.to_numeric(df["BVAP"] + df[HVAP_cols].sum(axis=1))
df["nBHVAP"] = df["VAP"] - df["BHVAP"]

df["BHCVAP"] = pd.to_numeric(df["BCVAP"] + df[HCVAP_cols].sum(axis=1))
df["nBHCVAP"] = df["CVAP"] - df["BHCVAP"]


graph.add_data(df, columns=new_cols)




elections = [Election("BPOP",{"BPOP":"BPOP","nBPOP":"nBPOP"}),
             Election("BCPOP",{"BCPOP":"BCPOP","nBCPOP":"nBCPOP"}),
             Election("BVAP",{"BVAP":"BVAP","nBVAP":"nBVAP"}),
             Election("BCVAP",{"BCVAP":"BCVAP","nBCVAP":"nBCVAP"}),
             Election("BHPOP",{"BHPOP":"BHPOP","nBHPOP":"nBHPOP"}),
             Election("BHCPOP",{"BHCPOP":"BHCPOP","nBHCPOP":"nBHCPOP"}),
             Election("BHVAP",{"BHVAP":"BHVAP","nBHVAP":"nBHVAP"}),
             Election("BHCVAP",{"BHCVAP":"BHCVAP","nBHCVAP":"nBHCVAP"})]

my_updaters = {"population" : Tally(POP_COL, alias="population"), 
               "cut_edges": cut_edges}
election_updaters = {election.name: election for election in elections}
my_updaters.update(election_updaters)


print("Creating seed plan")

total_pop = sum(df[POP_COL])
ideal_pop = total_pop / NUM_DISTRICTS

cddict = recursive_tree_part(graph=graph, parts=range(NUM_DISTRICTS), 
                             pop_target=ideal_pop, pop_col=POP_COL, epsilon=0.02)

init_partition = Partition(graph, assignment=cddict, updaters=my_updaters)


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
                 "BPOP": np.zeros((ITERS, NUM_DISTRICTS)),
                 "BVAP": np.zeros((ITERS, NUM_DISTRICTS)),
                 "BCPOP": np.zeros((ITERS, NUM_DISTRICTS)),
                 "BCVAP": np.zeros((ITERS, NUM_DISTRICTS)),
                 "BHPOP": np.zeros((ITERS, NUM_DISTRICTS)),
                 "BHVAP": np.zeros((ITERS, NUM_DISTRICTS)),
                 "BHCPOP": np.zeros((ITERS, NUM_DISTRICTS)),
                 "BHCVAP": np.zeros((ITERS, NUM_DISTRICTS)),}

for i, part in enumerate(chain):
    chain_results["cutedges"][i] = len(part["cut_edges"])
    chain_results["BPOP"][i] = sorted(part["BPOP"].percents("BPOP"))
    chain_results["BVAP"][i] = sorted(part["BVAP"].percents("BVAP"))
    chain_results["BCPOP"][i] = sorted(part["BCPOP"].percents("BCPOP"))
    chain_results["BCVAP"][i] = sorted(part["BCVAP"].percents("BCVAP"))
    chain_results["BHPOP"][i] = sorted(part["BHPOP"].percents("BHPOP"))
    chain_results["BHVAP"][i] = sorted(part["BHVAP"].percents("BHVAP"))
    chain_results["BHCPOP"][i] = sorted(part["BHCPOP"].percents("BHCPOP"))
    chain_results["BHCVAP"][i] = sorted(part["BHCVAP"].percents("BHCVAP"))

    if i % 100 == 0:
        print("*", end="", flush=True)
print()


## Save results

print("Saving results")

output = "../data/minority_opportunity_runs/{}_{}_min_opp_chain_results.p".format(POP_COL, args.map)

with open(output, "wb") as f_out:
    pickle.dump(chain_results, f_out)

# output_senate = "../data/partisan_data/{}_{}_GOP_seats_senate_2016.npy".format(POP_COL, args.map)
# output_pres = "../data/partisan_data/{}_{}_GOP_seats_pres_2016.npy".format(POP_COL, args.map)
# output_cutedges =  "../data/partisan_data/{}_{}_cut_edges.npy".format(POP_COL, args.map)

# np.save(output_senate, SENwins)
# np.save(output_pres, PRESwins)
# np.save(output_cutedges, cutedges)