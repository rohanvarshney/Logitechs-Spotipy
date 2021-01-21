''' 
Import the following:
	pip install spotipy
	pip install pandas
	pip install sklearn
	pip install numpy
	pip install yellowbrick
'''
# GitHub Page: https://github.gatech.edu/pages/aprasad72/ML_Group9_Spotify/
# GitHub Project Repository: https://github.gatech.edu/aprasad72/ML_Group9_Spotify
# GitHub Code Repository: https://github.com/daivi-patel/ML2020Spotipy
# Latest Doc: https://docs.google.com/document/d/1eSUnJm6WjIFtKie7tdZVAGiTQSp9C-1wxb62fzIGm4Q/edit?usp=sharing

'''
 Run command: 	python spotify.py <YOUR_USERNAME> "<PLAYLIST_NAME>"
 f.e. 	python spotify.py rohanvar "Today's Top Hits"
'''

'''
Notes:
	It must be a playlist name that you follow.
	Your username is your username that you use when signing in.
'''

'''
Team Notes:
	"Today's Top Hits": 50 songs that are mainly pop
	"Logitech's Lean": ~3000 songs of all sorts of genres
	"95.1": ~120 songs of a decent divesity of genres
'''

import numpy as np
import os
import sys
import json
import spotipy
import random
import spotipy.util as util
import pandas as pd
from sklearn import preprocessing
import sklearn.utils
from sklearn import metrics
from sklearn.metrics import accuracy_score, f1_score, recall_score, precision_score
from sklearn.datasets.samples_generator import make_blobs
from sklearn.cluster import KMeans
from sklearn.cluster import DBSCAN
from sklearn import tree
from sklearn import svm
from sklearn import datasets
from sklearn import model_selection
from sklearn.svm import SVC
from yellowbrick.cluster import InterclusterDistance
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from yellowbrick.cluster import KElbowVisualizer
from yellowbrick.cluster import SilhouetteVisualizer
from yellowbrick.datasets import load_nfl
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import AffinityPropagation

from kmeans_methods import *


def get_genres_from_track(track, spotifyObject):
    genres = []
    album = spotifyObject.album(track['track']['album']['external_urls']['spotify'])
    if (len(album["genres"]) == 0):
        artist = spotifyObject.artist(track["track"]["artists"][0]["external_urls"]["spotify"])
        genres = artist["genres"]
    else:
        genres = album["genres"]
    print("genres:", genres)
    return genres


def clean_genres_list(genre_list):
    i = 0
    for genre in genre_list:
        genre = "hip hop" if "hop" in genre else genre
        genre = "pop" if "pop" in genre else genre
        genre = "rap" if "rap" in genre else genre
        genre = "house" if "house" in genre else genre
        genre = "indie" if "indie" in genre else genre
        genre = "edm" if "edm" in genre else genre
        genre = "dance" if "dance" in genre else genre
        genre = "rock" if "rock" in genre else genre
        genre = "metal" if "metal" in genre else genre
        genre = "soul" if "soul" in genre else genre
        genre = "r&b" if "r&b" in genre else genre
        genre = "soundtrack" if "soundtrack" in genre else genre
        genre = "electronic" if "electronic" in genre else genre
        genre = "raggaeton" if "raggaeton" in genre else genre
        genre = "bollywood" if "sufi" in genre else genre
        genre = "bollywood" if "bollywood" in genre else genre
        genre = "bollywood" if "filmi" in genre else genre
        genre = "bollywood" if "chutney" in genre else genre
        genre_list[i] = genre
        i = i + 1

    genre_list = list(set(genre_list))
    print(genre_list)
    return genre_list


