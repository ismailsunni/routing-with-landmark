"""
Utilities functions for A* algorithm
"""

from osgeo import ogr, osr

def get_nodes(G, key, value):
    """Return list of nodes that has attribute key = value"""
    result_nodes = []
    for node in G.nodes:
        if G.node[node].get(key) == value:
            result_nodes.append(node)
    return result_nodes

def pretty_node(node):
    """Helper to convert node to string"""
    return '(%s, %s)' % node

def print_dictionary(dictionary, prefix=''):
    """Helper to print simple dictionary."""
    for k, v in dictionary.items():
        print("%s%s: %s" % (prefix, k, v))

def print_node(graph, node):
    """Helper to print `node` from `graph` with the attribute"""
    print("Key: %s" % pretty_node(node))
    print_dictionary(graph.node[node], prefix='\t')

def calculate_distance(a, b):
    """Helper function to calculate the distance between node a and b."""
    (x1, y1) = a
    (x2, y2) = b
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

def nodes_from_path(G, path, key=''):
    """Helper to get list of node from a path with key"""
    if not key:
        return path
    else:
        keys = [G.node[node][key] for node in path]
        return keys

def get_spatial_reference(path):
    """Helper to get spatial reference from a path of layer"""
    layers = ogr.Open(path)
    if layers is None:
        raise RuntimeError("Unable to open {}".format(path))
    for layer in layers:
        spatial_reference = layer.GetSpatialRef()
        if spatial_reference:
            break
    return spatial_reference

if __name__ == "__main__":
    path = '/home/ismailsunni/Documents/GeoTech/Routing/processed/small_data/'
    spatial_reference = get_spatial_reference(path)
    print(spatial_reference)
    print(spatial_reference.exportToEPSG())
    print('fin')
