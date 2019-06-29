# Landmark extraction

# Steps
# Add new fields
# Check if fields exists
# Visual 
#     3D Visibility 0.5 * 0.5 = 0.25
#     Facade area  0.3 * 0.5 = 0.15
#     Height 0.2 * 0.5 = 0.1
# Structural
#     Area 0.3 * 0.3 = 0.09
#     2D-Advance visibility 0.3 * 0.3 = 0.09
#     Neighbours 0.2 * 0.3 = 0.06
#     Road distance 0.2 * 0.3 = 0.06
# Semantic (Historical importance) 0.1
# Pragmatic (Landuse 200 m) 0.1

from datetime import datetime
import os
import sys

import argparse

import qgis.utils

from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsApplication, 
    QgsVectorLayer,
    QgsProject,
    QgsField,
    QgsSpatialIndex,
    QgsGeometry,
)

from qgis_utils import create_spatial_index

QgsApplication.setPrefixPath('/usr', True)
qgs = QgsApplication([], False)
qgs.initQgis()

field_names = [
    '3d_visibility',
    'facade_area',
    'height_index',
    'area_index',
    '2d_advance_visibility',
    'neighbours',
    'road_distance',
    'historical_importance',
    'land_use',
    'visual_index',
    'structural_index',
    'landmark_index',
]

DEBUG_MODE = True

def debug(message):
    if DEBUG_MODE:
        print(message)

def update_height_index(layer):
    # Height index
    debug('Update height index')
    height_index_field = layer.fields().indexFromName('height_index')
    height_field = layer.fields().indexFromName('height')
    max_height = layer.maximumValue(height_field)
    min_height = layer.minimumValue(height_field)
    range_height = max_height - min_height
    layer.startEditing()
    for feature in layer.getFeatures():
        height_index = (feature.attributes()[height_field] - min_height) / range_height
        layer.changeAttributeValue(feature.id(), height_index_field, height_index)
    layer.commitChanges()
    
def update_area_index(layer):
    # Height index
    debug('Update area index')
    area_index_field = layer.fields().indexFromName('area_index')
    area_field = layer.fields().indexFromName('area')
    max_area = layer.maximumValue(area_field)
    min_area = layer.minimumValue(area_field)
    range_area = max_area - min_area
    layer.startEditing()
    for feature in layer.getFeatures():
        area_index = (feature.attributes()[area_field] - min_area) / range_area
        layer.changeAttributeValue(feature.id(), area_index_field, area_index)
    layer.commitChanges()

def calculate_facade(layer):
    # Calculating facade index, normalize to 0 - 1
    debug('Calculate facade index')
    height_field = layer.fields().indexFromName('height')
    facade_field = layer.fields().indexFromName('facade_area')

    facade_values = []
    for feature in layer.getFeatures():
        height_index = feature.attributes()[height_field]
        perimeter = feature.geometry().length() 
        facade_values.append(height_index * perimeter)
    facade_range = max(facade_values) - min(facade_values)
    layer.startEditing()
    i = 0
    for feature in layer.getFeatures():
        facade_index = (facade_values[i] - min(facade_values)) / facade_range
        layer.changeAttributeValue(feature.id(), facade_field, facade_index)
        i += 1
    layer.commitChanges()

def calculate_land_use(layer, buffer_distance=200, type_field_name='lu_eng'):
    # Calculating pragmatic index for land use
    # Create buffer of 200 meter, then calculate the number of same type building compare to total building
    debug('Calculate land use index')
    land_use_field = layer.fields().indexFromName('land_use')
    building_type_field = layer.fields().indexFromName(type_field_name)
    
    land_use_value = []
    for feature in layer.getFeatures():
        # create buffer
        buffer = feature.geometry().buffer(buffer_distance, 5)
        current_building_type = feature.attributes()[building_type_field]
        # filter layer with the same building type
        same_building_count = 0
        all_building_count = 0
        for feature2 in layer.getFeatures():
            if feature2.geometry().intersects(buffer):
                all_building_count += 1
                if feature2.attributes()[building_type_field] == current_building_type:
                   same_building_count += 1
        # calculate total building area
        # get land use value (total building area/buffer area)
        land_use_value.append(1 - (same_building_count / all_building_count))
    max_land_use = max(land_use_value)
    min_land_use = min(land_use_value)
    range_land_use = max_land_use - min_land_use
    layer.startEditing()
    i = 0
    for feature in layer.getFeatures():
        land_use_index = (land_use_value[i] - min_land_use) / range_land_use
        layer.changeAttributeValue(feature.id(), land_use_field, land_use_index)
        i += 1
    layer.commitChanges()

