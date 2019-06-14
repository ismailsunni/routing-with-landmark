"""
Script to find shortest find from a road network by using A* algortihm
"""
import os
from pprint import pprint
import operator

import networkx as nx
import matplotlib.pyplot as plt

from utils import calculate_distance, get_nodes, pretty_node, print_dictionary, print_node

# Load node and path/edge
data_directory_path = '/home/ismailsunni/Documents/GeoTech/Routing/processed/small_data/'

if not os.path.exists(data_directory_path):
    print('Path %s is exist...' % data_directory_path)

G = nx.Graph(nx.read_shp(data_directory_path, strict=False, geom_attrs=False)) # Read and convert to Graph

print('Summary of G:')
print('Number of nodes in G: %s' % G.number_of_nodes())
print('Number of edges in G: %s' % G.number_of_edges())

# Set start and end point
start = get_nodes(G, 'fid', 736)[0]
end = get_nodes(G, 'fid', 741)[0]
print("Start node:")
print_node(G, start)
print("End node:")
print_node(G, end)

print('fin')