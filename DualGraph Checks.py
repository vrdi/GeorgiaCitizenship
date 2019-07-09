#imports 
from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges
import networkx as nx
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

##2016 Census Tract- TigerLine File for Georgia, follow link to download
geo = gpd.read_file("https://www2.census.gov/geo/tiger/TIGER2010/BG/2010/tl_2010_13_bg10/tl_2010_13_bg10.shp")

graph = Graph.from_file("""YOUR FILE PATH""/tl_2010_13_bg10/tl_2010_13_bg10.shp") #if graph is successfully generated, we should be able to run chain

nx.is_connected(graph) # if returns true, graph is connected
