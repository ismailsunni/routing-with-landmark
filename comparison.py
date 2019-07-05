import matplotlib.pyplot as plt
import numpy as np
import csv
import os
from copy import deepcopy

# Sample data
hausdorf_values_1 = np.array([
    372.9673221,
    372.9673221,
    372.9673385,
    225.345559,
    372.9673221,
    225.3455403,
    372.9673221,
    372.9673221,
    399.7266599,
    400.0337616,
    373.5843667,
    373.5843449,
])

hausdorf_values_2 = np.array([
    372.9673221,
    372.9673221,
    372.9673385,
    225.345559,
    372.9673221,
    225.3455403,
    372.9673221,
    372.9673221,
    399.7266599,
    400.0337616,
    373.5843667,
    373.5843449,
])

data = [
    [
        'A* with landmark',
        hausdorf_values_1
    ],
    [
        'Angle change with landmark',
        hausdorf_values_2
    ]
]

def read_csv(file_path, column_name):
    """Read CSV file, and extract values in column name as a array.
    """
    values = []
    with open(file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=';')
        for row in csv_reader:
            string_value = row.get(column_name)
            # just in case the value is empty
            if string_value == '':
                continue
            string_value = string_value.replace(',', '.')
            values.append(float(string_value))

    return values

def generate_data_from_cvs(csv_file_paths):
    """Generate data from list of csv_file_paths. csv_file_paths contains path to CSV file, column_name, and its label
    `csv_file_paths`: A list of CSV file path, column_name, and label
    """
    data = []
    for item in csv_file_paths:
        values = read_csv(item[0], item[1])
        data.append([
            item[2],
            values
        ])
    return data

def generate_means_stds_labels(data):
    """
    Generate dictionary of means, stds, and labels from data.
    Data is a list with this format:
    data = [
        [
            'label',
            []  # np.array
        ],
        [
            'label',
            []  # np.array
        ],
    ]
    """
    means = [np.mean(x[1]) for x in data]
    stds = [np.std(x[1]) for x in data]
    labels = [x[0] for x in data]

    return {
        'means': means,
        'stds': stds,
        'labels': labels
    }

def bar_chart_with_std(means, stds, labels, title, y_label, file_name=''):
    """
    Create bar chart height of means and error of stds and label of
    """
    x_pos = np.arange(len(labels))
    # Build the plot
    _, ax = plt.subplots()
    ax.yaxis.grid(True, zorder=0)
    ax.bar(
        x_pos,
        means,
        yerr=stds,
        align='center',
        ecolor='black',
        capsize=10,
        color=['red', 'green', 'blue', 'orange'],
        zorder=1
        )
    ax.set_ylabel(y_label)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.set_title(title)
    

    # Save the figure and show
    plt.tight_layout()
    if file_name:
        plt.savefig(file_name)
    else:
        plt.show()

def bar_chart_from_data(data, title, y_label, file_name=''):
    """
    Create bar chart from a data. See generate_means_stds_labels for the format of the data.
    """
    summary = generate_means_stds_labels(data)
    bar_chart_with_std(summary['means'], summary['stds'], summary['labels'], title, y_label, file_name)

