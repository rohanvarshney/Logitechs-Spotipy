# pip install spotipy
import os
import sys
import time
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError
from functools import cmp_to_key

from PIL import Image
import requests
from io import BytesIO

'''
<Resources/Info>
https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-features/
https://developer.spotify.com/documentation/web-api/reference/tracks/get-audio-analysis/
Pitch Data: https://en.wikipedia.org/wiki/Pitch_class
Mode Data: Major=1, Minor=0
Time Signature Data: Beats per bar/measure
Top Tracks Valid-values: short_term, medium_term, long_term
Example Website: http://107.170.81.187:8080/public/top
'''

def print_list_of_lists(listOfLists):
	numberOfElements = len(listOfLists[0])
	for i in range(numberOfElements):
		for list in listOfLists:
			print(list[i])
	'''for list in listOfLists:
		for element in list:
			print(element)
			'''

def test_spotify_user(user):
	displayName = user['display_name']
	follower = user['followers']['total']
	print()
	print("~~~ Welcome to Spotify, " + displayName + "!")
	print("~~~ You have " + str(follower) + " followers.")
	print()

def get_playlist_data(playlistName, spotifyObject):
	desired_playlist = object()
	playlists = spotifyObject.current_user_playlists()
	# print(json.dumps(playlists, sort_keys=True, indent=4))
	for playlist in playlists['items']:
		print("Playlist Name: ", playlist['name'])
		if (playlist['name'] in playlistName):
			desired_playlist = playlist

	# print(json.dumps(desired_playlist, sort_keys=True, indent=4))
	results = spotifyObject.user_playlist_tracks(username, desired_playlist['id'])
	tracks = results['items']
	while results['next']:
		results = spotifyObject.next(results)
		tracks.extend(results['items'])

	trackListNames, trackListAlbums, trackListArtists, trackListIDs, acousticnessData, danceabilityData, durationData, energyData, instrumentalnessData, keyData, livenessData, loudnessData, modeData, speechinessData, tempoData, timeSignatureData, valenceData = ([] for i in range(17))

	for track in tracks:
		#print(json.dumps(track['track'], sort_keys=True, indent=4))
		trackListIDs.append(track['track']['id'])
		trackListNames.append(track['track']['name'])
		trackListArtists.append(track['track']['artists'][0]['name'])
		trackListAlbums.append(track['track']['album']['name'])




	errors = 0
	for trackListID in trackListIDs:
		songFeatures = spotifyObject.audio_features(trackListID)
		if songFeatures is None:
			continue
		for feature in songFeatures:
			if feature is None:
				print('A track has a problem.')
				errors = errors + 1
			if feature is not None:
				print(json.dumps(feature, sort_keys = True, indent = 4))
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
	# Make all prints be redirected to the output.txt file
	sys.stdout = open('{name}.txt'.format(name = playlistName), 'wt')
	print_list_of_lists([trackListNames, trackListAlbums, trackListArtists, trackListIDs, acousticnessData, danceabilityData, durationData, energyData, instrumentalnessData, keyData, livenessData, loudnessData, modeData, speechinessData, tempoData, timeSignatureData, valenceData])

def get_x_term_data(spotifyObject, lengthOfTerm):
	currentfaves = spotifyObject.current_user_top_tracks(limit=500, offset=0, time_range=lengthOfTerm)

	trackListNames, trackListIDs, acousticnessData, danceabilityData, durationData, energyData, instrumentalnessData, keyData, livenessData, loudnessData, modeData, speechinessData, tempoData, timeSignatureData, valenceData = ([] for i in range(15))

	topTracks = currentfaves['items']
	for item in topTracks:
		trackListIDs.append(item['id'])
		trackListNames.append(item['name'])
	for trackListID in trackListIDs:
		songFeatures = spotifyObject.audio_features(trackListID)
		if songFeatures is None:
			continue
		for feature in songFeatures:
			if feature is None:
				print('A track has a problem.')
				errors = errors + 1
			if feature is not None:
				print(json.dumps(feature, sort_keys = True, indent = 4))
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

	# Make all prints be redirected to the output.txt file
	sys.stdout = open('{term}.txt'.format(term = lengthOfTerm), 'wt')
	print_list_of_lists([trackListNames, trackListIDs, acousticnessData, danceabilityData, durationData, energyData, instrumentalnessData, keyData, livenessData, loudnessData, modeData, speechinessData, tempoData, timeSignatureData, valenceData])

