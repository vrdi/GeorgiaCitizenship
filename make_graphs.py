import pickle
from gerrychain import Graph

# graph = Graph.from_file("data/GA_blockgroups_2018/GA_blockgroups_all_pops.shp")
# with open("graphs/GA_blockgroup_graph.p", "wb") as fout:
# 	pickle.dump(graph, fout)

graph = Graph.from_file("data/GA_precincts_all_pops/GA_precincts_2016.shp")
with open("graphs/GA_precincts_2016_graph.p", "wb") as fout:
    pickle.dump(graph, fout)

# graph = Graph.from_file("data/GA_precincts_all_pops/GA_precincts_2018.shp")
# with open("graphs/GA_precincts_2018_graph.p", "wb") as fout:
#     pickle.dump(graph, fout)