def calculate_land_use_spatial_index(layer, buffer_distance=200, type_field_name='lu_eng'):
    # Calculating pragmatic index for land use
    # Create buffer of 200 meter, then calculate the number of same type building compare to total building
    debug('Calculate land use index')

    land_use_field = layer.fields().indexFromName('land_use')
    building_type_field = layer.fields().indexFromName(type_field_name)

    # Select all features along with their attributes
    all_features = {feature.id(): feature for (feature) in layer.getFeatures()}
    # Create spatial index
    spatial_index = create_spatial_index(layer)
    
    land_use_value = []
    for feature in layer.getFeatures():
        # create buffer
        buffer = feature.geometry().buffer(buffer_distance, 5)
        current_building_type = feature.attributes()[building_type_field]
        # filter layer with the same building type
        intersect_indexes = spatial_index.intersects(buffer.boundingBox())
        all_building_count = len(intersect_indexes)
        same_building_count = 0
        for intersect_index in intersect_indexes:
            # debug(all_features[intersect_index].attributes()[building_type_field])
            if all_features[intersect_index].attributes()[building_type_field] == current_building_type:
                same_building_count += 1
        # calculate total building area
        # get land use value (total building area/buffer area)
        if all_building_count == 0:
            land_use_value.append(1)
        else:
            land_use_value.append(1 - (same_building_count / all_building_count))
    max_land_use = max(land_use_value)
    min_land_use = min(land_use_value)
    range_land_use = max_land_use - min_land_use
    layer.startEditing()
    i = 0
    for feature in layer.getFeatures():
        if range_land_use == 0:
            land_use_index = 1
        else:
            land_use_index = (land_use_value[i] - min_land_use) / range_land_use
        layer.changeAttributeValue(feature.id(), land_use_field, land_use_index)
        i += 1
    layer.commitChanges()

def calculate_neighbours_spatial_index(layer, buffer_distance=150):
    # Calculating adjacent neighbour
    # Create buffer of 150 meter, then calculate the number of same building
    debug('Calculate neighbours index')
    neighbours_field = layer.fields().indexFromName('neighbours')

    # Create spatial index
    spatial_index = create_spatial_index(layer)

    neighbours_values = []
    for feature in layer.getFeatures():
        buffer = feature.geometry().buffer(buffer_distance, 5)
        # filter layer with the same building type
    
        intersect_indexes = spatial_index.intersects(buffer.boundingBox())
        building_count = len(intersect_indexes)

        neighbours_values.append(building_count)
    
    max_neighbours = max(neighbours_values)
    min_neighbours = min(neighbours_values)
    range_neighbours = max_neighbours - min_neighbours
    layer.startEditing()
    i = 0
    for feature in layer.getFeatures():
        neighbours_index = (neighbours_values[i] - min_neighbours) / range_neighbours
        layer.changeAttributeValue(feature.id(), neighbours_field, neighbours_index)
        i += 1
    layer.commitChanges()

def calculate_historical_importance(layer, historic_layer):
    # Set historical status based on historical layer
    # All polygon in historical layer is assumed to be historic
    debug('Calculate historical importance')
    historical_field = layer.fields().indexFromName('historical_importance')

    layer.startEditing()

    # Select all features along with their attributes
    all_features = {feature.id(): feature for (feature) in layer.getFeatures()}
    for feature in all_features.values():
        layer.changeAttributeValue(feature.id(), historical_field, 0.0)
    layer.commitChanges()
    
    # Create spatial index
    spatial_index = create_spatial_index(layer)

    layer.startEditing()
    for historic_feature in historic_layer.getFeatures():
        if not historic_feature.attributes()[8]:
            continue
        geometry = historic_feature.geometry()
        intersect_indexes = spatial_index.intersects(geometry.boundingBox())
        debug(historic_feature.attributes()[8])
        debug(len(intersect_indexes))
        for intersect_index in intersect_indexes:
            feature = all_features[intersect_index]
            # all_features[intersect_index].setAttribute(historical_field, 1.0)
            layer.changeAttributeValue(feature.id(), historical_field, 1.0)
    layer.commitChanges()

