# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 10:53:35 2019

@author: Katherine
"""
from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges
import networkx as nx
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

##2016 Census Tract- TigerLine File for Georgia, follow link to download
geo = gpd.read_file("./data/ga_tract.shp")

graph = Graph.from_geodataframe(geo) #if graph is successfully generated, we should be able to run chain
graph.add_data(geo, columns = geo.columns )
nx.is_connected(graph) # if returns true, graph is connected

graph.to_json("./data/ga_tract.json")
