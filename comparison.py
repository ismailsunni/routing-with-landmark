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

means = [np.mean(x[1]) for x in data]
stds = [np.std(x[1]) for x in data]
labels = [x[0] for x in data]

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

bar_chart_with_std(means, stds, labels, title='Title', y_label='Y Label', file_name='')
