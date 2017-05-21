#scdl
# -*- coding: utf-8 -*-
import sys
import string
import requests
import urllib
import json
import re
import os
import os.path
import mutagen
import shutil
import tempfile
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC

client_id = u"2t9loNQH90kzJcsFCODdigxfp325aq4z"
app_version = u"1489155300"

def main():
	#get url from user
	soundcloud_url = unicode(raw_input("Please enter a URL: "))
	link_type, soundcloud_url = link_detection(soundcloud_url)
	hide_cursor()

	try:
		if link_type == 1:
			download_single_track(soundcloud_url)
			show_cursor()
		elif link_type == 2:
			download_playlist(soundcloud_url)
			show_cursor()
		elif link_type == 3:
			download_user_tracks(soundcloud_url)
			show_cursor()
		elif link_type == 4:
			download_user_likes(soundcloud_url)
		else:
			show_cursor()
	except:		
		show_cursor()

def link_detection(soundcloud_url):
	#Decides the type of link which was entered
	# 1 = single track
	# 2 = playlist
	# 3 = tracks of a user
	# 4 = likes of a user

	#Fix a missing https://
	https_regex = re.compile(r"^https:\/\/soundcloud\.com.{1,}$")
	if not (https_regex.match(soundcloud_url)):
		soundcloud_url = "{}{}".format(u"https://", soundcloud_url)

	#Fix URL if it is a single track out of a playlist
	if '?in=' in soundcloud_url:
		soundcloud_url = soundcloud_url.split('?in=')
		soundcloud_url = soundcloud_url[0]

	#URL is a playlist
	if '/sets' in soundcloud_url:
		return 2, soundcloud_url

	#URL for tracks of a user
	user_re_tracks_1 = re.compile(r"^https:\/\/soundcloud.com\/[abcdefghijklmnopqrstuvwxyz\-_1234567890]{1,}$")
	user_re_tracks_2 = re.compile(r"^https:\/\/soundcloud.com\/[abcdefghijklmnopqrstuvwxyz\-_1234567890]{1,25}\/tracks$")

	if (user_re_tracks_1.match(soundcloud_url)) or (user_re_tracks_2.match(soundcloud_url)):
		return 3, soundcloud_url

	#URL for likes of a user
	user_re_likes = re.compile(r"^https:\/\/soundcloud.com\/[abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ\-_1234567890]{1,}\/likes$")
	if (user_re_likes.match(soundcloud_url)):
		return 4, soundcloud_url

	#This is a single track
	else:
		return 1, soundcloud_url

def hide_cursor():
	sys.stdout.write("\033[?25l")
	sys.stdout.flush()

def show_cursor():
		sys.stdout.write("\033[?25h")
		sys.stdout.flush()

def download_single_track(soundcloud_url):
	trackid = get_track_id(soundcloud_url)
	print "Track ID:", trackid
	track_name, artist, coverflag, cover_file, description = get_tags(soundcloud_url)
	download_track(trackid, soundcloud_url, track_name)
	add_tags(track_name, artist, cover_file, 0, description)
	print "\nDone!"

def get_playlist_id(soundcloud_url):
	resolve_url = u"https://api-mobi.soundcloud.com/resolve?permalink_url=" + soundcloud_url + u"&client_id=" + client_id + u"&format=json&app_version=" + app_version
	playlist_id_request = requests.get(resolve_url)

	# Get the Playlist ID
	playlist_id_request = playlist_id_request.content
	playlist_id_request = json.loads(playlist_id_request)
	return unicode(playlist_id_request["id"])

def get_playlist_tracks(playlist_id):
	playlist_api_url = u"http://api.soundcloud.com/playlists/" + playlist_id + u"?client_id=" + client_id
	playlist_urls = requests.get(playlist_api_url)
	permalink_urls = json.loads(playlist_urls.content)

	album = permalink_urls["title"]

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

	return permalink_url, trackid, track_title, album

def download_playlist(soundcloud_url):
	playlist_id = get_playlist_id(soundcloud_url)
	print "Playlist ID:", playlist_id
	permalink_url, trackid, track_name, album = get_playlist_tracks(playlist_id)
	change_directory(album)
	track_name = []
	artist = []
	coverflag = []
	cover_file = []

	for index in range(len(trackid)):
		track_name.append(index)
		artist.append(index)
		coverflag.append(index)
		cover_file.append(index)
		track_name[index], artist[index], coverflag[index], cover_file[index], description[index] = get_tags(permalink_url[index])
		print u'\r[{}]/[{}] \t{}'.format(index + 1, max(range(len(trackid))) + 1, track_name[index], track_name[index])
		download_track(trackid[index], permalink_url[index], track_name[index]),
		print u"\r                                                    "
		#go to line above
		sys.stdout.write("\033[F")
		sys.stdout.flush()
		add_tags(track_name[index], artist[index], cover_file[index], album, description)

	print "Done!"

