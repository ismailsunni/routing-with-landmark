import matplotlib.pyplot as plt
import numpy as np
import csv
import os
from copy import deepcopy
import sys

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

def merge_csv(file_paths, column_name, merged_csv_file):
    """Merge the content of `file_paths` from `column_name` to `merged_csv_file`
    """
    values = []
    for file_path in file_paths:
        values.extend(read_csv(file_path, column_name))
    with open(merged_csv_file, mode='w') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow([column_name])
        for value in values:
            writer.writerow([value])
    return merged_csv_file


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
        capsize=10,
        color=['#C500FF', '#00FFC5', '#0070FF', '#E6E600'],
        zorder=2
        )
    # Make sure the error bar is visible
    ax.errorbar(x_pos, means, yerr=stds, zorder=3, color='black', fmt='none')
    ax.set_ylabel(y_label)
    ax.set_xlabel('Algorithm')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize='small')
    ax.set_title(title)

    # Save the figure or show
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
    date_directory = 'July5'
    # date_directory = 'July6'

    output_directory = '/home/ismailsunni/dev/python/routing/test/output/'
    barchart_output_directory = os.path.join(output_directory, 'barchart', date_directory)
    merge_csv_directory = os.path.join(output_directory, 'merged_csv')

    # Column name in the CSV files.
    esri_column_name = 'SUM_Shape_Area'
    haus_column_name = 'haus1'

    # Route names
    route_A_name = 'Route A (Gas Station Denim - Amtsgericht)'
    route_B_name = 'Route B (Bremer Platz - Domplatz)'
    route_C_name = 'Route C (Theatre - Castle)'

    # Algorithm labels
    angular_change_djikstra = 'Angular Change'
    angular_change_djikstra_landmark = 'Angular Change\nwith Landmark'
    shortest_distance_a_star = 'Shortest Distance\n(A*)'
    shortest_distance_a_star_landmark = 'Shortest Distance\n(A*) with Landmark'

    # Y Label
    distance_label = 'Distance (m)'
    area_label = u'Area (m²)'

    ### Template for area ###
    area_csv_file_paths_template = [
        [
            os.path.join(csv_directory, area_csv_sub_dir, date_directory, 'Angular_change_areaXXX.csv'),
            esri_column_name,
            angular_change_djikstra
        ],
        [
            os.path.join(csv_directory, area_csv_sub_dir, date_directory, 'Angular_change_landmark_areaXXX.csv'),
            esri_column_name,
            angular_change_djikstra_landmark
        ],
        [
            os.path.join(csv_directory, area_csv_sub_dir, date_directory, 'Astar_area_XXX.csv'),
            esri_column_name,
            shortest_distance_a_star
        ],
        [
            os.path.join(csv_directory, area_csv_sub_dir, date_directory, 'Astar_landmark_areaXXX.csv'),
            esri_column_name,
            shortest_distance_a_star_landmark
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
            os.path.join(csv_directory, distance_csv_sub_dir, date_directory, 'Angular_change_XXX.csv'),
            haus_column_name,
            angular_change_djikstra
        ],
        [
            os.path.join(csv_directory, distance_csv_sub_dir, date_directory, 'Angular_change_landmark_XXX.csv'),
            haus_column_name,
            angular_change_djikstra_landmark
        ],
        [
            os.path.join(csv_directory, distance_csv_sub_dir, date_directory, 'a_star_XXX.csv'),
            haus_column_name,
            shortest_distance_a_star
        ],
        [
            os.path.join(csv_directory, distance_csv_sub_dir, date_directory, 'a_star_landmark_XXX.csv'),
            haus_column_name,
            shortest_distance_a_star_landmark
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
            'name': route_A_name,
            'data': generate_data_from_cvs(area_csv_file_paths_1),
            'output': 'area_route_A.png',
            'title': 'Area Between',
            'y_label': area_label
        },
        {
            'name': route_B_name,
            'data': generate_data_from_cvs(area_csv_file_paths_2),
            'output': 'area_route_B.png',
            'title': 'Area Between',
            'y_label': area_label
        },
        {
            'name': route_C_name,
            'data': generate_data_from_cvs(area_csv_file_paths_3),
            'output': 'area_route_C.png',
            'title': 'Area Between',
            'y_label': area_label
        },
                {
            'name': route_A_name,
            'data': generate_data_from_cvs(distance_csv_file_paths_1),
            'output': 'distance_route_A.png',
            'title': 'Hausdorff Distance',
            'y_label': distance_label
        },
        {
            'name': route_B_name,
            'data': generate_data_from_cvs(distance_csv_file_paths_2),
            'output': 'distance_route_B.png',
            'title': 'Hausdorff Distance',
            'y_label': distance_label
        },
        {
            'name': route_C_name,
            'data': generate_data_from_cvs(distance_csv_file_paths_3),
            'output': 'distance_route_C.png',
            'title': 'Hausdorff Distance',
            'y_label': distance_label,
        },
    ]

    # merged CSV for area
    area_angular_change_summary_csv = 'area_angular_change_summary.csv'
    area_angular_change_summary_csv = os.path.join(merge_csv_directory, area_angular_change_summary_csv)
    csv_files = [
        area_csv_file_paths_1[0][0],
        area_csv_file_paths_2[0][0],
        area_csv_file_paths_3[0][0],
    ]
    merge_csv(csv_files, esri_column_name, area_angular_change_summary_csv)

    area_angular_change_landmark_summary_csv = 'area_angular_change_landmark_summary.csv'
    area_angular_change_landmark_summary_csv = os.path.join(merge_csv_directory, area_angular_change_landmark_summary_csv)
    csv_files = [
        area_csv_file_paths_1[1][0],
        area_csv_file_paths_2[1][0],
        area_csv_file_paths_3[1][0],
    ]
    merge_csv(csv_files, esri_column_name, area_angular_change_landmark_summary_csv)

    area_a_star_summary_csv = 'area_a_star_summary.csv'
    area_a_star_summary_csv = os.path.join(merge_csv_directory, area_a_star_summary_csv)
    csv_files = [
        area_csv_file_paths_1[2][0],
        area_csv_file_paths_2[2][0],
        area_csv_file_paths_3[2][0],
    ]
    merge_csv(csv_files, esri_column_name, area_a_star_summary_csv)

    area_a_star_landmark_summary_csv = 'area_a_star_landmark_summary.csv'
    area_a_star_landmark_summary_csv = os.path.join(merge_csv_directory, area_a_star_landmark_summary_csv)
    csv_files = [
        area_csv_file_paths_1[3][0],
        area_csv_file_paths_2[3][0],
        area_csv_file_paths_3[3][0],
    ]
    merge_csv(csv_files, esri_column_name, area_a_star_landmark_summary_csv)

    area_summary_csv_file_paths = [
        [
            area_angular_change_summary_csv,
            esri_column_name,
            angular_change_djikstra
        ],
        [
            area_angular_change_landmark_summary_csv,
            esri_column_name,
            angular_change_djikstra_landmark
        ],
        [
            area_a_star_summary_csv,
            esri_column_name,
            shortest_distance_a_star
        ],
        [
            area_a_star_landmark_summary_csv,
            esri_column_name,
            shortest_distance_a_star_landmark
        ],
    ]

    # merged CSV for Hausdorff Distance
    distance_angular_change_summary_csv = 'distance_angular_change_summary.csv'
    distance_angular_change_summary_csv = os.path.join(merge_csv_directory, distance_angular_change_summary_csv)
    csv_files = [
        distance_csv_file_paths_1[0][0],
        distance_csv_file_paths_2[0][0],
        distance_csv_file_paths_3[0][0],
    ]
    merge_csv(csv_files, haus_column_name, distance_angular_change_summary_csv)

    distance_angular_change_landmark_summary_csv = 'distance_angular_change_landmark_summary.csv'
    distance_angular_change_landmark_summary_csv = os.path.join(merge_csv_directory, distance_angular_change_landmark_summary_csv)
    csv_files = [
        distance_csv_file_paths_1[1][0],
        distance_csv_file_paths_2[1][0],
        distance_csv_file_paths_3[1][0],
    ]
    merge_csv(csv_files, haus_column_name, distance_angular_change_landmark_summary_csv)

    distance_a_star_summary_csv = 'distance_a_star_summary.csv'
    distance_a_star_summary_csv = os.path.join(merge_csv_directory, distance_a_star_summary_csv)
    csv_files = [
        distance_csv_file_paths_1[2][0],
        distance_csv_file_paths_2[2][0],
        distance_csv_file_paths_3[2][0],
    ]
    merge_csv(csv_files, haus_column_name, distance_a_star_summary_csv)

    distance_a_star_landmark_summary_csv = 'distance_a_star_landmark_summary.csv'
    distance_a_star_landmark_summary_csv = os.path.join(merge_csv_directory, distance_a_star_landmark_summary_csv)
    csv_files = [
        distance_csv_file_paths_1[3][0],
        distance_csv_file_paths_2[3][0],
        distance_csv_file_paths_3[3][0],
    ]
    merge_csv(csv_files, haus_column_name, distance_a_star_landmark_summary_csv)

    area_summary_csv_file_paths = [
        [
            area_angular_change_summary_csv,
            esri_column_name,
            angular_change_djikstra
        ],
        [
            area_angular_change_landmark_summary_csv,
            esri_column_name,
            angular_change_djikstra_landmark
        ],
        [
            area_a_star_summary_csv,
            esri_column_name,
            shortest_distance_a_star
        ],
        [
            area_a_star_landmark_summary_csv,
            esri_column_name,
            shortest_distance_a_star_landmark
        ],
    ]

    distance_summary_csv_file_paths = [
        [
            distance_angular_change_summary_csv,
            haus_column_name,
            angular_change_djikstra
        ],
        [
            distance_angular_change_landmark_summary_csv,
            haus_column_name,
            angular_change_djikstra_landmark
        ],
        [
            distance_a_star_summary_csv,
            haus_column_name,
            shortest_distance_a_star
        ],
        [
            distance_a_star_landmark_summary_csv,
            haus_column_name,
            shortest_distance_a_star_landmark
        ],
    ]

    summary_route_data = [
        {
            'name': 'All Route',
            'data': generate_data_from_cvs(area_summary_csv_file_paths),
            'output': 'area_between_summary.png',
            'title': 'Area Between',
            'y_label': area_label,
        },
        {
            'name': 'All Route',
            'data': generate_data_from_cvs(distance_summary_csv_file_paths),
            'output': 'distance_haudorff_summary.png',
            'title': 'Hausdorff Distance',
            'y_label': distance_label,
        },
    ]

    for route_data in summary_route_data:
        output_path = os.path.join(barchart_output_directory, route_data['output'])
        title = route_data['title'] + ' for ' + route_data['name']
        bar_chart_from_data(route_data['data'], title=title, y_label=route_data['y_label'], file_name=output_path)

    for route_data in routes_data:
        output_path = os.path.join(barchart_output_directory, route_data['output'])
        title = route_data['title'] + ' for ' + route_data['name']
        bar_chart_from_data(route_data['data'], title=title, y_label=route_data['y_label'], file_name=output_path)
