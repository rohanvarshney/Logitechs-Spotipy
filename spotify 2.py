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

def get_liked_tracks_with_high_energy(spotifyObject, energyCutoff=0.8):
    # Get user's liked songs (tracks in the Liked Songs playlist)
    results = spotifyObject.current_user_saved_tracks()
    # Filter liked songs with energy greater than 0.7
    high_energy_tracks = set()

    page = 0
    while results['items']:
        print(f'on page {page}...')
        for item in results['items']:
            trackListID = item['track']['id']
            songFeatures = spotifyObject.audio_features(trackListID)
            if songFeatures is None:
                continue
            for feature in songFeatures:
                if feature is None:
                    continue
                if feature is not None:
                    if feature['energy'] > energyCutoff:
                        high_energy_tracks.add(trackListID)
                        continue
        if results['next']:
            results = spotifyObject.next(results)
            page = page + 1
        else:
            break
    return list(high_energy_tracks)





def create_new_playlist_with_tracks(spotifyObject, playlist_name, track_ids):
    # Create a new public playlist
    playlist = spotifyObject.user_playlist_create(user=spotifyObject.me()['id'], name=playlist_name, public=True)
    # Add tracks to the new playlist
    original_list = list(track_ids)
    batch_size = 50
    batched_lists = []
    for i in range(0, len(original_list), batch_size):
        batch = original_list[i:i+batch_size]
        batched_lists.append(batch)
    
    for batch_list in batched_lists:
        spotifyObject.playlist_add_items(playlist_id=playlist['id'], items=batch_list)
    return


    
def create_new_playlist_with_high_energy_liked_tracks(spotifyObject):
	# Get high-energy liked tracks
    high_energy_tracks_ids = get_liked_tracks_with_high_energy(spotifyObject)

    # Create a new playlist and add high-energy tracks to it
    if high_energy_tracks_ids:
        print(high_energy_tracks_ids)
        playlist_name_input = input("Enter the name of the new playlist: ")
        # Create the new playlist and add high-energy tracks
        create_new_playlist_with_tracks(spotifyObject, playlist_name_input, high_energy_tracks_ids)
        print(f"New playlist '{playlist_name_input}' with high-energy liked tracks has been created!")
    else:
        print("No high-energy liked tracks found.")



