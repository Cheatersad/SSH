import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import warnings

# Read the CSV data
data = pd.read_csv('output_testing.csv')

# Select columns for clustering (all columns after the first 5 columns)
columns_for_clustering = data.columns[5:]
X = data[columns_for_clustering]

# Preprocess the data using MinMaxScaler
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Perform DBSCAN clustering with adjusted parameters
dbscan = DBSCAN(eps=1.5, min_samples=3)  # Adjust eps and min_samples as needed
dbscan.fit(X_scaled)

# Add the cluster labels to the original data
data['Cluster'] = dbscan.labels_

# Print the clustering results
print("Clustering Results:")
print(data[['Node Name', 'Cluster']])

# Analyze cluster characteristics
unique_labels = np.unique(dbscan.labels_)
for label in unique_labels:
    if label == -1:
        print("\nNoise:")
    else:
        print(f"\nCluster {label}:")
    cluster_data = data[data['Cluster'] == label]
    print(cluster_data[columns_for_clustering].describe())

# Visualize the clusters using a scatter plot matrix
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fig = plt.figure(figsize=(16, 16))
    ax = pd.plotting.scatter_matrix(data[columns_for_clustering], c=data['Cluster'], marker='o', hist_kwds={'bins': 20}, s=60, alpha=0.8, ax=fig.gca())

    # Remove axis labels and ticks
    for sub_ax in ax.ravel():
        sub_ax.set_xticks([])
        sub_ax.set_yticks([])
        sub_ax.set_xticklabels([])
        sub_ax.set_yticklabels([])

    # Add a main title
    fig.suptitle('Scatter Plot Matrix', fontsize=20)

    # Add a legend
    unique_labels = np.unique(dbscan.labels_)
    colors = plt.cm.get_cmap('viridis', len(unique_labels))
    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors(i), markersize=8) for i in range(len(unique_labels))]
    labels = ['Noise' if label == -1 else f'Cluster {label}' for label in unique_labels]
    fig.legend(handles, labels, title='Clusters', loc='upper right', fontsize=12)

# Adjust layout
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()

# Determine the level of criticality based on cluster characteristics
print("\nCluster Criticality:")
cluster_metrics = []
for label in unique_labels:
    if label == -1:
        cluster_name = 'Noise'
    else:
        cluster_name = f'Cluster {label}'
    cluster_data = data[data['Cluster'] == label]
    cluster_mean = cluster_data[columns_for_clustering].mean()
    cluster_metrics.append(cluster_mean)
cluster_criticality = pd.DataFrame(cluster_metrics, columns=columns_for_clustering)
cluster_criticality.index = [cluster_name for label in unique_labels]
print(cluster_criticality)