def add_tags(track_name, artist, cover_file, album, description):
	try:
		audio = EasyID3(u"%s" % track_name + u".mp3")
	except mutagen.id3._util.ID3NoHeaderError:
		audio = mutagen.File(u"%s" % track_name + u".mp3", easy=True)
		audio.add_tags()
	EasyID3.RegisterTextKey('comment', 'COMM')
	audio['title'] = u"%s" % track_name
	audio['artist'] = u"%s" % artist
	audio['comment'] = u"%s" % description

	if album is not 0:
		audio['album'] = u"%s" % album
	else:
		audio['album'] = u"SoundCloud"
	audio.save(v2_version=3)
	if cover_file is not 0:
	    with tempfile.NamedTemporaryFile() as out_file:
	    	shutil.copyfileobj(cover_file, out_file)
	        out_file.seek(0)

		audio = ID3(u"%s" % track_name + u".mp3")
		#audio[u"USLT::'eng'"] = (USLT(encoding=3, lang=u'en', desc=u'desc', text=description))
		audio.add(
			USLT(
				encoding=3,
				lang=u'eng',
				desc=u'desc',
				text=description
				)
			)
		audio.add(
			APIC(
				encoding=3,
				mime='image/jpeg',
				type=3,
				desc=u'Cover',
				data=out_file.read()
				)
			)
		audio.save(v2_version=3)

def download_track(trackid, song_url, track_name):
	trackid = str(trackid)
	song_url = str(song_url)
	get_mp3_url = "https://api.soundcloud.com/i1/tracks/" + trackid + "/streams?client_id=" + client_id + "&app_version=" + app_version
	mp3_url = requests.get(get_mp3_url)
	file_mp3_url = mp3_url.content[21:]
	x = '"'
	url_split = file_mp3_url.split(x)
	file_mp3_url = url_split[0]

	#Step 3: Replace the \u0026 with &
	file_mp3_url = file_mp3_url.replace("\u0026", "&")
	#Download the track
	filename = (u"%s" % track_name) + u".mp3"
	if not os.path.exists(filename):
		with open(unicode(filename), "wb") as file:
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

def download_user_tracks(soundcloud_url):
	user_id = get_user_id(soundcloud_url)
	print "User ID:", user_id
	track_ids, permalink_url, track_name, album = get_user_tracks(user_id)
	change_directory(album)
	track_name = []
	artist = []
	coverflag = []
	cover_file = []

	for index in range(len(track_ids)):
		track_name.append(index)
		artist.append(index)
		coverflag.append(index)
		cover_file.append(index)
		if get_tags(permalink_url[index]) == 0:
			continue

		track_name[index], artist[index], coverflag[index], cover_file[index], description[index] = get_tags(permalink_url[index])
		print u'\r[{}]/[{}] \t{}'.format(index + 1, max(range(len(track_ids))) + 1, track_name[index], track_name[index])
		download_track(track_ids[index], permalink_url[index], track_name[index]),
		print u"\r                                                    "
		#go to line above
		sys.stdout.write("\033[F")
		sys.stdout.flush()
		add_tags(track_name[index], artist[index], cover_file[index], album, description)

def download_user_likes(soundcloud_url):
	user_id = get_user_id(soundcloud_url)
	if user_id != None:
		print user_id
	else:
		print "Couldn't get user ID, exiting."
		return 0
	print "About to get likes..."
	track_ids, permalink_url, track_name, album = get_user_likes(user_id)
	print len(track_ids)

def get_user_likes(user_id):
	like_url = "https://api-v2.soundcloud.com/users/" + str(user_id) + "/likes?client_id=" + str(client_id) + "&limit=300&offset=0&linked_partitioning=1&app_version=" + str(app_version)
	print "Like URL:", like_url
	likes = requests.get(like_url)
	likes = likes.content
	with open("likes.txt", "w") as file:
		file.write(likes)
	likes = json.loads(likes)
	track_ids = []
	permalink_url = []
	track_name = []
	print "Made empty lists"
	for index in range(len(likes["collection"])):
		print "Inside loop"
		if likes["collection"][index]['track']:
			print "Found a like"
			track_ids.append(index)
			permalink_url.append(index)
			track_name.append(index)
			track_ids[index] = likes["collection"][index]["track"]["id"]
		else:
			print "This is not a track, this is a playlist"
		print track_ids(index)
		permalink_url[index] = likes["collection"][index]["track"]["permalink_url"]
		track_name[index] = likes["collection"][index]["track"]["title"]

	if likes["next_href"] is not None:
		track_ids, permalink_url, track_name = get_user_tracks_recursion(likes["next_href"], url, track_ids, permalink_url, track_name)

	return track_ids, permalink_url, track_name, album

