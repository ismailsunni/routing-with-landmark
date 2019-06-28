import qgis.utils

from qgis.core import (
    QgsSpatialIndex
)

def create_spatial_index(layer):
    # Select all features along with their attributes
    all_features = {feature.id(): feature for (feature) in layer.getFeatures()}
    # Create spatial index
    spatial_index = QgsSpatialIndex()
    for f in all_features.values():
        spatial_index.addFeature(f)
    return spatial_index

def get_nearest_feature(layer, point):
    """Helper to get nearest feature of a `layer` from `point`"""
    all_features = {feature.id(): feature for (feature) in layer.getFeatures()}
    spatial_index = create_spatial_index(layer)
    nearest_id = spatial_index.nearestNeighbor(point)[0] # we need only one neighbour
    return all_features[nearest_id]

def get_nearest_features(layer, point, num_points=1, max_distance=0):
    """Helper to get nearest feature of a `layer` from `point`"""
    all_features = {feature.id(): feature for (feature) in layer.getFeatures()}
    spatial_index = create_spatial_index(layer)
    nearest_ids = spatial_index.nearestNeighbor(point, num_points, max_distance) # we need only one neighbour
    return [all_features[nearest_id] for nearest_id in nearest_ids]

def get_nearest_feature_buffer(layer, the_feature, buffer_distance):
    """Get the points which located near a buffer with distance of a polygon"""
    all_features = {feature.id(): feature for (feature) in layer.getFeatures()}
    spatial_index = create_spatial_index(layer)

    buffer = the_feature.geometry().buffer(buffer_distance, 5)
    intersect_indexes = spatial_index.intersects(buffer.boundingBox())
    return [all_features[intersect_index] for intersect_index in intersect_indexes]

if __name__ == "__main__":
    from qgis.core import QgsApplication, QgsVectorLayer, QgsPointXY
    
    QgsApplication.setPrefixPath('/usr', True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    node_path = './test/input/smaller_nodes_single.shp'
    node_layer = QgsVectorLayer(node_path, 'historical', 'ogr')
    if not node_layer.isValid():
        print('Node layer is not valid.')

    point = QgsPointXY(404362.77, 5757893.31)
    nearest_node = get_nearest_feature(node_layer, point)
    print(nearest_node['nodeID'])

    point = QgsPointXY(404362.77, 5757893.31)
    nearest_nodes = get_nearest_features(node_layer, point, 5, 20)
    for n in nearest_nodes:
        print(n['nodeID'])
