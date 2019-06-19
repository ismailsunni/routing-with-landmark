"""
Script to find shortest find from a road network by using A* algortihm.

    Author      : Ismail Sunni
    Email       : imajimatika@gmail.com
    Date        : Jun 2019
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
    create_path_layer,
    graph_summary
)

def shortest_path_a_star(start_node, end_node, input_data_path, output_file):
    """Main function for A* shortest path
        
        `start_node` and `end_node` are ('key', 'value') format.
        `input_data_path` is a path to directory with nodes and edges layer.
        `output_file` is a path to the output shape file.
    """
    # Read graph
    G = nx.Graph(nx.read_shp(input_data_path, strict=False, geom_attrs=True)) # Read and convert to Graph
    graph_summary(G)

    # Get start and end node
    start = get_nodes(G, start_node[0], start_node[1])[0]
    end = get_nodes(G, end_node[0], end_node[1])[0]
    print("Start node:")
    print_node(G, start)
    print("End node:")
    print_node(G, end)

    # Find shortest path
    shortest_path = nx.astar_path(G, start, end, heuristic=calculate_distance, weight='length')
    fids = nodes_from_path(G, shortest_path, key=start_node[0])
    print('Shortest path: ' + ' - '.join(['%d' % fid for fid in fids]))
    shortest_path_length = nx.astar_path_length(G, start, end, heuristic=calculate_distance, weight='length')
    print('Shortest path length: %f' % shortest_path_length)

    return shortest_path

    # Skip this writing file, move to the wrapper
    # # Write result to a shapefile
    # spatial_reference = get_spatial_reference(input_data_path)
    # create_path_layer(G, shortest_path, output_file, spatial_reference)

    # if os.path.exists(output_file):
    #     return shortest_path
    # else:
    #     return False

if __name__ == "__main__":
    print('Start')

    id_field = 'nodeID'
    input_data_path = '/home/ismailsunni/Documents/GeoTech/Routing/topic_data'
    base_output_file =  '/home/ismailsunni/dev/python/routing/test/output/'
    route_pairs = [
        {
            'name': 'A',
            'start': 4063,
            'end': 33
        },
        {
            'name': 'B',
            'start': 6492,
            'end': 3858
        },
        {
            'name': 'C',
            'start': 870,
            'end': 3102
        },
    ]
    for pair in route_pairs:
        start_node = (id_field, pair['start'])
        end_node = (id_field, pair['end'])
        output_file = os.path.join(base_output_file, '%s.shp' % pair['name'])
        shortest_path_a_star(start_node, end_node, input_data_path, output_file)
    
    print('fin')