"""
Script to find shortest find from a road network by using A* algortihm with landmarks as a transit node.
"""
import os
from pprint import pprint
import networkx as nx
import matplotlib.pyplot as plt

def get_nodes(G, key, value):
    """Return list of nodes that has attribute key = value"""
    result_nodes = []
    for node in G.nodes:
        if G.node[node].get(key) == value:
            result_nodes.append(node)
    return result_nodes
def pretty_node(node):
    """Helper to conver node to string"""
    return '(%s, %s)' % node


def calculate_distance(a, b):
    """Helper function to calculate the distance between node a and b."""
    (x1, y1) = a
    (x2, y2) = b
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

road_path = '/home/ismailsunni/Documents/GeoTech/Routing/processed/small_data/'

if os.path.exists(road_path):
    print('Path exist...')

G = nx.Graph(nx.read_shp(road_path, strict=False, geom_attrs=False)) # Read and convert to Graph
# nx.draw(G)

print(len(G.nodes))

# Start and end node
start = get_nodes(G, 'fid', 736)[0]
end = get_nodes(G, 'fid', 741)[0]
print(start)
print("Start node: %s" % pretty_node(start))
pprint(G.node[start])
print("End node: %s" % pretty_node(end))
pprint(G.node[end])
# for e in G.edges(data=True):
#     print(e)

# Draw G graph
# nx.draw(G)
# plt.show()

# Get landmarks node
landmarks = get_nodes(G, 'landmark', 1)
print('Landmarks')
for landmark in landmarks:
    print(pretty_node(landmark))

# Create landmark graph
landmark_graph = nx.Graph()
landmark_graph.add_nodes_from(landmarks)
landmark_graph.add_node(start)
landmark_graph.add_node(end)
for landmark in landmark_graph.nodes:
    landmark_graph.node[landmark]['fid'] = G.node[landmark]['fid']

# Find landmarks that give smallest sum distance from start to end
# current_node = start
# unvisited_landmarks = list(landmarks)
# visited_landmarks = []

# while (current_node != end):
#     shortest_sum_distance = 9999999
#     potential_landmark = None
#     for landmark in unvisited_landmarks:
#         start_distance = calculate_distance(current_node, landmark)
#         end_distance = calculate_distance(end, landmark)
#         if shortest_sum_distance > (start_distance + end_distance):
#             shortest_sum_distance = (start_distance + end_distance)
#             potential_landmark = landmark
    
#     unvisited_landmarks.remove(potential_landmark)
#     visited_landmarks.append(potential_landmark)
#     current_node = potential_landmark

# print('Visited landmarks:')
# print(visited_landmarks)

# Add edges for all pairs
for node1 in landmark_graph.nodes:
    for node2 in landmark_graph.nodes:
        # if node1 == node2:
        #     continue
        if node1 == start and node2 == end:
            continue
        if node2 == start and node1 == end:
            continue
        if landmark_graph.node[node1]['fid'] >= landmark_graph.node[node2]['fid']:
            continue
        try:
            distance = nx.shortest_path_length(G, node1, node2, weight='length')
            landmark_graph.add_edge(node1, node2, weight=distance)
        except nx.exception.NetworkXNoPath as e:
            print('Unreachable: %s to %s' % (landmark_graph.node[node1]['fid'], landmark_graph.node[node2]['fid']))
            pass


# for e in landmark_graph.edges(data=True):
#     print(e)

# Calculate A* path from landmark_graph
landmark_path = nx.astar_path(landmark_graph, start, end, heuristic=calculate_distance, weight='weight')
landmark_path_distance = nx.astar_path_length(landmark_graph, start, end, heuristic=calculate_distance, weight='weight')
print(landmark_path)
print([landmark_graph.node[l]['fid'] for l in landmark_path])
print(landmark_path_distance)


# show landmark graph
pos = nx.shell_layout(landmark_graph)
nx.draw_networkx_nodes(landmark_graph, pos)
labels = nx.get_node_attributes(landmark_graph, 'fid')
nx.draw_networkx_labels(landmark_graph, pos, labels=labels, font_size=16, font_color='r')
nx.draw_networkx_edges(landmark_graph, pos)
edge_labels = nx.get_edge_attributes(landmark_graph, 'weight')
edge_labels = {k:int(v) for k, v in edge_labels.items()}
nx.draw_networkx_edge_labels(landmark_graph, pos, edge_labels=edge_labels)

# nx.draw(landmark_graph)
plt.show()

# path = nx.astar_path(G, start, end, heuristic=dist, weight='length') 
# print(path)

# Get start and end
# Create graph from landmarks + start + end
# Get route: start -> (landmarks*) -> end
# For each path, find A* route path
    # start -> landmark_1
    # landmark_1 -> landmark_2
    # landmark_2 -> ...
    # ... -> landmark_n
    # landmark_n -> end
# Create total route