def get_user_likes_recursion(next_href, first_url, track_ids, permalink_url, track_name):
	link_to_next_part = next_href.split("offset=")
	link_to_next_part = link_to_next_part[1].split("&representation=")
	link_to_next_part = link_to_next_part[0]
	link_to_next_part = first_url.replace("offset=0", "offset=" + str(link_to_next_part))
	next_part = requests.get(link_to_next_part)
	next_part = next_part.content
	next_part = json.loads(next_part)

	for index in range(len(next_part["collection"])):
		track_ids.append(next_part["collection"][index]["id"])
		permalink_url.append(next_part["collection"][index]["permalink_url"])
		track_name.append(next_part["collection"][index]["title"])

	if next_part["next_href"]:
		get_user_tracks_recursion(next_part["next_href"], first_url, track_ids, permalink_url, track_name)

	else:
		return track_ids, permalink_url, track_name


def change_directory(folder_name):
	if u"/" in folder_name:
		folder_name = folder_name.replace(u"/", u"-")
	if not os.path.exists(folder_name):
		os.makedirs(folder_name)
		os.chdir(folder_name)
	else:
		os.chdir(folder_name)

def get_tags(soundcloud_url):
	resolve_url = "https://api.soundcloud.com/resolve.json?url="
	a = requests.get(resolve_url + soundcloud_url + "&client_id=" + client_id)
	a = a.content
	tags = json.loads(a)
	if tags["duration"] == 30000:
		print "This is a SoundCloud Go Plus-only track, skipping download."
		return 0
	track_name = u"%s" % tags["title"]

	description = u"%s" % tags["description"]

	if u"/" in track_name:
		track_name = track_name.replace(u"/", u"-")
	if u"\\" in track_name:
		track_name = track_name.replace(u"\\", u"-")
	if u"|" in track_name:
		track_name = track_name.replace(u"|", u"-")
	if u":" in track_name:
		track_name = track_name.replace(u":", u"-")
	if u"?" in track_name:
		track_name = track_name.replace(u"?", u"-")
	if u"<" in track_name:
		track_name = track_name.replace(u"<", u"-")
	if u">" in track_name:
		track_name = track_name.replace(u">", u"-")
	if u'"' in track_name:
		track_name = track_name.replace(u'"', u"-")
	if u"*" in track_name:
		track_name = track_name.replace(u"*", u"-")


	artist = u"%s" % tags["user"]["username"]
	cover = tags["artwork_url"]
	if cover is not None:
		coverflag = 1
		cover = cover.replace("large", "t500x500")
		cover_request = requests.get(cover, stream=True)
		cover_file = cover_request.raw
		#cover_download = requests.get(cover)
		#open('cover.jpg', 'w').write(cover_download.content)
	else:
		coverflag = 0

	if (coverflag == 0):
		cover_file = 0
		return  track_name, artist, coverflag, cover_file, description
	return track_name, artist, coverflag, cover_file, description

def get_user_id(soundcloud_url):
	url = u"https://api-mobi.soundcloud.com/resolve?permalink_url=" + soundcloud_url + u"&client_id=" + client_id + "&format=json&app_version=" + app_version
	user_id = requests.get(url)
	user_id = json.loads(user_id.content)
	user_id = user_id["id"]
	return user_id

def get_user_tracks(user_id):
	offset = 0
	url = u"https://api-v2.soundcloud.com/users/" + unicode(user_id) + u"/tracks?representation=&client_id=" + client_id + "&limit=5000&offset=0&linked_partitioning=1&app_version=" + app_version
	playlist = requests.get(url)
	playlist = playlist.content
	playlist = json.loads(playlist)
	album = playlist["collection"][0]["user"]["username"]
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

	if playlist["next_href"] is not None:
		track_ids, permalink_url, track_name = get_user_tracks_recursion(playlist["next_href"], url, track_ids, permalink_url, track_name)

	return track_ids, permalink_url, track_name, album

def get_user_tracks_recursion(next_href, first_url, track_ids, permalink_url, track_name):
	link_to_next_part = next_href.split("offset=")
	link_to_next_part = link_to_next_part[1].split("&representation=")
	link_to_next_part = link_to_next_part[0]
	link_to_next_part = first_url.replace("offset=0", "offset=" + str(link_to_next_part))
	next_part = requests.get(link_to_next_part)
	next_part = next_part.content
	next_part = json.loads(next_part)

	for index in range(len(next_part["collection"])):
		track_ids.append(next_part["collection"][index]["id"])
		permalink_url.append(next_part["collection"][index]["permalink_url"])
		track_name.append(next_part["collection"][index]["title"])

	if next_part["next_href"]:
		get_user_tracks_recursion(next_part["next_href"], first_url, track_ids, permalink_url, track_name)

	else:
		return track_ids, permalink_url, track_name

def get_track_id(soundcloud_url):
	resolve_url = u"https://api.soundcloud.com/resolve.json?url="
	url = resolve_url + soundcloud_url + u"&client_id=" + client_id
	s = requests.get(resolve_url + soundcloud_url + u"&client_id=" + client_id)
	s = s.content
	trackid = json.loads(s)
	trackid = trackid["id"]
	return trackid

if __name__ == '__main__':
	main()