# https://note.nkmk.me/en/python-pillow-concat-images/
def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


def get_user_top_albums(spotifyObject):
	# get all the user's saved tracks
	print('executing get_user_top_albums')
	results = spotifyObject.current_user_saved_tracks()
	print('retrieved current_user_saved_tracks')
	albums = dict()
	album_cache = dict()

	# iterate over each saved track and get the album information
	page = 0
	itemnum = 0
	printed = False
	while results['items']:
		print(f'on page {page}...')
		for item in results['items']:
			# print(f'on item {itemnum}')
			album = item['track']['album']
			if not printed:
				print(album)
				printed = True
			album_id = album['id']
			album_cache[album_id] = album
			album_name = album['name']
			album_artist = album['artists'][0]['name']
			if album_id not in albums.keys():
				albums[album_id] = 1
				# print(spotifyObject.album(album_id)['name'], 1)
			else:
				albums[album_id] = albums[album_id] + 1
				# print(spotifyObject.album(album_id)['name'], albums[album_id])
			itemnum = itemnum + 1
		page = page + 1
		if results['next']:
			results = spotifyObject.next(results)
		else:
			break
	print('retrieved all albums from current_user_saved_tracks')

	# remove items with only one/two item(s), we don't care about those
	sample_item = None
	for key in list(albums.keys()):
		if albums[key] < 3:
			 del albums[key]
	print('removed non-pertinent albums')


	def compare(album_id1, album_id2):
		# print(album_id1, album_id2)
		album_liked_songs1 = albums[album_id1]
		album_liked_songs2 = albums[album_id2]
		album_total_songs1 = album_cache[album_id1]['total_tracks']
		album_total_songs2 = album_cache[album_id2]['total_tracks']
		album_proportion1 = (album_liked_songs1 / album_total_songs1)
		album_proportion2 = (album_liked_songs2 / album_total_songs2)
		# print(album_proportion1, album_proportion2)
		score = (album_proportion1 * album_proportion1) - (album_proportion2 * album_proportion2)
		# print('score', score)
		if score == 0:
			return album_liked_songs1 - album_liked_songs2
		return score

	sorted_albums = sorted(albums, key=cmp_to_key(compare), reverse=True)
	print('sorted albums based on likeness score')

	print('sample of an album JSON below')


	print('Here is your Album Wrapped:')
	# print out the album information
	rank = 1
	for album_id in sorted_albums:
		album_name = album_cache[album_id]['name']
		album_artist = album_cache[album_id]['artists'][0]['name']
		album_liked_songs_number = albums[album_id]
		album_song_count = album_cache[album_id]['total_tracks']
		print(f'{rank}: {album_name} by {album_artist}. {album_liked_songs_number}/{album_song_count}.')
		rank = rank + 1


	base_image = None
	limit_num = 0
	for album_id in sorted_albums:
		if limit_num > 10:
			break
		album_object = album_cache[album_id]
		album_image_url = album_cache[album_id]['images'][0]['url']
		img_response = requests.get(album_image_url)
		album_image = Image.open(BytesIO(img_response.content))
		if base_image is None:
			base_image = album_image
		else:
			base_image = get_concat_h(base_image, album_image)
		limit_num = limit_num + 1
	base_image.save('test.jpg')
	return



username = sys.argv[1] # f.e. 'python spotify.py rohanvar'
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
# Create our spotifyObject
spotifyObject = spotipy.Spotify(auth=token)
user = spotifyObject.current_user()
test_spotify_user(user)

'''
Playlist Name:  Logitech's Lean ✨
Playlist Name:  95.1 📡
Playlist Name:  The 1209 Album 🙇🏽‍♂️
Playlist Name:  Public Rolex Collection 🔊
Playlist Name:  Sad Snoozes 💤
Playlist Name:  BollyGOOD 💃🏽
'''
# get_playlist_data("BollyGOOD 💃🏽", spotifyObject)
# get_x_term_data(spotifyObject, "short_term")
# get_x_term_data(spotifyObject, "long_term")
get_user_top_albums(spotifyObject)
