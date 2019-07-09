#imports 
from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges
import networkx as nx

graph = Graph.from_file("""YOUR FILE PATH""/tl_2010_13_bg10/tl_2010_13_bg10.shp") #if graph is successfully generated, we should be able to run chain

nx.is_connected(graph) # if returns true, graph is connected
