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


def make_dual_graph(st, year):
    """
    Takes a 2-letter state postal code abbreviation (e.g. GA for Georgia), makes a dual graph of its shapefile, and writes the dual graph to a JSON
    
    Arguments:
    st -- 2 letter state postal code
    """
    
    # Fold state postal code to lowercase:
    st = st.lower()
    
    ##2016 Census Tract- TigerLine File for the appropriate state, follow link to download
    geo = gpd.read_file("./data/"+st+"_"+str(year)+"_tract.gpkg")
    graph = Graph.from_geodataframe(geo) #if graph is successfully generated, we should be able to run chain
    graph.add_data(geo, columns = geo.columns )
    #nx.is_connected(graph) # if returns true, graph is connected
    graph.to_json("./data/"+st+"_tract.json")


if __name__ == "__main__":
    make_dual_graph('GA', 2012)