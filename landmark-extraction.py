layers = QgsProject.instance().mapLayersByName('Muenster_buildings_obstructions_area3')
building_layer = layers[0]

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

field_names = [
    '3d_visibility',
    'facade_area',
    'height',
    'area',
    '2d_advance_visibility',
    'neighbours',
    'road_distance',
    'historical_importance',
    'land_use',
]

fields = [
    QgsField(field_name, QVariant.Double) for field_name in field_names if building_layer.fields().indexFromName(field_name) == -1
]

if building_layer.fields().indexFromName('landmark_index') == -1:
    fields.append(QgsField('landmark_index', QVariant.Bool))

building_layer.dataProvider().addAttributes(fields)

 
building_layer.updateFields()
 