def calculate_shortest_road_distance(layer, road_layer):
    """Calculating the shortest distance to the nearest road"""
    debug('Calculate shortest road distance')
    road_distance_field = layer.fields().indexFromName('road_distance')
    all_roads = {feature.id(): feature for (feature) in road_layer.getFeatures()}
    # Create spatial index
    road_spatial_index = create_spatial_index(road_layer)

    nearest_distances = []
    for building in layer.getFeatures():
        nearest_road_id = road_spatial_index.nearestNeighbor(building.geometry())[0]
        road = all_roads[nearest_road_id]
        distance = QgsGeometry.distance(building.geometry(), road.geometry())
        nearest_distances.append(distance)

    # Rescale
    min_nearest_distances = min(nearest_distances)
    max_nearest_distances = max(nearest_distances)
    range_nearest_distances = max_nearest_distances - min_nearest_distances

    # Update value
    layer.startEditing()
    i = 0
    for feature in layer.getFeatures():
        nearest_distance_index = (nearest_distances[i] - min_nearest_distances) / range_nearest_distances
        layer.changeAttributeValue(feature.id(), road_distance_field, nearest_distance_index)
        i += 1
    layer.commitChanges()

def calculate_visual_index(layer):
    # Calculate visual index. Result should be between 0-1
    # Visual 
    #     3D Visibility 0.5 * 0.5 = 0.25
    #     Facade area  0.3 * 0.5 = 0.15
    #     Height 0.2 * 0.5 = 0.1
    debug('Calculate visual index')
    facade_field = layer.fields().indexFromName('facade_area')
    height_index_field = layer.fields().indexFromName('height_index')
    visual_index_field = layer.fields().indexFromName('visual_index')

    visual_raw_values = []
    for feature in layer.getFeatures():
        facade = feature.attributes()[facade_field]
        height_index = feature.attributes()[height_index_field]

        visual_component_ratios = [
            (height_index, 0.2),
            (facade, 0.3),
        ]
        
        divisor = sum(component_ratio[1] for component_ratio in visual_component_ratios)
        visual_raw_value = sum(
            component_ratio[0] * component_ratio[1] for component_ratio in visual_component_ratios
        ) / divisor
        visual_raw_values.append(visual_raw_value)
    
    # Rescale
    min_visual_raw_value = min(visual_raw_values)
    max_visual_raw_value = max(visual_raw_values)
    range_visual_raw_value = max_visual_raw_value - min_visual_raw_value
    
    # Update value
    layer.startEditing()
    i = 0
    for feature in layer.getFeatures():
        visual_index = (visual_raw_values[i] - min_visual_raw_value) / range_visual_raw_value
        layer.changeAttributeValue(feature.id(), visual_index_field, visual_index)
        i += 1
    layer.commitChanges()

def calculate_structural_index(layer):
    # Calculate structural index. Result should be between 0-1
    # Structural
    #     Area 0.3 * 0.3 = 0.09
    #     2D-Advance visibility 0.3 * 0.3 = 0.09
    #     Neighbours 0.2 * 0.3 = 0.06
    #     Road distance 0.2 * 0.3 = 0.06
    debug('Calculate structural index')
    area_index_field = layer.fields().indexFromName('area_index')
    neighbours_field = layer.fields().indexFromName('neighbours')
    road_distance_field = layer.fields().indexFromName('road_distance')
    structural_index_field = layer.fields().indexFromName('structural_index')

    structural_raw_values = []
    for feature in layer.getFeatures():
        area_index = feature.attributes()[area_index_field]
        neighbours = feature.attributes()[neighbours_field]
        road_distance = feature.attributes()[road_distance_field]

        structural_component_ratios = [
            (area_index, 0.3),
            (neighbours, 0.2),
            (road_distance, 0.2)
        ]
        
        divisor = sum(component_ratio[1] for component_ratio in structural_component_ratios)
        structural_raw_value = sum(
            component_ratio[0] * component_ratio[1] for component_ratio in structural_component_ratios
        ) / divisor
        structural_raw_values.append(structural_raw_value)
    
    # Rescale
    min_structural_raw_value = min(structural_raw_values)
    max_structural_raw_value = max(structural_raw_values)
    range_structural_raw_value = max_structural_raw_value - min_structural_raw_value
    
    # Update value
    layer.startEditing()
    i = 0
    for feature in layer.getFeatures():
        structural_index = (structural_raw_values[i] - min_structural_raw_value) / range_structural_raw_value
        layer.changeAttributeValue(feature.id(), structural_index_field, structural_index)
        i += 1
    layer.commitChanges()


