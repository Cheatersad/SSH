from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import pandas as pd
import warnings

data = pd.read_csv('node_outputs.csv')
columns_for_clustering = data.columns[5:]
X = data[columns_for_clustering]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=0.95)
X_reduced = pca.fit_transform(X_scaled)

X_train, X_test, data_train, data_test = train_test_split(X_reduced, data, test_size=0.2, random_state=42)

best_score = -1
best_params = {}

param_grid = {
    'n_clusters': [2, 3, 4, 5],
    'init': ['k-means++', 'random'],
    'max_iter': [100, 200, 300],
    'n_init': [10, 20, 30]
}

for n_clusters in param_grid['n_clusters']:
    for init in param_grid['init']:
        for max_iter in param_grid['max_iter']:
            for n_init in param_grid['n_init']:
                kmeans = KMeans(n_clusters=n_clusters, init=init, max_iter=max_iter, n_init=n_init, random_state=42)
                kmeans.fit(X_train)
                labels = kmeans.predict(X_train)
                score = silhouette_score(X_train, labels)
                if score > best_score:
                    best_score = score
                    best_params = {'n_clusters': n_clusters, 'init': init, 'max_iter': max_iter, 'n_init': n_init}

kmeans_best = KMeans(n_clusters=best_params['n_clusters'], init=best_params['init'], max_iter=best_params['max_iter'], n_init=best_params['n_init'], random_state=42)
kmeans_best.fit(X_train)
y_pred = kmeans_best.predict(X_test)

silhouette_avg = silhouette_score(X_test, y_pred)
ch_score = calinski_harabasz_score(X_test, y_pred)
db_score = davies_bouldin_score(X_test, y_pred)

data_train['Cluster'] = kmeans_best.labels_

cluster_metrics = []
for i in range(best_params['n_clusters']):
    cluster_data = data_train[data_train['Cluster'] == i]
    cluster_mean = cluster_data[columns_for_clustering].mean()
    cluster_metrics.append(cluster_mean)

cluster_criticality = pd.DataFrame(cluster_metrics, columns=columns_for_clustering)
cluster_criticality.index = ['Cluster ' + str(i) for i in range(best_params['n_clusters'])]

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    fig = plt.figure(figsize=(16, 16))
    ax = pd.plotting.scatter_matrix(data_train[columns_for_clustering], c=data_train['Cluster'], marker='o', hist_kwds={'bins': 20}, s=60, alpha=0.8, ax=fig.gca())
    plt.subplots_adjust(wspace=0.05, hspace=0.05)
    for sub_ax in ax.ravel():
        sub_ax.set_xticks([])
        sub_ax.set_yticks([])
        sub_ax.set_xticklabels([])
        sub_ax.set_yticklabels([])
    fig.suptitle('Scatter Plot Matrix (Training Data)', fontsize=20)
    unique_labels = data_train['Cluster'].unique()
    colors = plt.cm.get_cmap('viridis', len(unique_labels))
    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=colors(i), markersize=8) for i in range(len(unique_labels))]
    fig.legend(handles, ['Cluster {}'.format(i) for i in unique_labels], title='Clusters', loc='upper right', fontsize=12)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()


print("\nCluster Criticality (Training Data):")
cluster_metrics = []
for i in range(best_params['n_clusters']):
    cluster_data = data_train[data_train['Cluster'] == i]
    cluster_mean = cluster_data[columns_for_clustering].mean()
    cluster_metrics.append(cluster_mean)

cluster_criticality = pd.DataFrame(cluster_metrics, columns=columns_for_clustering)
cluster_criticality.index = ['Cluster ' + str(i) for i in range(best_params['n_clusters'])]
print(cluster_criticality)