if __name__ == "__main__":
    csv_directory = '/home/ismailsunni/Documents/GeoTech/Routing/csv_comparison/'
    area_csv_sub_dir = 'Area comparison csv'
    distance_csv_sub_dir = 'distance comparison csv'
    output_directory = '/home/ismailsunni/dev/python/routing/test/output'
    
    esri_column_name = 'SUM_Shape_Area'
    haus_column_name = 'haus1'
    
    ### Template for area ###
    area_csv_file_paths_template = [
        [
            os.path.join(csv_directory, area_csv_sub_dir, 'Angular_change_areaXXX.csv'), 
            esri_column_name,
            'Angular change'
        ],
        [
            os.path.join(csv_directory, area_csv_sub_dir, 'Angular_change_landmark_areaXXX.csv'), 
            esri_column_name,
            'Angular change with landmark'
        ],
        [
            os.path.join(csv_directory, area_csv_sub_dir, 'Atsar_areaXXX.csv'), 
            esri_column_name,
            'A*'
        ],
        [
            os.path.join(csv_directory, area_csv_sub_dir, 'Astar_landmark_area_XXX.csv'), 
            esri_column_name,
            'A* with landmark'
        ],   
    ]

    area_csv_file_paths_1 = deepcopy(area_csv_file_paths_template)
    for csv_file_path in area_csv_file_paths_1:
        csv_file_path[0] = csv_file_path[0].replace('XXX', '1')
    
    area_csv_file_paths_2 = deepcopy(area_csv_file_paths_template)
    for csv_file_path in area_csv_file_paths_2:
        csv_file_path[0] = csv_file_path[0].replace('XXX', '2')

    area_csv_file_paths_3 = deepcopy(area_csv_file_paths_template)
    for csv_file_path in area_csv_file_paths_3:
        csv_file_path[0] = csv_file_path[0].replace('XXX', '3')

    ### Template for distance ###
    distance_csv_file_paths_template = [
        [
            os.path.join(csv_directory, distance_csv_sub_dir, 'Angular_change_XXX.csv'), 
            haus_column_name,
            'Angular change'
        ],
        [
            os.path.join(csv_directory, distance_csv_sub_dir, 'Angular_change_landmark_XXX.csv'), 
            haus_column_name,
            'Angular change with landmark'
        ],
        [
            os.path.join(csv_directory, distance_csv_sub_dir, 'a_star_XXX.csv'), 
            haus_column_name,
            'A*'
        ],
        [
            os.path.join(csv_directory, distance_csv_sub_dir, 'a_star_landmark_XXX.csv'), 
            haus_column_name,
            'A* with landmark'
        ],   
    ]

    distance_csv_file_paths_1 = deepcopy(distance_csv_file_paths_template)
    for csv_file_path in distance_csv_file_paths_1:
        csv_file_path[0] = csv_file_path[0].replace('XXX', 'A')
    
    distance_csv_file_paths_2 = deepcopy(distance_csv_file_paths_template)
    for csv_file_path in distance_csv_file_paths_2:
        csv_file_path[0] = csv_file_path[0].replace('XXX', 'B')

    distance_csv_file_paths_3 = deepcopy(distance_csv_file_paths_template)
    for csv_file_path in distance_csv_file_paths_3:
        csv_file_path[0] = csv_file_path[0].replace('XXX', 'C')

    routes_data = [
        {
            'name': 'Route 1',
            'data': generate_data_from_cvs(area_csv_file_paths_1),
            'output': 'area_route_1.png',
            'title': 'Area Between',
            'y_label': 'Area'
        },
        {
            'name': 'Route 2',
            'data': generate_data_from_cvs(area_csv_file_paths_2),
            'output': 'area_route_2.png',
            'title': 'Area Between',
            'y_label': 'Area'
        },
        {
            'name': 'Route 3',
            'data': generate_data_from_cvs(area_csv_file_paths_3),
            'output': 'area_route_3.png',
            'title': 'Area Between',
            'y_label': 'Area',
        },
                {
            'name': 'Route 1',
            'data': generate_data_from_cvs(distance_csv_file_paths_1),
            'output': 'distance_route_1.png',
            'title': 'Hausdorff Distance',
            'y_label': 'Distance'
        },
        {
            'name': 'Route 2',
            'data': generate_data_from_cvs(distance_csv_file_paths_2),
            'output': 'distance_route_2.png',
            'title': 'Hausdorff Distance',
            'y_label': 'Distance'
        },
        {
            'name': 'Route 3',
            'data': generate_data_from_cvs(distance_csv_file_paths_3),
            'output': 'distance_route_3.png',
            'title': 'Hausdorff Distance',
            'y_label': 'Distance',
        },
    ]

    for route_data in routes_data:
        output_path = os.path.join(output_directory, route_data['output'])
        title = route_data['title'] + ' for ' + route_data['name']
        bar_chart_from_data(route_data['data'], title=title, y_label=route_data['y_label'], file_name=output_path)
