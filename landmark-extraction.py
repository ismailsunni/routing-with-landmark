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

# Choosing the layer
layers = QgsProject.instance().mapLayersByName('Small test')
building_layer = layers[0]

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
    'landmark_index',
]
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
 
def update_height_index(layer):
    # Height index
    print('Update height index')
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
    print('Update area index')
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
    print('Calculate facade index')
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
    print('Calculate land use index')
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

def calculate_neighbours(layer, buffer_distance=150):
    # Calculating adjacent neighbour
    # Create buffer of 150 meter, then calculate the number of same building
    print('Calculate neighbours index')
    neighbours_field = layer.fields().indexFromName('neighbours')
    
    neighbours_values = []
    for feature in layer.getFeatures():
        buffer = feature.geometry().buffer(buffer_distance, 5)
        # filter layer with the same building type
    
        building_count = 0
        for feature2 in layer.getFeatures():
            if feature2.geometry().intersects(buffer):
                building_count += 1
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

def calculate_landmark_index(layer):
    # Calculate landmark index
    # Formula
    print('Calculate landmark index')
    height_index_field = layer.fields().indexFromName('height_index')
    area_index_field = layer.fields().indexFromName('area_index')
    facade_field = layer.fields().indexFromName('facade_area')
    land_use_field = layer.fields().indexFromName('land_use')
    neighbours_field = layer.fields().indexFromName('neighbours')
    landmark_index_field = layer.fields().indexFromName('landmark_index')

    layer.startEditing()
    for feature in layer.getFeatures():
        height_index = feature.attributes()[height_index_field]
        area_index = feature.attributes()[area_index_field]
        facade = feature.attributes()[facade_field]
        land_use = feature.attributes()[land_use_field]
        neighbours_index = feature.attributes()[neighbours_field]

        division = 0.1 + 0.09 + 0.15 + 0.1 + 0.06
        landmark_index = (height_index * 0.1 + area_index * 0.09 + facade * 0.15 + land_use * 0.1 + neighbours_index * 0.06) / division
        layer.changeAttributeValue(feature.id(), landmark_index_field, landmark_index)
    
    layer.commitChanges()

def calculate_landmark_status(layer, threshold=0.5):
    # Set landmark status
    print('Calculate landmark status')
    landmark_index_field = layer.fields().indexFromName('landmark_index')
    landmark_status_field = layer.fields().indexFromName('landmark_status')

    layer.startEditing()
    for feature in layer.getFeatures():
        landmark_index = feature.attributes()[landmark_index_field]

        layer.changeAttributeValue(feature.id(), landmark_status_field, landmark_index > threshold)
    
    layer.commitChanges()

# Updating the component's value.
# update_height_index(building_layer)
# update_area_index(building_layer)
# calculate_facade(building_layer)
# calculate_land_use(building_layer, 200, 'lu_eng')
calculate_neighbours(building_layer)
calculate_landmark_index(building_layer)
calculate_landmark_status(building_layer)

print('fin')
