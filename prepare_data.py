
if __name__ == "__main__":
    from qgis.PyQt.QtCore import QVariant
    from qgis.core import QgsApplication, QgsVectorLayer, QgsPointXY, QgsField

    from qgis_utils import get_nearest_feature
    
    QgsApplication.setPrefixPath('/usr', True)
    qgs = QgsApplication([], False)
    qgs.initQgis()

    landmark_file = '/home/ismailsunni/Documents/GeoTech/Routing/processed/Building_casestudy_area_3.gpkg|layername=Buildning_caseStudy_area_3'
    node_file = '/home/ismailsunni/Documents/GeoTech/Routing/topic_data/nodes_single.shp'

    # Open layer
    landmark_layer = QgsVectorLayer(landmark_file, 'Landmarks', 'ogr')
    node_layer = QgsVectorLayer(node_file, 'Landmarks', 'ogr')

    # Field name
    landmark_field_name = 'landmark'

    # Add landmark_status field to node if it doesn't have
    if node_layer.fields().indexFromName(landmark_field_name) == -1:
        landmark_field = QgsField(landmark_field_name, QVariant.Bool)
        # Add the fields to the layer
        node_layer.dataProvider().addAttributes([landmark_field])
        node_layer.updateFields()
    
    # Set all value of landmark_status to False
    node_layer.startEditing()
    landmark_field_index = node_layer.fields().indexFromName(landmark_field_name)
    all_features = {feature.id(): feature for (feature) in node_layer.getFeatures()}
    for feature in all_features.values():
        node_layer.changeAttributeValue(feature.id(), landmark_field_index, False)
    node_layer.commitChanges()

    node_layer.startEditing()
    # Get all polygon that is a landmark
    features = landmark_layer.getFeatures('"landmark_status" = 1')
    i = 0
    for feature in features:
        # Get all nearest node for each landmark
        nearest_node = get_nearest_feature(node_layer, feature.geometry().centroid().asPoint())
        # Set the value of landmark_status to True for the nearest node
        node_layer.changeAttributeValue(nearest_node.id(), landmark_field_index, 1)
        print('%s get %s' % (feature['lu_eng'], nearest_node['nodeID']))
        i = i + 1
    print('Number of landmark: %s' % i)
    
    node_layer.commitChanges()
    print('fin')