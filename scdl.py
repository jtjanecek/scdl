import sys
import string
import requests
import urllib
import json
import re
import os
import os.path
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

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
	#print "Amount of tracks in the playlist:", len(permalink_urls["tracks"])

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
		#print index + 1, "\t", trackid[index], "\t", permalink_url[index]

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

	#Step 3: Replace the \u0026 with &
	file_mp3_url = file_mp3_url.replace("\u0026", "&")

	#Download the track
	filename = u"%s" % track_title + ".mp3"
	if not os.path.exists(filename):
		with open(filename, "wb") as file:
			filedl = requests.get(file_mp3_url, stream=True)
			file_length = filedl.headers.get('content-length')
			file_length = int(file_length)
			downloaded = 0
			for data in filedl.iter_content(chunk_size=file_length/100):
				downloaded += len(data)
				file.write(data)
				done = int(50 * downloaded / file_length)
				sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )
				sys.stdout.flush()

			#print "\n"
	else:
		pass

def get_tags(soundcloud_url):
	client_id = "fDoItMDbsbZz8dY16ZzARCZmzgHBPotA"
	resolve_url = "https://api.soundcloud.com/resolve.json?url="
	a = requests.get(resolve_url + soundcloud_url + "&client_id=" + client_id)
	a = a.content
	tags = json.loads(a)
	track_name = tags["title"]
	
	artist = str(tags["user"]["username"])
	cover = tags["artwork_url"]
	if cover:
		coverflag = 1
		cover = cover.replace("large", "t500x500")
		cover_download = requests.get(cover)
		open('cover.jpg', 'w').write(cover_download.content)
	else:
		coverflag = 0

	return track_name, artist, coverflag

def get_album_name(soundcloud_url):
	client_id = "fDoItMDbsbZz8dY16ZzARCZmzgHBPotA"
	resolve_url = "https://api.soundcloud.com/resolve.json?url="
	a = requests.get(resolve_url + soundcloud_url + "&client_id=" + client_id)
	a = a.content
	tags = json.loads(a)
	album = tags["title"]
	return album


def add_tags(title, artist, coverflag):
	try:
		audio = EasyID3("%s" % title + ".mp3")
	except mutagen.id3._util.ID3NoHeaderError:
		audio = mutagen.File("%s" % title + ".mp3", easy=True)
		audio.add_tags()
	audio['title'] = u"%s" % title
	audio['artist'] = u"%s" % artist
	if '/sets/' in soundcloud_url:
		audio['album'] = u"%s" % album
	else:
		audio['album'] = u"SoundCloud"

	audio.save()
	audio = MP3("%s" % title + ".mp3", ID3=ID3)
	if coverflag == 1:
		audio.tags.add(
			APIC(
				encoding=3,
				mime='image/jpeg',
				type=3,
				desc=u'Cover',
				data=open('cover.jpg').read()
				)
			)
	audio.save()

def delete_albumart():
	os.remove("cover.jpg")

def get_user_id (profile_url):
	url = "https://api-mobi.soundcloud.com/resolve?permalink_url=" + profile_url + "&client_id=c8ce5cbca9160b790311f06638a61037&format=json&app_version=1481130054"
	user_id = requests.get(url)
	#print user_id.content
	user_id = json.loads(user_id.content)
	user_id = user_id["id"]
	return user_id

def get_user_tracks(user_id):
	url = "https://api-v2.soundcloud.com/users/" + str(user_id) + "/tracks?representation=&client_id=fDoItMDbsbZz8dY16ZzARCZmzgHBPotA&limit=5000&offset=0&linked_partitioning=1&app_version=1486402392"
	playlist = requests.get(url)
	playlist = playlist.content
	playlist = json.loads(playlist)
	track_ids = []
	permalink_url = []
	track_name = []
	for index in range(len(playlist["collection"])):
		track_ids.append(index)
		permalink_url.append(index)
		track_name.append(index)
		track_ids[index] = playlist["collection"][index]["id"]
		permalink_url[index] = playlist["collection"][index]["permalink_url"]
		track_name[index] = playlist["collection"][index]["title"]
	return track_ids, permalink_url, track_name


#Hide the cursor
try:
	sys.stdout.write("\033[?25l")
	sys.stdout.flush()
	#fix URL if it is a single track out of a playlist
	if '?in=' in soundcloud_url:
		soundcloud_url = soundcloud_url.split('?in=')
		soundcloud_url = soundcloud_url[0]

	#check for pattern in url, if it is a user page or a track page of a user
	user_re = re.compile(r"^https:\/\/soundcloud.com\/[abcdefghijklmnopqrstuvwxyz\-_1234567890]{1,}$")
	user_re_tracks = re.compile(r"^https:\/\/soundcloud.com\/[abcdefghijklmnopqrstuvwxyz\-_1234567890]{1,25}\/tracks$")
	if (user_re.match(soundcloud_url)) or (user_re_tracks.match(soundcloud_url)):
		user_id = get_user_id(soundcloud_url)
		track_ids, permalink_url, track_title = get_user_tracks(user_id)
		for index in range(len(track_ids)):

			if "/" in track_title[index]:
				track_title[index] = track_title[index].replace("/", "-")

			print '\r[{}]/[{}] \t{}'.format(index + 1, max(range(len(track_ids))) + 1, track_title[index], track_title[index])
			download_track(track_ids[index], permalink_url[index], track_title[index]),
			print "\r                                                    "
			#go to line above
			sys.stdout.write("\033[F")
			sys.stdout.flush() 
			track_name, artist, coverflag = get_tags(permalink_url[index])
			if "/" in track_name:
				track_name = track_name.replace("/", "-")

			album = artist
			add_tags(track_name, artist, coverflag)
			if coverflag == 1:
				delete_albumart()

		print "Done!"
		#Show cursor again
		sys.stdout.write("\033[?25h")
		sys.stdout.flush()

	# Checks, whether the URL is a playlist or not
	if '/sets' in soundcloud_url:
		permalink_url, trackid, track_title = get_trackids_playlist(soundcloud_url)

		for index in range(len(trackid)):
			if "/" in track_title[index]:
				track_title[index] = track_title[index].replace("/", "-")
			print '\r[{}]/[{}] \t{}'.format(index + 1, max(range(len(trackid))) + 1, track_title[index], track_title[index])
			download_track(trackid[index], permalink_url[index], track_title[index]),
			print "\r                                                    "
			#go to line above
			sys.stdout.write("\033[F")
			sys.stdout.flush() 
			track_name, artist, coverflag = get_tags(permalink_url[index])
			if "/" in track_name:
				track_name = track_name.replace("/", "-")
			album = get_album_name(soundcloud_url)
			add_tags(track_name, artist, coverflag)
			if coverflag == 1:
				delete_albumart()

		print "Done!"
		#Show cursor again
		sys.stdout.write("\033[?25h")
		sys.stdout.flush()


	else:	
		track_name, trackid = get_trackid_single_song(soundcloud_url)
		if "/" in track_name:
				track_name = track_name.replace("/", "-")
		download_track(trackid, soundcloud_url, track_name);
		track_name, artist, coverflag = get_tags(soundcloud_url)
		add_tags(track_name, artist, coverflag)
		if coverflag == 1:
			delete_albumart()
		print "\nDone!"
		#Show cursor again
		sys.stdout.write("\033[?25h")
		sys.stdout.flush()

except:
	#print "\nAborting..."
	sys.stdout.write("\033[?25h")
	sys.stdout.flush()