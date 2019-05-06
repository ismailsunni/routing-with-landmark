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
building_layer.dataProvider().addAttributes([
    QgsField("3d_visibility", QVariant.Double),
#    QgsField("facade_area", QVariant.Double),
#    QgsField("height", QVariant.Double),
#    QgsField("area", QVariant.Double),
#    QgsField("2d_advance_visibility", QVariant.Double),
#    QgsField("road_distance", QVariant.Double),
#    QgsField("historical_importance", QVariant.Double),
#    QgsField("landuse", QVariant.Double),
 ])
 
building_layer.updateFields()
 