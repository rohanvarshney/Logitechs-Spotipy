from sklearn.datasets.samples_generator import make_blobs
from yellowbrick.cluster import InterclusterDistance
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from yellowbrick.cluster import KElbowVisualizer
from yellowbrick.cluster import SilhouetteVisualizer
from sklearn.preprocessing import MinMaxScaler


def kmeans_main(df):
    df_new = df[['danceability', 'energy', 'tempo', 'valence']]
    print("Initial dataframe")
    print(df_new.head)

    kmeans_with_pca(df, df_new)
    # kmeans_wo_pca(df, df_new)

    elbow(df_new)


def kmeans_with_pca(df, df_new):
    pcaKmeans = pca_method(df_new)
    _kmeans = KMeans(n_clusters=3)
    X_clustered = _kmeans.fit_predict(pcaKmeans)
    print("X Clustered")
    print(X_clustered)
    df['KMeansCluster'] = pd.DataFrame(X_clustered)
    print("df with clusters")
    print(df.head)
    centroids = _kmeans.cluster_centers_
    print("Centroids")
    print(centroids)
    LABEL_COLOR_MAP = {0: 'r', 1: 'g', 2: 'b'}
    label_color = [LABEL_COLOR_MAP[l] for l in X_clustered]

    plt.figure(figsize=(9, 7))
    plt.scatter(pcaKmeans[:, 0], pcaKmeans[:, 2], c=label_color, alpha=0.5)
    plt.scatter(centroids[:, 0], centroids[:, 1], c='black', s=50)
    plt.title("KMeans Performed with PCA")
    plt.show()


def kmeans_wo_pca(df, df_new):
    _kmeans = KMeans(n_clusters=3).fit(df_new)
    labels = _kmeans.labels_
    print("Labels")
    print(labels)
    df['KMeansCluster'] = pd.DataFrame(labels)
    print("df with clusters")
    print(df.head)
    centroids = _kmeans.cluster_centers_
    print("Centroids")
    print(centroids)

    LABEL_COLOR_MAP = {0: 'r', 1: 'g', 2: 'b'}
    label_color = [LABEL_COLOR_MAP[l] for l in labels]

    plt.scatter(df['danceability'], df['energy'], c=label_color, s=50, alpha=0.5)
    plt.scatter(centroids[:, 0], centroids[:, 1], c='black', s=50)
    plt.title("KMeans Performed without PCA")
    plt.show()


def pca_method(df):
    X_std = StandardScaler().fit_transform(df)
    # Create a PCA instance: pca
    pca = PCA(n_components=3)
    principalComponents = pca.fit_transform(X_std)
    print("Principal components")
    plt.figure(figsize=(9, 7))
    plt.scatter(principalComponents[:, 0], principalComponents[:, 1], c='black', alpha=0.5)
    plt.title("PCA Plot")
    plt.xlabel('PCA 1')
    plt.ylabel('PCA 2')
    plt.show()
    print("PCA")
    print(principalComponents)
    return principalComponents


def elbow(X):
    mms = MinMaxScaler()
    mms.fit(X)
    data_transformed = mms.transform(X)
    model = KMeans()
    visualizer = KElbowVisualizer(model, k=(1, 10), timings=False)

    visualizer.fit(data_transformed)  # Fit the data to the visualizer
    visualizer.show()  # Finalize and render the figure


# Unused Methods


def intercluster(X):
    model = KMeans(3)
    visualizer = InterclusterDistance(model)

    visualizer.fit(X)
    visualizer.show()


def silhouette(X):
    for i in range(2, 4):
        model = KMeans(i, random_state=42)
        visualizer = SilhouetteVisualizer(model, colors='yellowbrick')
        visualizer.fit(X)  # Fit the data to the visualizer
        visualizer.show()  # Finalize and render the figure


def usingMakeBlobs(df):
    print("Doing KMeans")
    centerNum = 3
    print("Size: " + str(df.shape[0]))
    X, _ = make_blobs(n_samples=df.shape[0], centers=centerNum, n_features=4, random_state=0)

    df_sample = pd.DataFrame(X, columns=['danceability', 'energy', 'tempo', 'valence'])
    print(df_sample)

    print("Showing scatterplot")
    plt.scatter(X[:, 0], X[:, 1])
    plt.show()

    kmeans = KMeans(n_clusters=centerNum, init='k-means++', max_iter=300, n_init=10, random_state=0)
    pred_y = kmeans.fit_predict(X)
    plt.scatter(X[:, 0], X[:, 1])
    plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=300, c='red')
    plt.show()

    kmeans = KMeans(n_clusters=centerNum).fit(df_sample)
    y_pred = kmeans.fit_predict(X)

    plt.scatter(
        X[y_pred == 0, 0], X[y_pred == 0, 1],
        c='lightgreen',
        marker='s', edgecolor='black',
        label='cluster 1'
    )

    plt.scatter(
        X[y_pred == 1, 0], X[y_pred == 1, 1],
        c='orange',
        marker='o', edgecolor='black',
        label='cluster 2'
    )

    plt.scatter(
        X[y_pred == 2, 0], X[y_pred == 2, 1],
        c='lightblue',
        marker='v', edgecolor='black',
        label='cluster 3'
    )

    plt.scatter(
        kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1],
        s=250, marker='*',
        c='red', edgecolor='black',
        label='centroids'
    )
    plt.legend(scatterpoints=1)
    plt.grid()
    plt.show()

    df['Cluster'] = y_pred
    print('Head')
    print(df.head())
    intercluster(X)
    return df
