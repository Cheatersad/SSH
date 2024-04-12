#!/usr/bin/env python
# coding: utf-8

# In[7]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Read the CSV file
df = pd.read_csv("output_testing_sample.csv")

# Select specific columns from the DataFrame
columns = ['subscriber_count', 'NT_AMF_PCMD', 'NT_SGSN_PCMD', 'NT_MME_PCMD', 'Total']
df = df[columns]

# Normalize the data using StandardScaler
scaler = StandardScaler()
df_normalized = pd.DataFrame(scaler.fit_transform(df), columns=df.columns)

# Determine the optimal number of clusters using the elbow method (KMeans algorithm)
wcss = []
for i in range(1, 11):
    kmeans = KMeans(n_clusters=i, init='k-means++', random_state=42)
    kmeans.fit(df_normalized)
    wcss.append(kmeans.inertia_)

plt.figure(figsize=(10, 6))
plt.plot(range(1, 11), wcss)
plt.title('The Elbow Method (KMeans Algorithm)')
plt.xlabel('Number of Clusters')
plt.ylabel('WCSS')
plt.show()

# Choose the optimal number of clusters based on the elbow method
optimal_clusters = 3

# Apply KMeans clustering on the normalized data
kmeans = KMeans(n_clusters=optimal_clusters, init='k-means++', random_state=42)
cluster_labels = kmeans.fit_predict(df_normalized)

# Add the cluster labels to the original DataFrame
df['Cluster'] = cluster_labels

# Apply KMeans clustering on the subscriber count to determine the cluster ranges
kmeans_subscriber = KMeans(n_clusters=3, init='k-means++', random_state=42)
subscriber_labels = kmeans_subscriber.fit_predict(df[['subscriber_count']])

# Get the cluster centers for subscriber count
subscriber_centers = kmeans_subscriber.cluster_centers_

# Assign cluster names based on the subscriber count ranges determined by KMeans
cluster_names = []
for count in df['subscriber_count']:
    if count < subscriber_centers[0]:
        cluster_names.append('Low')
    elif count < subscriber_centers[1]:
        cluster_names.append('Moderate')
    else:
        cluster_names.append('Critical')

df['Cluster_Name'] = cluster_names

# Visualize the clusters using a pair plot
plt.figure(figsize=(12, 8))
sns.pairplot(data=df, hue='Cluster_Name', palette='viridis', diag_kind='kde')
plt.title('Pair Plot of Features Colored by Cluster Name (KMeans Algorithm)')
plt.show()

# Analyze the characteristics of each cluster
for name in df['Cluster_Name'].unique():
    cluster_data = df[df['Cluster_Name'] == name]
    print(f"Cluster: {name}")
    print("Number of data points:", len(cluster_data))
    print("Mean values:")
    print(cluster_data[columns].mean())
    print("Standard deviations:")
    print(cluster_data[columns].std())
    print()

# Analyze the distribution of data points across clusters
print("Distribution of data points across clusters:")
print(df['Cluster_Name'].value_counts())

# Visualize the distribution of data points across clusters
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x='Cluster_Name')
plt.title('Distribution of Data Points across Clusters (KMeans Algorithm)')
plt.xlabel('Cluster')
plt.ylabel('Count')
plt.show()

# Create a scatter plot of subscriber_count vs. Total, colored by Cluster_Name
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='subscriber_count', y='Total', hue='Cluster_Name', palette='viridis')
plt.title('Subscriber Count vs. Total Colored by Cluster Name (KMeans Algorithm)')
plt.xlabel('Subscriber Count')
plt.ylabel('Total')
plt.show()


# In[ ]:




