"""
Script to find shortest find from a road network by using A* algortihm
"""
import os
from pprint import pprint

from osgeo import ogr
from osgeo import osr
import networkx as nx
import matplotlib.pyplot as plt

from utils import (
    calculate_distance, 
    get_nodes, 
    pretty_node, 
    print_dictionary, 
    print_node, 
    nodes_from_path,
    get_spatial_reference,
    create_path_layer
)

# Setting
with_geometry_attribute = True

# Load node and path/edge
data_directory_path = '/home/ismailsunni/dev/python/routing/test/input/'

if not os.path.exists(data_directory_path):
    print('Path %s is exist...' % data_directory_path)

G = nx.Graph(nx.read_shp(data_directory_path, strict=False, geom_attrs=with_geometry_attribute)) # Read and convert to Graph

print('Summary of G:')
print('Number of nodes in G: %s' % G.number_of_nodes())
print('Number of edges in G: %s' % G.number_of_edges())

# Set start and end point
start = get_nodes(G, 'fid', 736)[0]
end = get_nodes(G, 'fid', 750)[0]
print("Start node:")
print_node(G, start)
print("End node:")
print_node(G, end)

# Sample edges
# print('edges')
# e = list(G.edges)[0]
# print(G.edges[e])

# A*
shortest_path = nx.astar_path(G, start, end, heuristic=calculate_distance, weight='length')
fids = nodes_from_path(G, shortest_path, key='fid')
print('Shortest path: ' + ' - '.join(['%d' % fid for fid in fids]))
shortest_path_length = nx.astar_path_length(G, start, end, heuristic=calculate_distance, weight='length')
print('Shortest path length: %f' % shortest_path_length)

path_file = '/home/ismailsunni/dev/python/routing/test/output/a_star_shortest_path.shp'
spatial_reference = get_spatial_reference(data_directory_path)
create_path_layer(G, shortest_path, path_file, spatial_reference)


print('fin')