"""
Script to find shortest find from a road network by using A* algortihm
"""
import os
from pprint import pprint
import operator

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
    get_spatial_reference
)

# Setting
with_geometry_attribute = True

# Load node and path/edge
data_directory_path = '/home/ismailsunni/Documents/GeoTech/Routing/processed/small_data/'

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

# print('Edges')
# for i in range(len(fids) - 1):
#     node1 = shortest_path[i]
#     node2 = shortest_path[i+1]
#     print(G.edges[node1, node2])

# Create geometry from the edges
print('Create geometry')
# set up the shapefile driver
driver = ogr.GetDriverByName("ESRI Shapefile")
# create the data source
path_file = '/home/ismailsunni/dev/python/routing/a_star_shortest_path.shp'
data_source = driver.CreateDataSource(path_file)

# create the spatial reference
spatial_reference = get_spatial_reference(data_directory_path)

# create the layer
layer = data_source.CreateLayer("A Star Shortest Path", spatial_reference, ogr.wkbLineString)

# Create fields
# fid
layer.CreateField(ogr.FieldDefn("fid", ogr.OFTReal))
# streetID
layer.CreateField(ogr.FieldDefn("streetID", ogr.OFTInteger64))
# length
layer.CreateField(ogr.FieldDefn("length", ogr.OFTReal))
# u
layer.CreateField(ogr.FieldDefn("u", ogr.OFTInteger64))
# v
layer.CreateField(ogr.FieldDefn("v", ogr.OFTInteger64))
# length_sc
layer.CreateField(ogr.FieldDefn("length_sc", ogr.OFTReal))
# order
layer.CreateField(ogr.FieldDefn("order", ogr.OFTInteger))

fields = ['fid', 'streetID', 'length', 'u', 'v', 'length_sc']

# Iterate over the path edges
for i in range(len(fids) - 1):
    node1 = shortest_path[i]
    node2 = shortest_path[i+1]
    # print(node1)
    # print(node2)
    # print(G.edges[node1, node2])
    edge = G.edges[node1, node2]
    feature = ogr.Feature(layer.GetLayerDefn())
    for field in fields:
        feature.SetField(field, edge[field])
    feature.SetField('order', i)
    # Create geometry from the Wkt
    geom = ogr.CreateGeometryFromWkt(edge['Wkt'])
    # Set the feature geometry using the geom
    feature.SetGeometry(geom)
    
    # Create the feature in the layer (shapefile)
    layer.CreateFeature(feature)
    # Dereference the feature
    feature = None

# Save and close the data source
data_source = None

print('fin')