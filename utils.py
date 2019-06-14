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

def create_path_layer(G, path, output_file, spatial_reference):
    """Helper to create layer from a path"""
    # Create geometry from the edges
    print('Create geometry')
    # set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")
    # create the data source
    data_source = driver.CreateDataSource(output_file)

    # create the layer
    layer = data_source.CreateLayer("A Star Shortest Path", spatial_reference, ogr.wkbLineString)

    # Create fields (using default field first, TODO:read from data)
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
    
    # order (added field to get the order)
    layer.CreateField(ogr.FieldDefn("order", ogr.OFTInteger))

    fields = ['fid', 'streetID', 'length', 'u', 'v', 'length_sc']

    # Iterate over the path edges
    for i in range(len(path) - 1):
        node1 = path[i]
        node2 = path[i+1]
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

    return output_file

if __name__ == "__main__":
    path = '/home/ismailsunni/Documents/GeoTech/Routing/processed/small_data/'
    spatial_reference = get_spatial_reference(path)
    print(spatial_reference)
    print(spatial_reference.exportToEPSG())
    print('fin')