def get_playlist_data(playlistName, spotifyObject):
    print("Getting playlist!")
    desired_playlist = object()
    playlists = spotifyObject.current_user_playlists()
    for playlist in playlists['items']:
        if (playlist['name'] == playlistName):
            desired_playlist = playlist

    print("Getting playlist tracks!")
    results = spotifyObject.user_playlist_tracks(username, desired_playlist['id'])
    tracks = results['items']
    while results['next']:
        results = spotifyObject.next(results)
        tracks.extend(results['items'])

    trackListNames, trackListIDs, genreData, danceabilityData, energyData, tempoData, valenceData = ([] for i in
                                                                                                     range(7))

    print("Getting playlist track names, genres, and IDs!")
    for track in tracks:
        genres = get_genres_from_track(track, spotifyObject)
        genres = clean_genres_list(genres)
        if (len(genres) == 0): genres.append("alternative")
        genre = genres[0]  # pick first genre

        trackListIDs.append(track['track']['id'])
        trackListNames.append(track['track']['name'])
        genreData.append(genre)

    print("Getting playlist track traits:")
    errors = 0  # Not used but may be important
    i = 0  # index
    trackList = []
    for trackListID in trackListIDs:
        songFeatures = spotifyObject.audio_features(trackListID)
        json_dict = {'name': trackListNames[i]}
        i += 1
        print("Track " + str(i) + ": " + trackListNames[i - 1])
        if songFeatures is None:
            errors = errors + 1
            continue
        for feature in songFeatures:
            if feature is None:
                print('A track has a problem.')
                errors = errors + 1
            if feature is not None:
                json_dict['danceability'] = feature['danceability']
                json_dict['energy'] = feature['energy']
                json_dict['tempo'] = feature['tempo']
                json_dict['valence'] = feature['valence']
                json_dict['genre'] = genreData[i - 1]
                # Why these use lists but not above?
                tempoData.append(feature['tempo'])

                trackList.append(json_dict)

    print("Normalizing Tempo!")
    tempo = {'tempo': tempoData}
    dataframe = pd.DataFrame(tempo)
    t = dataframe[['tempo']].values.astype(float)
    min_max_scaler = preprocessing.MinMaxScaler()
    tempoScaled = min_max_scaler.fit_transform(t)
    tempoNormalized = pd.DataFrame(tempoScaled)

    '''
    Wait, we normalized tempo with respect to itself.
    The maximum possible tempo could be 255, but our playlist has a max of 120.
    Is that equitable? It's not a fair representative value of all ranges.
    Our playlist may have danceability values of only .3 to .7.
    Normalizing tempo as such above guarantees a 0 and a 1 value.
    Therefore, we should normalize all columns.
    '''

    for index, _dict in enumerate(trackList):
        trackList[index]['tempo'] = tempoNormalized[0][index]

    return trackList


def convert_to_df(tracklist_dicts):
    df = pd.DataFrame(tracklist_dicts)
    return df


def kMeans(df):
    kmeans_main(df)


def dbScan(df):
    print("Doing DBSCAN")

    ss = preprocessing.StandardScaler()
    # two dimensions only
    # df_adjusted = pd.DataFrame(df, columns=['tempo', 'valence'])  # only working with 2 dimensions? *****
    df_new = df[['danceability', 'energy', 'tempo', 'valence']]
    df_adjusted = pca_method(df_new)
    new_df = ss.fit_transform(df_adjusted)
    # pick values of eps and min_points??
    db = DBSCAN(eps=0.5, min_samples=5).fit(new_df)  # values???
    y_pred = db.fit_predict(new_df)

    df['Cluster'] = y_pred
    print('Head')
    print(df.head())

    # print(df)
    return df


def decisionTree(df, playlist_name, random_state, training_size):  # Rohan
    print("Decision Tree")
    X = pd.DataFrame(df, columns=['danceability', 'energy', 'tempo', 'valence'])
    Y = pd.DataFrame(df, columns=['genre'])
    decisionTree = tree.DecisionTreeClassifier(random_state=random_state)
    songs = Y.size
    trainingSize = training_size
    trainingSongs = round(songs * 0.2)

    decisionTree = decisionTree.fit(X[0:trainingSongs], Y[0:trainingSongs])
    prediction = decisionTree.predict(X[trainingSongs:])
    prediction_df = pd.DataFrame(prediction)
    df['Predicted Genre'] = prediction_df

    print(pd.DataFrame(df, columns=['name', 'genre', 'Predicted Genre']))

    # https://mljar.com/blog/visualize-decision-tree/

    text_representation = tree.export_text(decisionTree)
    print(text_representation)

    accuracy = accuracy_score(Y[trainingSongs:], prediction_df, normalize=True)
    accuracyText = 'Accuracy: ' + str(accuracy)
    print(accuracyText)
    f1 = f1_score(Y[trainingSongs:], prediction_df, average='weighted')
    f1Text = 'F1: ' + str(f1)
    print(f1Text)
    recall = recall_score(Y[trainingSongs:], prediction_df, average='weighted')
    recallText = 'Recall: ' + str(recall)
    print(recallText)
    precision = precision_score(Y[trainingSongs:], prediction_df, average='weighted')
    precisionText = 'Precision: ' + str(precision)
    print(precisionText)

    class_names = decisionTree.classes_
    feature_names = X.columns

    fig = plt.figure(figsize=(50, 40))
    title = str(playlist_name) + "_decision_tree_" + str(random_state)
    titleLine2 = accuracyText + ", " + precisionText + ", " + f1Text
    titleLine3 = "Training Data Proportion: " + str(training_size)
    # Recall is not pertinent to the scope of this problem
    fig.suptitle(title + '\n' + titleLine2 + '\n' + titleLine3, fontsize=72)
    _ = tree.plot_tree(decisionTree,
                       feature_names=feature_names,
                       class_names=class_names,
                       filled=True)
    fig.savefig(str(playlist_name) + "_decision_tree_" + str(random_state) + "_" + str(training_size) + ".png")

    return df


