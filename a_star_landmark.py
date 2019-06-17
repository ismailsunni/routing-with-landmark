"""
Script to find shortest find from a road network by using A* algortihm.

    Author      : Ismail Sunni
    Email       : imajimatika@gmail.com
    Date        : Jun 2019
"""
import os
from pprint import pprint
import operator
from copy import deepcopy

from osgeo import ogr, osr

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

    # Get landmark node
    landmark_nodes = get_nodes(G, 'landmark', 1)
    for landmark_node in landmark_nodes:
        print(G.node[landmark_node]['nodeID'], G.node[landmark_node]['landmark'])

    # Remove landmark that has bigger distance than the starting point to end
    #TODO: ????

    # Get transit node
    current_node = start
    unvisited_landmarks = deepcopy(landmark_nodes)
    path = [start]
    finish = False
    while not finish:
        current_distance_to_end = calculate_distance(current_node, end)

        # order distance
        # get distance for all unvisited landmarks from the current node
        landmark_distance_dict = {node: calculate_distance(current_node, node) for node in unvisited_landmarks}
        # sort the distance
        sorted_landmark_distance_dict = sorted(landmark_distance_dict.items(), key=operator.itemgetter(1))
        for landmark_distance in sorted_landmark_distance_dict:
            # get landmark to end distance
            landmark_end_distance = calculate_distance(landmark_distance[0], end)
            # compare the `current_node to end distance` with the `landmark to end distance`
            # TODO: ????
            if current_distance_to_end < landmark_end_distance or calculate_distance(current_node, landmark_distance[0]) > current_distance_to_end:
                # the current node distance 
                finish = True
                continue
            else:
                path.append(landmark_distance[0])
                current_node = landmark_distance[0]
                unvisited_landmarks.remove(current_node)
                finish = False
                break
    print('Path')
    path.append(end)
    for landmark_node in path:
        print(G.node[landmark_node]['nodeID'], G.node[landmark_node]['landmark'], landmark_node)
    
    # Build full path from the path using A*
    full_path = []
    i = 0
    for i in range(len(path) - 1):
        shortest_landmark_path = nx.astar_path(G, path[i], path[i+1], heuristic=calculate_distance, weight='length')
        full_path.extend(shortest_landmark_path[:-1])

    # Adding end node
    full_path.append(end)
    # print('Full path')
    # for node in full_path:
    #     print(G.node[node]['nodeID'], G.node[node]['landmark'], node)

    # Clean path from duplicated node, this algorithm work since the path is continue
    if len(full_path) != len(set(full_path)):
        unduplicate_path = []
        skip = False
        current_node = None
        for node in full_path:
            if not skip:
                if full_path.count(node) == 1:
                    # Always add node with single occurence
                    unduplicate_path.append(node)
                else:
                    # Add the first node that has more than one occurence
                    unduplicate_path.append(node)
                    # Mark skip as true for the next nodes
                    skip = True
                    # Store the first duplicate node
                    current_node = node
            else:
                if node == current_node:
                    # Found another current_node
                    # Remove the skip flag
                    skip = False
                    current_node = None
                else:
                    # Always skip until found another current_node
                    pass

        full_path = unduplicate_path

    # Write result to a shapefile
    spatial_reference = get_spatial_reference(input_data_path)
    create_path_layer(G, full_path, output_file, spatial_reference)

    if os.path.exists(output_file):
        return output_file
    else:
        return False

if __name__ == "__main__":
    print('Start')

    from qgis.core import QgsApplication, QgsVectorLayer, QgsPointXY
    
    QgsApplication.setPrefixPath('/usr', True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

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
        output_file = os.path.join(base_output_file, 'landmark_%s.shp' % pair['name'])
        shortest_path_a_star(start_node, end_node, input_data_path, output_file)
    
    print('fin')