username = sys.argv[1] # f.e. 'python spotify.py rohanvar'
ID='ca7d8ea9cda54fb8b9140214fcb1aa1f'
SECRET='4821503f455d48458d4f19d8d1fa7d1a'
URI='http://google.com/'
scope = 'user-top-read user-library-read playlist-read-private playlist-modify-public'

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
# get_user_top_albums(spotifyObject)
create_new_playlist_with_high_energy_liked_tracks(spotifyObject)
# create_new_playlist_with_tracks(spotifyObject, "TestPlaylist2", ['6viRjWnLyctmtvcYfEePwh', '6btyEL6NwUa97Nex9cZFvo', '5KNJ2qBD92lNfdcdcHmzEY', '5YY8EsBdUYAg1NJQIvgCEj', '4mL55yuSeFzQmyRO7K2X7G', '3vq4QqcaVIRePdxSxRQmPX', '5OGRK9nb9luUPlWcFTmsAD', '21h0F6z614BHwNDDfkjZ7Q', '1SqHHN5Mqy13gHbDGjTaU7', '3sl4dcqSwxHVnLfqwF2jly', '7gA8vO4KhJ8iJpns5qTUYS', '74DDMxe4UFFV9atMMlG6FA', '7oVEtyuv9NBmnytsCIsY5I', '59YkyPuZCXyiLmcmSNKRtH', '7cGFbx7MP0H23iHZTZpqMM', '4QNpBfC0zvjKqPJcyqBy9W', '0VpFFXnT2kNjqJmTv57aZi', '4CVOUJki8YUWol3jhLphgs', '2RjpDxBii8EvC6p6wxwCSz', '0fzyk9aEI7To2GvapPdTgl', '5JuOjj6HZO1619LMpHwG8U', '6eEAevjmfFiu5SSvH0DRY8', '4cHZ7W5R81upaIGZfqWxbB', '4ila6GeGBPGmJTGRoHOV5E', '6M14BiCN00nOsba4JaYsHW', '2NBP1dxxf6hyoJfE7kmR0o', '5P9lfNxIoCTCcInZRSdjW4', '1knElcYQT1E135uHsny2IL', '20hsdn8oITBsuWNLhzr5eh', '6xq3Bd7MvZVa7pda9tC4MW', '2NQBsh7D6bDS5tv5VcvdoN', '492M9gtZYZsdjPPlyHhMHG', '3HtCaD8SkNbjy3TrEcS4Km', '4S7yPbt2aW7N3pthEpcP7S', '3Ql8FoHiDuU5aKCekZInYR', '14EBj3BdbkGQtnQQJav444', '16gpaVpjUdhDE7qPnEyrXt', '4QKp78XQvd4Sr8Qj0vEXYv', '1XlpaijGmAY0pWe16oucrC', '7IDV5mTDlniHiW4L3ps8yR', '7IZwjpLSvABzr1E7xeBaRJ', '4CNpsYx0PjzXeGa8BzHdm2', '5IUP91X8fKfJnWQgCHT9dN', '3JT3s6xGkhSzu1v6EYXuby', '5Rcs3fREgibWujLUlUb8KA', '5ZvcukFVP22G9BzQ0QrcCS', '0suLmBuEbatdochI4tHduq', '5NbplIIyJnnAPrUWeJAbQ4', '1vBmaijoCBoqmwc3zs5n3s', '3gYSqxntZtlR4com7pDv9f', '1Vej0qeQ3ioKwpI6FUbRv1', '7dFikRPQuLFz4PdCw4ZvCy', '7DFk01bs34zPldpuAQsfwY', '15uMARayIr55AVXNnKYCT3', '3UFn9DppMdzAiEY46eDSNr', '04AYgtKFrpldRXe5y0LNGQ', '0bTDn1Cg64Uhlt6rcXiX8B', '4Vhq6lkvT1f9mna51yFdoj', '5kVXjAxYDkN57tZQi0JKya', '4sikeWZ1jdsLyhPOzThPfh', '3iVFBmRZtDXdp8tFGpK0Et', '7EvAlx0lOLbZgCKH50wnUU', '1buWPBwvTd6VnIdBV48yQM', '1IecjpoB4D0fT01g9qiJvU', '0upcwsWXAgtSFAG72Ry9em', '1Q4jb2UjtWUDUojHsB8mLY', '51uSQlZ2GYuFWRS3o2vKz6', '4oHHfupA93zfZyXHNPxmXo', '6W6GpWzBiu58bRg1TMTqBT', '7LR85XLWw2yXqKBSI5brbG', '1d5UuboIPRMD4HaU3yycKC', '02GnSPkHSU3cZldlwnwQnT', '4mQpBIJKBpd8lcrtZ73SP8', '1XSSm7oKOzNE8oUapjIRWV', '7ufw2AvrztmY9Y8pU41FfK', '0GVBPuCT3pBrXCdY3Uiy5B', '18lR4BzEs7e3qzc0KVkTpU', '6AzYQlmA1lEZz4wHbfnnaN', '3eu9JkPNIsK4vsLj1WN7Li', '5k7wy2Ek7y6kSQ4fER7w0E', '449LomMxWudGSkUsZjchZs', '6loBU3j6zvULZMIlD7n4JW', '7fSFdF4ymvjiOIr1EzB2pu', '5egqKwgK5r5rvGD1LrtR7J', '5ogIZnw2wGLe4i69uqmESi', '0WVv6KMRkZKMMqkcmcQJOK', '1kWgDpdw6kALKUrErh0GbE', '6jbN3ibWMut3lTVjUhYGgW', '3h5gMWp1KJQkLBgCtG5EgH', '1cYtqvYDbuzjgSJsAkTRaH', '6oDHAjaJJjwwgoAuMIeY9K', '41jZ1WPNVy0sqKNBpURO5X', '7tRXTDi87CiAqU5sIBQfIC', '2M38zNMI7gCoCwfEUZQPq5', '4cFwhwH5ydnHgB0Tv3lZsm', '4Urv6Lbjqs42xLqjxahwvQ', '69uxyAqqPIsUyTO8txoP2M', '2aCsRmHTuWPL7WnL5uSijc', '4MtDnnAJ1AtWit10FRmZdW', '5uHYcK0nbEYgRaFTY5BqnP', '2W6bC4K4e6y42HnYTA5yHO', '6MqW785UN5QF9UZ6ocL5s9', '7jVFODQGxTvxMoVXL1I9NK', '2xO3tUdbE42rjV81NrQJ0S', '2Qr5Ao8BkVYf5kBkGMfBnw', '0pn8eHCvZsBAF9Y9wfv4rt', '2cZXlLwkRmDww37tbEygXl', '3hfDl12AHis9jgRi5wMqFo', '6JNluWWlzWmrW1LKR5X2SN', '1iP5UMdOsGz6EdltGbbcb7', '4LLvxxkWtt818FNO3cbsdo', '2ynLMerQLCKAYtMMrF6pSd', '4CBAKSus371zX1icqqyyUC', '6YVbCxw3Yqyj4dRomrXPhl', '0Ph6L4l8dYUuXFmb71Ajnd', '4o1zYFH5QWKu3E4MiC6lgE', '6NsxPxFzZ18TKBcTgxX3dh', '7yn0E97MoGLBaW8mqIwqNr', '0Fx59cxbrS4v9CsOMUtQEM', '3rKCyhZEFRstr6dKKlO5GM', '5bxlyO2txvnfHjvNpYmYQu', '7BGg9wSF98j6FzvHGkq3f0', '6U82eC2OHyiQM4Wr5Bejar', '5jOMxC9ezgFPGSMSn1zJ5S', '0GFXbdgwVYO8Dw6BG8MLfL', '6H503HrJOogVycvQkq2SuG', '4IpdzHwvjFQaivAVRpnmFC', '2bMgRkcHX3tcBmwQOQV7RJ', '55KYlnsC6nYnr3IykbmJwE', '575urseJcD6iGioNWuQy3H', '6IYS7wNZxRBvLpwMZDbcdP', '0dAfw35k2hBsnbSl74AVJF', '5HadIAY3Oray8VKuv3shgQ', '26VnEKps0l0JWIrdx2E62G', '5CVZeK7bOC9QxYcZ9gJ5X2', '0VhuTK5k3OZOCQy2bHQdz5', '6Q9bMlh2AhykET9yr437FQ', '5FihcmME7NlwW8KbYOaHVH', '2xYTrkiW9gYynSFv5duRiy', '1gHbvt2Q3Br0mZcCEQa8GH', '05Oz1nvpGtWFE8lU7sVbPu', '62LsspNBMWFGDa5Arpytm3', '6CTG85NJI1Wm60pxTSRNwL', '223t7TwvWm5PuE1IuWpRZM', '2XgOPFAoff5oLfufCRB0xC', '3UuylZ8AmrOT4OfjGofTCN', '2uxL6E8Yq0Psc1V9uBtC4F', '4p8hEugsVDbekDgDH4QagU', '19eEhd1hR5TPAcpNrhdwkN', '1mw50a4DGRhkdMX7nOoLE4', '2Ggpu9s4UP2fO7bjgBMiss', '2igwFfvr1OAGX9SKDCPBwO', '4mbJ90SPdL9WdItbkWDkpv', '1gxHYlzU60Wz5NnFm1Yv33', '76BFt6hGCrZhGHrGh0N3uC', '1h4qhOmbd7eQLeMNOg8nWQ', '08dWCKcPuFjUsAkJt4tnaW', '4B8sgPFTHrILkBxfNLRCI0', '5SLhbyOJgcKGTDNWaQN91M', '45zvStEMsXp8z45OQRhWFJ', '2oNYsdCasRRlz1shXFAz7D', '53RG6rDqEvGDsZ0Ijr3ur1', '1gsnHGopfdevZt7gbmygOq', '4wmrfUPuvK9phVehREZZ1X', '0Jh9EBGN205Yc7JN2zZ2f1', '4xxcd6cnmFfj67AmnaF6tc', '0FOPDqF7FBZwHITfKHMvLK', '00KfIFi2TpAaQGPbRbFbKJ', '4vgCpNUUcpEIBifidhQOnR', '5HJGzB7sZleFrrDvr0pRo4', '36MGfjOTOwx1udRX5dDnoJ', '0h2DNYdWq3mWE8Ov2A03oU', '3LdZ1fFzohRUbcNI9sa8jV', '3hgFwotX5fCegIUb49jQem', '2ZAx6NDhX2yE5aL5ueEQgY', '1gihuPhrLraKYrJMAEONyc', '74P9ePdXM4i11PN9ximdLe', '6ScGFNxhQPaVuvlzjSQrd1', '57a2GZdXL4q0dpXgtoEnUr', '1YGvvTwsMI67MJCmQpLAPO', '1vl4tsBmTXygX47k8c2ixM', '3LS2MlVs2sHPvw8JnzgmFJ', '2oTdiDj4AawNeeYFz8bipG', '0HSLQNyOkBZupUBurCHZdC', '1r1fPuhj9H4VdXr7OK6FL5', '76YXmewvHFse7tBeOTtSx3', '1VTvqPZc50yS6MiWw520Kh', '2gPwE07qAJBp6B0VlPXnVD', '6txvQu0zUbiqG24A8XMLnK', '3drHOAgmNmMtCyCBNPQjUq', '6GEm8jphIDl1LfV83qxoP1', '7cFFhb9Wz2ZXLSpEk2VDKd', '0ZmkjefPVLvloVSgtmRu5M', '5K5LbSTVuKKe1KGMNfBgIW', '6AGcLDEgd0FXwHAxUaSg84', '3JT0mVof65rIHpRZITwRx1', '7Ie9W94M7OjPoZVV216Xus', '3yRoV3XxY866zW6PZuwzXy', '5e1D90g8borqYvbIt2S2Mr', '7xqeIdLJSf3bgmZ7vUvHrE', '4BRvD5QdauTo8EuUvYchu3', '5gZtOj758iAYTKWpFd2HzM', '5ZcMWSpUeUPvO87FkSZbJB', '5Fli1xRi01bvCjsZvKWro0', '2V4TXFqYWE09VSk6ORqD7j', '60SvhHtwefT0e2G7i7kOH3', '5i1RcRRodwy5lelFacx6AM', '7BIE80fFY0ARACh4HsHXcT', '5e45GhSF18JYoLpaq2F48h', '0dMYPDqcI4ca4cjqlmp9mE', '3oLXQgbcC34Oo4gFHCeTmi', '2dUkCUXXoknwsLwuGaL4bA', '6JHYKezmmJSKqRMq5zPaUn', '52jHZXtW03EI5qCv3NKg1E', '74DRF0JULR2WIADSTtoVs3', '5fBx0CyspbLYEO073IHxGN', '4L6QpiLxCLok9wZfFIdiqF', '6jKVU3e0gnQLj3iifJBvVN', '0qke9ep1LfxZvPHETd3N2e', '3W1XPf7mvuQcWQB7U7MbTM', '3SwlakM6VX47IwG0Wll5ek', '6N43Qgg9jx21vfMkTYvSi3', '7Bw56mGeOVbBBWBSLg356s', '4FRKGdgOh9G5sub5GiknfS', '6zBFQ5dWHEmEx2RDoZ1ZP2', '42Cvh6itGBXTIXqcGWsi9f', '2bCQHF9gdG5BNDVuEIEnNk', '4p16E9c9Ig6xFMGS3Y82mT', '2tbvAGoLMQgjvfgW7naBiE', '5PUawWFG1oIS2NwEcyHaCr', '1djVUAbgkPikakGN5SkUzk', '2VgbvKdaSOXWByBKYgBsEc', '7wVuc5To4LyVZvZllNSlpB', '7LIQNY8P7ZGxilKVX88MF1', '3cQGb2POE359G9WH81bF60', '0hkRONsyMGzkhJGc56L5v0', '2xLwq7JoNv9ZJdFehKC2K5', '37lzNf9Ylt8JXZcBk1yuCD', '0CnRxBOItBbzq9vDgyRpXj', '2MZrOmrVxRmmOoFW6dhenG', '083lOftWDnrpSSL7u9p53d', '3VeW0pO2pae144rAX2oXPP', '3v5amQiIq5pxKicUJESLJ8', '6Dyyp0X3WfuN25IRPgePyl', '43x5gxJ3WWadu1qx6nXhPY', '6i1T2HszgQegmbChKbvshh', '3OpQNTSzF5pVMTUfwuycM1', '2gQK13gXYZRq2MgvPJyHx8', '4mtCNSfEwcwvm9iLG1bADY', '5eURoU1GtJypHBQJTXWTPN', '6KASl3S3bdyrn8GxjlVimb', '5TrwpMwZ16VI64BP5gKHWZ', '2uBhGx3m5iJrtsql8Qk00j', '2bns5HD6pmOhfqcPuVkw8A', '1bPRhOz3nOfEIoLjB1YYT3', '6ZAjDjl1rJ9Z70gsiocw25', '7uATh1ln4JvMbQwsXOdCeo', '4JqgUZ4yZqjeEmgJNsuUjX', '24LS4lQShWyixJ0ZrJXfJ5', '27gUeiai56GKF6TxvmPJut', '62hWYjPL57rbUd5rhvI3Of', '6xzCQrXrn0uOOKBQZK1zsF', '1YoMveQNDS1h2kJrv2OMSc', '37q95xoPlZZzzymKJmEFIB', '6kbSicgkNZI3Drcy5PIgw6', '5sqs99n1gCg2Ygg3eNz6rJ', '3UgSQu6WwrXfKKDq019IHE', '6uwjDA0Qi6hk8C6lPJIMc9', '1Aj3mTJznujGX2ov6Op1cZ', '02dPa4nXABwnFzjZosKxsk', '7EIq46YALncEzg0fYvLo0L', '45uPKvMUFmObuDYka9AnKa', '3rZDUjPQBkja9EDMQM1qqL', '4tjLYTXFqZhkUDga4bQ0yl', '2xhwpVFdD9KZC2R1KIRcHI', '7aq8t9D82PJuqH7TFT4W6O', '7e0nXDIIa6hFqI4HmuanLP', '0sS9XWjcZ0FgB3QkDiVwyT', '3Rx5i283zQ87tvbvOZGVXc', '6EMIPL540mVil5ixO38WVm', '1XkVZKfViRyaQcBWUEVwrd', '7s0qlp1ibUxVXLsOM0YWia', '1gMT8boiNdGWiYy7HQHyZk', '2CEYIgQM8cloUeNaFOwT1C', '4qb2AKvnaDdvJJnKmxo9ST', '1tEto4JrqNmBZFH5uAiYqb', '5YE5Pjo8LQkzYLTyZOY9DV', '3FmsKw8ie3KLC5273nH6wD', '7iA8BlFVOityG3DGPExJtx', '17AtR2mHWKdDXCPUFydJKL', '4jyKXQsaWSRO46NKkoxcoe', '0mBL2JwjNYKtdFacHxvtJt', '7k271swC1weiuiU0pI8kxw', '15JINEqzVMv3SvJTAXAKED', '2nNaw1QUcqiEX6pBFxcpp3', '3ryXl6OFAr9fzUpIjAnHIY', '1cTZMwcBJT0Ka3UJPXOeeN', '1VuBmEauSZywQVtqbxNqka', '2gZUPNdnz5Y45eiGxpHGSc', '6gbALcuMskVVi3IiynsWrB', '6f49kbOuQSOsStBpyGvQfA', '1M61PaGIKWdams4A2NInOc', '2NXLCUySCK9odGGCGIzbOA', '5XRHGXut00SrJUFmcn2lQF', '5cgKosPPj5Cs9a2JQufUc1', '6kiauSlWtddVQx4JwJx51p', '29TPjc8wxfz4XMn21O7VsZ', '7emLx4rVwr0tPyjktu7A7U', '0H9SbdtxCAWQVuhdbqw0b3', '6HRzMSkNA8VwC80OD5Qy40', '2SSFvQBwsxeazzo7z5l9gD', '04hFLMBiGOrTeuZBVnCGhh', '3OmoIMCAaJtvM9B9HuWArW', '7H03ThGkXAeXMpmHjjgwGn', '0Qp1IH1EkRCNabfgzxNMUT', '5x43kajvJQfmcRktDpz9Og', '7GGJ7uPEFfjhfx2UD3ZNYX', '7gTSX0ZtLKl305F1sHMXgT', '7eD2qAkE1EAs9poZhpVD6o', '63MvWd6T6yoS7h4AJ4Hjrm', '2iLd8cKIhE3KLnpz2m6A8B', '2YRDTr0reanrGZOTsWXdek', '5ATXoiPaHKClnFxQmBDLFB', '1jZ8zhjl5Gvg7AHfKJKDXz', '4CWhc9FaMMfBTt4ANjfbOf', '6tIilLqzatIQU1RDP1kUSu', '0se928CIhZPlfVGi3A6zrx', '3zZ009FB8sc8JghwVrbLFq', '0oaF3jKUzt03X2Ze06jxt3', '5IzDsRBAo3JaTpho5BcyGk', '7jtdG988aYR7IkFObSWfJe', '6LPCVPG7SmilgxuWQOOZ3f', '1JZ7WVfz2MBNRc14O9Qx7D', '6urYuTdNG7TJWLQ5hDqacj', '2mwnYvlLVP465u9V9wjUGj', '2WWP0IPX9xFjAMraNHX390', '4ap6JHm4Jr0pRbtDmibsGq', '17xeyhLPJcyywTHzRwPkdq', '2opvzpPKzw8W3RTmnpc0RW', '3xmJo7JydhDml7GAS9YTcN', '18e3XXYCv4Tx8uUl1mP3CN', '41VvpaE99PfuaINUeTshtF', '01pOtDU5YHWbxuNBzlRUem', '4o08tZyCpk2exnO9HGoAO5', '3jksOdXCaDXyGiZ7L4YZbp', '2D1uFfnp5ylRPNYbdEa5Kv', '0UFDKFqW2oGspYeYqo9wjA', '4BHYJiAqyqGtN267ypm1ke', '0csz09qS2n8Jo7LogHKu7j', '2PaAG9RNH3HKL57LKc3GJI', '2WfaOiMkCvy7F5fcp2zZ8L', '0usLRFLmYXYahKNgXxsuJc', '2nDTyZyFYSPXrwxt3n7EkI', '19u20B0E3KO1copzKVSJxi', '6Kynli1iHBqJRWUCohcV9h', '0waK9D203FQO5FpMmfjxBw', '6QOfkcfdrEZ2nwi5R9KJTK', '6haTrice1PU59Kd7esp3w1', '4eu27jAU2bbnyHUC3G75U8', '0KiKfllNTmhImvXVIHqR0z', '03abU98g89psJPe49XO4UW', '352hnmCMucGmz4OhIey1Wq', '5ghIJDpPoe3CfHMGu71E6T', '0buUlnWLraOX28CQLuR1dE', '5BJSZocnCeSNeYMj3iVqM7', '6wSY0LlCBb5QLQIjMiVv5v', '7AJtoJnHV80IMEHgQs6YvU', '4J3I4jpAtNjsclcs99jzeF', '1LRV5Gyq5pp3CozJbXaiNS', '7KlTFTpy7dXLzr2NtLkvG6', '6yJYMvn6845hnoMY2ypZN6', '09yhMTRqQ1I1dniu3PoIQi', '3UaP2PQwhA31keZXt7oPLA', '39x8osSFRUQarEgkYwyJsT', '5tytAc5ROJYRJuIeREv6sZ', '3u1Er1rkjn1oSz1xdZH3ZD', '60ON92YSFjEzHljyWsnVHy', '4U72is70mlDtchLsnV3qo1', '1JNoTMJh0IbhJ8ehTwUrKm', '7Hm2bCSurV5Fn2bdwevmou', '5HGXuAy0YA1GBRkAny0cvV', '6fORBVECjNDJ1gdq5uuoAz', '5VQ0SPGs7vdzQCIzsHTNUz', '2GEnvQgSJhedm2sqZlOP8o', '7kTDTw5oX657IHsmkXvnjJ', '69TeyCRYS543Sys0zFD1xV', '1L0YPzmCa4KtbyADm8WlJt', '0pPGUL7171TRGgI6wyP8wP', '3jje1pbXn6itQcppcWPKuJ', '7xxxQG1BupSnOBo4qId9kl', '680su2851wO74z7uNBcAbF', '4iNoqM0X35E4AK4pzWFW5z', '4nqZIPw2PNo1W54kEmswJ2', '1Ztd5zEfCEPsRa05waBbHu', '2XhAPy0qOe4Q0OnSv3mS8o', '10lT3pp9QERGOWiIzLx4We', '0wIhWLNLIOmzQ89B3rtTd3'])
