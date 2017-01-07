import sys
import string
import requests
import urllib
import json
import re


soundcloud_url = raw_input("Please enter a URL: ")

def get_trackid_single_song(soundcloud_url):
	client_id = "fDoItMDbsbZz8dY16ZzARCZmzgHBPotA"
	resolve_url = "https://api.soundcloud.com/resolve.json?url="
	s = requests.get(resolve_url + soundcloud_url + "&client_id=" + client_id)
	s = s.content
	trackid = json.loads(s)
	track_name = trackid["title"]
	print track_name
	trackid = str(trackid["id"])
	print "Track ID: " + trackid

	return track_name, trackid

def get_trackids_playlist(soundcloud_url):

	#Get playlist URL into the right format
	soundcloud_url = soundcloud_url.split("https://")
	soundcloud_url = soundcloud_url[1]

	client_id = "c8ce5cbca9160b790311f06638a61037"
	app_version = "1481130054"
	resolve_url = "https://api-mobi.soundcloud.com/resolve?permalink_url=https%3A//" + soundcloud_url + "&client_id=" + client_id + "&format=json&app_version=" + app_version
	playlist_id_request = requests.get(resolve_url)

	# Get the Playlist ID
	playlist_id_request = playlist_id_request.content
	playlist_id_request = json.loads(str(playlist_id_request))
	playlist_id = str(playlist_id_request["id"])
	print "Playlist ID: ", playlist_id_request["id"]

	# Get the Permalink URLs for each track and put them into a list

	playlist_api_url = "http://api.soundcloud.com/playlists/" + playlist_id + "?client_id=" + client_id
	playlist_urls = requests.get(playlist_api_url)
	permalink_urls = json.loads(playlist_urls.content)
	print "Amount of tracks in the playlist:", len(permalink_urls["tracks"])

	permalink_url = []
	trackid = []
	track_title = []

	for index in range(len(permalink_urls["tracks"])):
		permalink_url.append(index)
		trackid.append(index)
		track_title.append(index)
		permalink_url[index] = permalink_urls["tracks"][index]["permalink_url"]
		trackid[index] = permalink_urls["tracks"][index]["id"]
		track_title[index] = permalink_urls["tracks"][index]["title"]
		print index + 1, "\t", trackid[index], "\t", permalink_url[index]

	return permalink_url, trackid, track_title

def download_track(trackid, song_url, track_title):
	trackid = str(trackid)
	song_url = str(song_url)
	client_id = "c8ce5cbca9160b790311f06638a61037"
	get_mp3_url = "https://api.soundcloud.com/i1/tracks/" + trackid + "/streams?client_id=" + client_id + "&app_version=1482339819"
	mp3_url = requests.get(get_mp3_url)
	file_mp3_url = mp3_url.content[21:]
	x = '"'
	url_split = file_mp3_url.split(x)
	file_mp3_url = url_split[0]
	#print mp3_url

	#Step 3: Replace the \u0026 with &
	file_mp3_url = file_mp3_url.replace("\u0026", "&")

	#Download the track
	urllib.urlretrieve(file_mp3_url, track_title + ".mp3")


# Checks, whether the URL is a playlist or not
if '/sets' in soundcloud_url:
	permalink_url, trackid, track_title = get_trackids_playlist(soundcloud_url)

	for index in range(len(trackid)):
		print track_title[index]
		download_track(trackid[index], permalink_url[index], track_title[index])

	print "Done!"


else:	
	track_name, trackid = get_trackid_single_song(soundcloud_url)
	download_track(trackid, soundcloud_url, track_name);
	print "Done!"