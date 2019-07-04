import matplotlib.pyplot as plt
import numpy as np

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
    ax.bar(
        x_pos,
        means,
        yerr=stds,
        align='center',
        alpha=0.5,
        ecolor='black',
        capsize=10)
    ax.set_ylabel(y_label)
    # ax.set_xlabel('Hausdorf')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels)
    ax.set_title(title)
    ax.yaxis.grid(True)

    # Save the figure and show
    plt.tight_layout()
    if file_name:
        plt.savefig(file_name)
    plt.show()

def bar_chart_from_data(data, title, y_label, file_name=''):
    """
    Create bar chart from a data. See generate_means_stds_labels for the format of the data.
    """
    summary = generate_means_stds_labels(data)
    bar_chart_with_std(summary['means'], summary['stds'], summary['labels'], title, y_label, file_name)

if __name__ == "__main__":
    bar_chart_from_data(data, title='Title', y_label='Y label')