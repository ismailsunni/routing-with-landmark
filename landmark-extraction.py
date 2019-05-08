# Landmark extraction

# Steps
# Add new fields
# Check if fields exists
# Visual 
#     3D Visibility
#     Facade area 
#     Height
# Structural
#     Area 
#     2D-Advance visibility 
#     Neighbours
#     Road distance
# Semantic (Historical importance)
# Pragmatic (Landuse 200 m)

# Choosing the layer
layers = QgsProject.instance().mapLayersByName('Test')
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
    layer.startEditing()
    for feature in layer.getFeatures():
        height_index = feature.attributes()[height_field] / max_height
        layer.changeAttributeValue(feature.id(), height_index_field, height_index)
    layer.commitChanges()
    
def update_area_index(layer):
    # Height index
    print('Update area index')
    area_index_field = layer.fields().indexFromName('area_index')
    area_field = layer.fields().indexFromName('area')
    max_area = layer.maximumValue(area_field)
    layer.startEditing()
    for feature in layer.getFeatures():
        area_index = feature.attributes()[area_field] / max_area
        layer.changeAttributeValue(feature.id(), area_index_field, area_index)
    layer.commitChanges()

def calculate_landmark_index(layer):
    # Calculate landmark index
    # Formula height * 0.2 * 0.5 + area * 0.3 * 0.3
    print('Calculate landmark index')
    height_index_field = layer.fields().indexFromName('height_index')
    area_index_field = layer.fields().indexFromName('area_index')
    landmark_index_field = layer.fields().indexFromName('landmark_index')

    layer.startEditing()
    for feature in layer.getFeatures():
        height_index = feature.attributes()[height_index_field]
        area_index = feature.attributes()[area_index_field]

        landmark_index = (height_index * 0.1 + area_index * 0.09) / 0.19
        layer.changeAttributeValue(feature.id(), landmark_index_field, landmark_index)
    
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
update_height_index(building_layer)
update_area_index(building_layer)
calculate_facade(building_layer)
calculate_landmark_index(building_layer)
calculate_landmark_status(building_layer)

print('fin')