def svm(df):  # SH
    print("SVM")
    X = pd.DataFrame(df, columns=['danceability', 'energy', 'tempo', 'valence'])
    Y = pd.DataFrame(df, columns=['genre'])
    # X_train, X_test, y_train, y_test = model_selection.train_test_split(X, Y, test_size=0.5,random_state=109) # 70% training and 30% test
    # clf = SVC(kernel='poly',degree=4).fit(X_train, y_train.values.ravel())
    # print("Test Accuracy :")
    # print(clf.score(X_test,y_test.values.ravel()))

    clf = SVC(kernel='poly').fit(X, Y.values.ravel())
    print("Model Accuracy :")
    print(clf.score(X, Y.values.ravel()))
    predict = clf.predict(X)
    prediction_df = pd.DataFrame(predict)
    df['Predicted Genre'] = prediction_df
    print(pd.DataFrame(df, columns=['name', 'genre', 'Predicted Genre']))

    return df


# print(df) #pandas DataFrame


username = sys.argv[1]
playlist_name = sys.argv[2]

print("Username: " + str(username))
print("Playlist Name: " + str(playlist_name))

ID = '9c6542bd7bd040cb8341e44cafbc9081'
SECRET = '2ddf5ad78a854889bcb4d28f1e226431'
URI = 'http://google.com/'
scope = 'user-top-read user-library-read playlist-read-private'

# Erase cache and prompt for user permission
try:
    token = util.prompt_for_user_token(username, scope, ID, SECRET, URI)
except:
    os.remove(f".cache-{username}")
    token = util.prompt_for_user_token(username, scope, ID, SECRET, URI)

# Create our spotifyObject
spotifyObject = spotipy.Spotify(auth=token)
user = spotifyObject.current_user()

tracklist_dicts = get_playlist_data(playlist_name, spotifyObject)

tracklist_df = convert_to_df(tracklist_dicts)
print("Tracklist head")
print(tracklist_df.head())

# ML Algorithms!


# KMeans - Daivi

# kMean_df = kMeans(tracklist_df)

'''
print('K-Mean Clusters')
# print(pd.DataFrame(kMean_df, columns=['name','Cluster']))
print(pd.DataFrame(kMean_df[kMean_df['Cluster']==0], columns=['name','Cluster']))
print(pd.DataFrame(kMean_df[kMean_df['Cluster']==1], columns=['name','Cluster']))
print(pd.DataFrame(kMean_df[kMean_df['Cluster']==2], columns=['name','Cluster']))


print("Cluster 0")
print(pd.DataFrame(kMean_df[kMean_df['Cluster']==0], columns=['danceability', 'energy', 'tempo', 'valence']).head())

print("Cluster 1")
print(pd.DataFrame(kMean_df[kMean_df['Cluster']==1], columns=['danceability', 'energy', 'tempo', 'valence']).head())

print("Cluster 2")
print(pd.DataFrame(kMean_df[kMean_df['Cluster']==2], columns=['danceability', 'energy', 'tempo', 'valence']).head())
'''

# DBSCAN - Anusha

dbscan_df = dbScan(tracklist_df) #eps, min_points

'''
print('DBSCAN Clusters')
print(pd.DataFrame(kMean_df, columns=['name','Cluster'])) #Whole thing
print(pd.DataFrame(dbscan_df[dbscan_df['Cluster']==0], columns=['name','Cluster'])) #specific clusters
print(pd.DataFrame(dbscan_df[dbscan_df['Cluster']==1], columns=['name','Cluster']))
print(pd.DataFrame(dbscan_df[dbscan_df['Cluster']==2], columns=['name','Cluster']))
'''

# Decision Tree - Rohan
# for x in range(3):
# 	for y in range(1, 8):
# 		fraction = y / 10
# 		random_state = random.randint(0, 4096)
# 		decisionTree(tracklist_df, playlist_name, random_state, fraction)

# SVM - SH
# svm(tracklist_df)


print("Done!")
