#export SPOTIPY_CLIENT_ID='ca7d8ea9cda54fb8b9140214fcb1aa1f'
#export SPOTIPY_CLIENT_SECRET='4821503f455d48458d4f19d8d1fa7d1a'
#export SPOTIPY_REDIRECT_URI='http://google.com/'
# copy and paste the above three lines in Terminal
import os
import sys
import time
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError

#Get the username from terminal
# python spotify.py rohanvar    ---> rohanvar is the username
username = sys.argv[1]
#https://open.spotify.com/user/rohanvar?si=slMxEVGFQ7SBK85tV7bhng

ID='ca7d8ea9cda54fb8b9140214fcb1aa1f'
SECRET='4821503f455d48458d4f19d8d1fa7d1a'
URI='http://google.com/'
scope = 'user-top-read user-library-read playlist-read-private'


# Erase cache and prompt for user permission
try:
	token = util.prompt_for_user_token(username, scope, ID, SECRET, URI)
except:
	os.remove(f".cache-{username}")
	token = util.prompt_for_user_token(username, scope, ID, SECRET, URI)


#Create our spotifyObject
spotifyObject = spotipy.Spotify(auth=token)
user = spotifyObject.current_user()
#print(json.dumps(user, sort_keys=True, indent=4))

displayName = user['display_name']
follower = user['followers']['total']


print()
print("~~~ Welcome to Spotify, " + displayName + "!")
print("~~~ You have " + str(follower) + " followers.")
print()
start = time.time()


logitechLeanPlaylist = object()
NineFiveOnePlaylist = object()


playlists = spotifyObject.current_user_playlists()
print(json.dumps(playlists, sort_keys=True, indent=4))
for playlist in playlists['items']:
	if (playlist['name'] == "Logitech's Lean"):
		logitechLeanPlaylist = playlist
	if (playlist['name'] == "95.1"):
		NineFiveOnePlaylist = playlist


results = spotifyObject.user_playlist_tracks(username, logitechLeanPlaylist['id'])
tracks = results['items']
while results['next']:
	results = spotifyObject.next(results)
	tracks.extend(results['items'])


trackListNames = []
trackListIDs = []
for track in tracks:
	trackListIDs.append(track['track']['id'])
	trackListNames.append(track['track']['name'])
	#print(json.dumps(track['track'], sort_keys=True, indent = 4))


#print(trackListIDs)
#print(trackListNames)


# https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/
acousticnessData = []
danceabilityData = []
durationData = []
energyData = []
instrumentalnessData = []
keyData = [] #https://en.wikipedia.org/wiki/Pitch_class
livenessData = []
loudnessData = []
modeData = [] #Major=1, Minor=0
speechinessData = []
tempoData = []
timeSignatureData = [] #Beats per bar/measure
valenceData = []

#https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-analysis/
# Potential use?

errors = 0

'''
for trackListID in trackListIDs:
	songFeatures = spotifyObject.audio_features(trackListID)
	if songFeatures is None:
		continue
	for feature in songFeatures:
		#print(json.dumps(feature, sort_keys = True, indent = 4))
		if feature is None:
			#raise Exception("This song has a problem.")
			print('A track has a problem.')
			errors = errors + 1
		if feature is not None:
			acousticnessData.append(feature['acousticness'])
			danceabilityData.append(feature['danceability'])
			durationData.append(feature['duration_ms'])
			energyData.append(feature['energy'])
			instrumentalnessData.append(feature['instrumentalness'])
			keyData.append(feature['key'])
			livenessData.append(feature['liveness'])
			loudnessData.append(feature['loudness'])
			modeData.append(feature['mode'])
			speechinessData.append(feature['speechiness'])
			tempoData.append(feature['tempo'])
			timeSignatureData.append(feature['time_signature'])
			valenceData.append(feature['valence'])
'''


size = len(tempoData)
print(errors)

#Make all prints be redirected to the output.txt file
#sys.stdout = open('output.txt', 'wt')
'''
print(size)
print(acousticnessData)
print(danceabilityData)
print(durationData)
print(energyData)
print(instrumentalnessData)
print(keyData)
print(livenessData)
print(loudnessData)
print(modeData)
print(speechinessData)
print(tempoData)
print(timeSignatureData)
print(valenceData)
'''
#print(size)


for name in trackListNames:
	print(name)

for element in acousticnessData:
	print(element)
for element in danceabilityData:
	print(element)
for element in durationData:
	print(element)
for element in energyData:
	print(element)
for element in instrumentalnessData:
	print(element)
for element in keyData:
	print(element)
for element in livenessData:
	print(element)
for element in loudnessData:
	print(element)
for element in modeData:
	print(element)
for element in speechinessData:
	print(element)
for element in tempoData:
	print(element)
for element in timeSignatureData:
	print(element)
for element in valenceData:
	print(element)




'''
print(json.dumps(VARIABLE, sort_keys=True, indent=4))

https://github.com/plamere/spotipy/tree/master/examples
'''


delta = time.time() - start
#print ("program performed in %.2f seconds" % (delta,))


#sys.stdout = open('faves.txt', 'wt')
#http://107.170.81.187:8080/public/top
currentfaves = spotifyObject.current_user_top_tracks(limit=500, offset=0, time_range='long_term')
trackListIDs = []
trackListNames = []

topTracks = currentfaves['items']
for item in topTracks:
	trackListIDs.append(item['id'])
	trackListNames.append(item['name'])

#print(trackListIDs)

sys.stdout = open('output.txt', 'wt')
for trackListID in trackListIDs:
	songFeatures = spotifyObject.audio_features(trackListID)
	if songFeatures is None:
		continue
	for feature in songFeatures:
		#print(json.dumps(feature, sort_keys = True, indent = 4))
		if feature is None:
			#raise Exception("This song has a problem.")
			print('A track has a problem.')
			errors = errors + 1
		if feature is not None:
			acousticnessData.append(feature['acousticness'])
			danceabilityData.append(feature['danceability'])
			durationData.append(feature['duration_ms'])
			energyData.append(feature['energy'])
			instrumentalnessData.append(feature['instrumentalness'])
			keyData.append(feature['key'])
			livenessData.append(feature['liveness'])
			loudnessData.append(feature['loudness'])
			modeData.append(feature['mode'])
			speechinessData.append(feature['speechiness'])
			tempoData.append(feature['tempo'])
			timeSignatureData.append(feature['time_signature'])
			valenceData.append(feature['valence'])



for name in trackListNames:
	print(name)

for element in acousticnessData:
	print(element)
for element in danceabilityData:
	print(element)
for element in durationData:
	print(element)
for element in energyData:
	print(element)
for element in instrumentalnessData:
	print(element)
for element in keyData:
	print(element)
for element in livenessData:
	print(element)
for element in loudnessData:
	print(element)
for element in modeData:
	print(element)
for element in speechinessData:
	print(element)
for element in tempoData:
	print(element)
for element in timeSignatureData:
	print(element)
for element in valenceData:
	print(element)
