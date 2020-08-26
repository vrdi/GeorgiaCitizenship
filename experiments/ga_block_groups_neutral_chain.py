import argparse
import geopandas as gpd
import numpy as np
from functools import partial
import pickle

## Set up argument parser

parser = argparse.ArgumentParser(description="Neutral blockgroup ensemble for GA", 
                                 prog="ga_block_groups_neutral_chain.py")
parser.add_argument("map", metavar="map", type=str,
                    choices=["congress", "congress_2000",
                             "state_house", "state_senate"],
                    help="the map to redistrict")
parser.add_argument("n", metavar="iterations", type=int,
                    help="the number of plans to sample")
parser.add_argument("popcol", metavar="population column", type=str,
                    choices=["TOTPOP", "VAP", "CPOP", "CVAP"],
                    help="the population column by which to balance redistricting")
parser.add_argument("--i", metavar="run number", type=int, default=0,
                    help="which chain run is this?")
args = parser.parse_args()

from gerrychain.random import random
random.seed(args.i)
from gerrychain import Graph, GeographicPartition, Partition, Election, accept
from gerrychain.updaters import Tally, cut_edges
from gerrychain import MarkovChain
from gerrychain.proposals import recom
from gerrychain.accept import always_accept
from gerrychain import constraints
from gerrychain.tree import recursive_tree_part



num_districts_in_map = {"congress" : 14,
                        "congress_2000" : 13,
                        "state_senate" : 56,
                        "state_house" : 180}

epsilons = {"congress" : 0.01,
            "congress_2000" : 0.01,
            "state_senate" : 0.02,
            "state_house" : 0.05} 

POP_COL = "{}18".format(args.popcol)
NUM_DISTRICTS = num_districts_in_map[args.map]
ITERS = args.n
EPS = epsilons[args.map]
DEMO_COLS = ["TOTPOP", "VAP", "CPOP", "CVAP", 
             "BPOP", "HPOP", "WPOP", "BPOP_perc", "HPOP_perc", "WPOP_perc",
             "BCPOP", "HCPOP", "WCPOP", "BCPOP_perc", "HCPOP_perc", "WCPOP_perc",
             "BCVAP", "HCVAP", "WCVAP", "BCVAP_perc", "HCVAP_perc", "WCVAP_perc"]

## Pull in graph and set up updaters

print("Reading in Data/Graph")

with open("../graphs/GA_blockgroup_graph.p", "rb") as f_in:
    graph = pickle.load(f_in)


ga_updaters = {"population" : Tally(POP_COL, alias="population"),
               "cut_edges": cut_edges,
               "TOTPOP": Tally("TOTPOP18", alias="TOTPOP"),
               "VAP": Tally("VAP18", alias="VAP"),
               "CPOP": Tally("CPOP18", alias="CPOP"),
               "CVAP": Tally("CVAP18", alias="CVAP"),
               "BPOP": Tally("NH_BLACK18", alias="BPOP"),
               "HPOP": Tally("HISP18", alias="HPOP"),
               "WPOP": Tally("NH_WHITE18", alias="WPOP"),
               "BCPOP": Tally("BCPOP18", alias="BCPOP"),
               "HCPOP": Tally("HCPOP18", alias="HCPOP"),
               "WCPOP": Tally("WCPOP18", alias="WCPOP"),
               "BCVAP": Tally("BCVAP18", alias="BCVAP"),
               "HCVAP": Tally("HCVAP18", alias="HCVAP"),
               "WCVAP": Tally("WCVAP18", alias="WCVAP"),
               "BPOP_perc": lambda p: {k: (v / p["TOTPOP"][k]) for k, v in p["BPOP"].items()},
               "HPOP_perc": lambda p: {k: (v / p["TOTPOP"][k]) for k, v in p["HPOP"].items()},
               "WPOP_perc": lambda p: {k: (v / p["TOTPOP"][k]) for k, v in p["WPOP"].items()},
               "BCPOP_perc": lambda p: {k: (v / p["CPOP"][k]) for k, v in p["BCPOP"].items()},
               "HCPOP_perc": lambda p: {k: (v / p["CPOP"][k]) for k, v in p["HCPOP"].items()},
               "WCPOP_perc": lambda p: {k: (v / p["CPOP"][k]) for k, v in p["WCPOP"].items()},
               "BCVAP_perc": lambda p: {k: (v / p["CVAP"][k]) for k, v in p["BCVAP"].items()},
               "HCVAP_perc": lambda p: {k: (v / p["CVAP"][k]) for k, v in p["HCVAP"].items()},
               "WCVAP_perc": lambda p: {k: (v / p["CVAP"][k]) for k, v in p["WCVAP"].items()},
               }


## Create seed plan

print("Creating seed plan")

total_pop = sum([graph.nodes[n][POP_COL] for n in graph.nodes])
ideal_pop = total_pop / NUM_DISTRICTS

if args.map != "state_house":
    cddict = recursive_tree_part(graph=graph, parts=range(NUM_DISTRICTS), 
                                 pop_target=ideal_pop, pop_col=POP_COL, epsilon=EPS)
else:
    with open("GA_house_seed_part_0.05.p", "rb") as f:
        cddict = pickle.load(f)

init_partition = Partition(graph, assignment=cddict, updaters=ga_updaters)


while(not constraints.within_percent_of_ideal_population(init_partition, EPS)(init_partition)):
    cddict = recursive_tree_part(graph=graph, parts=range(NUM_DISTRICTS), 
                                 pop_target=ideal_pop, pop_col=POP_COL, epsilon=EPS)
    init_partition = Partition(graph, assignment=cddict, updaters=ga_updaters)


## Setup chain

proposal = partial(recom, pop_col=POP_COL, pop_target=ideal_pop, epsilon=EPS, 
                   node_repeats=1)

compactness_bound = constraints.UpperBound(lambda p: len(p["cut_edges"]), 
                                           2*len(init_partition["cut_edges"]))

chain = MarkovChain(
        proposal,
        constraints=[
            constraints.within_percent_of_ideal_population(init_partition, EPS),
            compactness_bound],
        accept=accept.always_accept,
        initial_state=init_partition,
        total_steps=ITERS)


## Run chain

print("Starting Markov Chain")

def init_chain_results():
    data = {"cutedges": np.zeros(ITERS)}
    parts = {"samples": []}


    for c in DEMO_COLS:
        data[c] = np.zeros((ITERS, NUM_DISTRICTS))

    return data, parts

def tract_chain_results(data, part, i):
    data["cutedges"][i] = len(part["cut_edges"])

    for c in DEMO_COLS:
        data[c] = sorted(part[c].values())


def update_saved_parts(parts, part):
    parts["samples"].append(part.assignment)

chain_results, parts = init_chain_results()

for i, part in enumerate(chain):
    chain_results["cutedges"][i] = len(part["cut_edges"])
    tract_chain_results(chain_results, part, i)

    if i % (ITERS / 10) == 99: update_saved_parts(parts, part)
    if i % 1000 == 0: print("*", end="", flush=True)
print()

## Save results

print("Saving results")

output = "/cluster/tufts/mggg/jmatth03/Georgia/GA_blockgroups_{}_{}_{}_{}.p".format(args.map, POP_COL, ITERS, args.i)
output_parts = "/cluster/tufts/mggg/jmatth03/Georgia/GA_blockgroups_{}_{}_{}_{}_parts.p".format(args.map, POP_COL, ITERS, args.i) 

with open(output, "wb") as f_out:
    pickle.dump(chain_results, f_out)

with open(output_parts, "wb") as f_out:
    pickle.dump(parts, f_out)