def calculate_landmark_index(layer):
    # Calculate landmark index
    debug('Calculate landmark index')
    visual_index_field = layer.fields().indexFromName('visual_index')
    structural_index_field = layer.fields().indexFromName('structural_index')
    historical_field = layer.fields().indexFromName('historical_importance')
    land_use_field = layer.fields().indexFromName('land_use')
    landmark_index_field = layer.fields().indexFromName('landmark_index')

    
    landmark_raw_values = []
    for feature in layer.getFeatures():
        visual_index = feature.attributes()[visual_index_field]
        structural_index = feature.attributes()[structural_index_field]
        land_use = feature.attributes()[land_use_field]
        historical_index = feature.attributes()[historical_field]

        component_ratios = [
            (visual_index, 0.5),
            (structural_index, 0.3),
            (land_use, 0.1),
            (historical_index, 0.1)
        ]

        divisor = sum(component_ratio[1] for component_ratio in component_ratios)
        landmark_raw_value = sum(
            component_ratio[0] * component_ratio[1] for component_ratio in component_ratios
        ) / divisor
        landmark_raw_values.append(landmark_raw_value)

    # Rescale
    min_landmark_raw_value = min(landmark_raw_values)
    max_landmark_raw_value = max(landmark_raw_values)
    range_landmark_raw_value = max_landmark_raw_value - min_landmark_raw_value
    
    # Update value
    layer.startEditing()
    i = 0
    for feature in layer.getFeatures():
        landmark_index = (landmark_raw_values[i] - min_landmark_raw_value) / range_landmark_raw_value
        layer.changeAttributeValue(feature.id(), landmark_index_field, landmark_index)
        i += 1
    layer.commitChanges()

def calculate_landmark_status(layer, threshold=0.5):
    # Set landmark status
    debug('Calculate landmark status')
    landmark_index_field = layer.fields().indexFromName('landmark_index')
    landmark_status_field = layer.fields().indexFromName('landmark_status')

    layer.startEditing()
    for feature in layer.getFeatures():
        landmark_index = feature.attributes()[landmark_index_field]

        layer.changeAttributeValue(feature.id(), landmark_status_field, landmark_index > threshold)
    
    layer.commitChanges()


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode", 
        help="`full` or `update` index", 
        nargs='?', 
        type=str,
        const='update')
    parser.add_argument(
        '--threshold', 
        nargs='?', 
        const=0.5, 
        type=float, 
        help='The threshold for landmark status')
    args = parser.parse_args()
    mode = args.mode if args.mode else 'full'
    threshold = args.threshold if args.threshold else 0.5
    print('Running [%s] mode with threshold = %.2f' % (mode, threshold))

    # Debug mode
    DEBUG_MODE = True

    # Load layer, used in external script
    small_test_path = '/home/ismailsunni/Documents/GeoTech/Routing/processed/small_test_building.gpkg|layername=small_test'
    full_test_path = '/home/ismailsunni/Documents/GeoTech/Routing/processed/Building_casestudy_area_3.gpkg|layername=Buildning_caseStudy_area_3'
    building_layer = QgsVectorLayer(full_test_path, 'building', 'ogr')

    if not building_layer.isValid():
        print('Building layer invalid')

    historical_path = '/home/ismailsunni/Documents/GeoTech/Routing/processed/historical_3044.gpkg|layername=historical building muenster'
    historical_layer = QgsVectorLayer(historical_path, 'historical', 'ogr')
    if not historical_layer.isValid():
        print('Historical layer invalid')

    road_path = '/home/ismailsunni/Documents/GeoTech/Routing/topic_data/edges.shp'
    road_layer = QgsVectorLayer(road_path, 'road', 'ogr')
    if not road_layer.isValid():
        print('Road layer invalid')

    # Create intermediate fields for storing the values
    fields = [
        QgsField(field_name, QVariant.Double) for field_name in field_names if building_layer.fields().indexFromName(field_name) == -1
    ]

    # Create landmark_status for the final 
    if building_layer.fields().indexFromName('landmark_status') == -1:
        fields.append(QgsField('landmark_status', QVariant.Bool))

    # Add the fields to the layer
    building_layer.dataProvider().addAttributes(fields)
    building_layer.updateFields()
    
    start = datetime.now()

    if mode == 'full':
        # Updating the component's value.
        update_height_index(building_layer)
        update_area_index(building_layer)
        calculate_facade(building_layer)
        calculate_land_use_spatial_index(building_layer, 200, 'lu_eng')
        calculate_neighbours_spatial_index(building_layer)
        calculate_historical_importance(building_layer, historical_layer)
        calculate_shortest_road_distance(building_layer, road_layer)
        
        # Update index per component
        calculate_structural_index(building_layer)
        calculate_visual_index(building_layer)
    
    # always re-calculate index
    calculate_landmark_index(building_layer)
    calculate_landmark_status(building_layer,threshold=threshold)

    end = datetime.now()

    # Summary
    landmarks = building_layer.getFeatures('"landmark_status" = true')
    print('Summary: ')
    print('Duration: ' + str((end - start)))
    print('Number of landmarks: %s' % len(list(landmarks)))
    print('Total buildings: %s' % building_layer.featureCount())

    print('fin')

