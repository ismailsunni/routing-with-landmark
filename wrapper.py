"""
Wrapper script to get path from a point with an algorithm

    Author      : Ismail Sunni
    Email       : imajimatika@gmail.com
    Date        : Jun 2019
"""
from osgeo import ogr, osr
import os
import networkx as nx

from qgis.core import QgsApplication, QgsVectorLayer, QgsPointXY, QgsGeometry, QgsFeature
from utils import get_points, get_spatial_reference
from qgis_utils import get_nearest_feature

from a_star import shortest_path_a_star as a_star_algorithm
from a_star_landmark import shortest_path_a_star as a_star_landmark_algorithm

def algorithm_wrapper(start_point, end_point, node_layer, input_data_path, output_file, algorithm, node_id_attribute='nodeID'):
    """
        `start_point` : the starting point as QgsPointXY
        `end_point` : the end point as QgsPointXY
        `node_layer` : a point vector layer that contains the node. Naturally it's located in input_data_path
        `input_data_path` : a path to directory with nodes and edges layer.
        `output_file` : a path to the output shape file.
    """
    # Get the nearest node from start and end
    start_node = get_nearest_feature(node_layer, start_point)
    print('start nodeID:', start_node['nodeID'])
    end_node = get_nearest_feature(node_layer, end_point)
    print('end nodeID:', end_node['nodeID'])
    
    # generate path with the `algorithm`
    start_node_id = (node_id_attribute, start_node['nodeID'])
    end_node_id = (node_id_attribute, end_node['nodeID'])
    path = algorithm(start_node_id, end_node_id, input_data_path, output_file)

    # Sort the path
    coordinates = [start_point]
    G = nx.Graph(nx.read_shp(input_data_path, strict=False, geom_attrs=True)) # Read and convert to Graph
    for i in range(len(path) - 1):
        node1 = path[i]
        node2 = path[i+1]
        edge_key = [node1, node2]
        # print('edge key: ', edge_key)
        points = get_points(G, edge_key)
        # print(points)
        if i == 0:
            for p in points:
                coordinates.append(QgsPointXY(p[0], p[1]))
        else:
            start_point_path = QgsPointXY(points[0][0], points[0][1])
            if start_point_path == coordinates[-1]:
                # Same end point, add a usual
                for p in points[1:]:
                    coordinates.append(QgsPointXY(p[0], p[1]))
            else:
                # Different endpoint, reverse
                for p in points[::-1][1:]:
                    coordinates.append(QgsPointXY(p[0], p[1]))
    # Append end point
    coordinates.append(end_point)
    
    # Spatial reference
    spatial_reference = get_spatial_reference(input_data_path)

    # Write result to a shapefile (TODO: put it in a function)
    # Create geometry for the whole line
    line_geometry = QgsGeometry.fromPolylineXY(coordinates)
    # Convert to Wkt for ogr
    line_wkt = line_geometry.asWkt()
    # set up the shapefile driver
    driver = ogr.GetDriverByName("ESRI Shapefile")
    # create the data source
    data_source = driver.CreateDataSource(output_file)
    # create the layer
    layer = data_source.CreateLayer("A Star Shortest Path", spatial_reference, ogr.wkbLineString)
    feature = ogr.Feature(layer.GetLayerDefn())
    geom = ogr.CreateGeometryFromWkt(line_wkt)
    # Set the feature geometry using the geom
    feature.SetGeometry(geom)
    # Create the feature in the layer (shapefile)
    layer.CreateFeature(feature)
    # Dereference the feature
    feature = None
    data_source = None

    print(output_file)


if __name__ == "__main__":
    from qgis.core import QgsApplication, QgsVectorLayer, QgsPointXY
    
    QgsApplication.setPrefixPath('/usr', True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    # Point A
    start_point = QgsPointXY(405812, 5756851)
    end_point = QgsPointXY(404984, 5757671)
    # Test
    # start_point = QgsPointXY(404346.48, 5757913.23)
    # end_point = QgsPointXY(404447.56, 5757876.82)

    node_path = '/home/ismailsunni/Documents/GeoTech/Routing/topic_data/nodes_single.shp'
    # node_path = '/home/ismailsunni/Documents/GeoTech/Routing/processed/small_data/smaller_nodes_single.shp'
    node_layer = QgsVectorLayer(node_path, 'nodes', 'ogr')
    if not node_layer.isValid():
        print('Node layer is not valid.')
    
    input_data_path = '/home/ismailsunni/Documents/GeoTech/Routing/topic_data'
    # input_data_path = '/home/ismailsunni/Documents/GeoTech/Routing/processed/small_data'

    base_output_file =  '/home/ismailsunni/dev/python/routing/test/output/'
    output_file = os.path.join(base_output_file, 'landmark_wrapper_A.shp')

    algorithm_wrapper(start_point, end_point, node_layer, input_data_path, output_file, a_star_landmark_algorithm)
