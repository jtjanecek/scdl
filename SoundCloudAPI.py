from bs4 import BeautifulSoup
import sys
import os
import urllib.request
import locale
import scdl
locale.setlocale(locale.LC_ALL, 'en_US')

class SoundCloudAPI():
	def __init__(self):
		self._soundcloud_url = "https://www.soundcloud.com"	
		self._search_url = "/search?q="

	def query(self, search_query: str, n_results=5):
		'''
		Return a list of 10 of the following:
		[song name, artist name, views(?), total length]
		'''
		search_query = search_query.strip()

		base_url = "https://soundcloud.com/search?q=" + search_query.lower().replace(" ","%20")

		# Get the html		
		print("*** Getting HTML: {}".format(base_url))
		html_raw = self._get_html(search_query)

		base_results = self._parse_search_query_html(html_raw, n_results)

		results = self._update_details(base_results)

		for result in results:
			result['Downloader'] = self
			result['DL'] = 'SoundCloud'

		return results

	def _get_html(self, search_query):
		self._soundcloud_url = "https://www.soundcloud.com"	
		self._search_url = "/search?q="

		base_url = self._soundcloud_url + self._search_url + search_query.lower().replace(" ","%20")

		
		#logger = urllib.request.HTTPSHandler(debuglevel=1)
		#opener = urllib.request.build_opener(logger)
		#urllib.request.install_opener(opener)
		f = urllib.request.urlopen(base_url)
		html_raw = f.read().decode('utf-8')

		return html_raw

	def _parse_search_query_html(self, html_raw, n_results):
		# Parse the HTML
		soup = BeautifulSoup(html_raw, 'html.parser')

		# Extract the  
		res = []
		all_links = soup.find_all('h2')
		for i, link in enumerate(all_links):
			sub_link = link.find_all('a')
			assert(len(sub_link)==1)		
			sub_link = sub_link[0]

			this_song = {}
			this_song['Link'] = self._soundcloud_url + sub_link.get('href')
			this_song['Name'] = sub_link.get_text()
			res.append(this_song)
			if i == n_results-1:
				break
		return res

	def _update_details(self, base_results: [dict]):
		# Now that we have the base info, we can query the deeper links, and get views

		for result in base_results:
			url = result['Link']
			print("*** Querying sub-results: {}".format(url))
			f = urllib.request.urlopen(url)
			print("*** Got HTML")
			html_raw = f.read().decode('utf-8')
			print("*** Decoding HTML")

			# Get the playback count
			try:
				playback_count_idx = html_raw.find("playback_count")	
				html_playback = html_raw[playback_count_idx:]
				end_idx = html_playback.find("}")
				html_playback = html_playback[0:end_idx]
				result['Plays/Views'] = int(html_playback.split(":")[1])
				result['Plays/Views'] = locale.format("%d", result['Plays/Views'], grouping=True)
			except: 
				result['Plays/Views'] = "n/a"

			# Get the duration from the html
			try:
				duration_idx = html_raw.rfind("duration")
				html_duration = html_raw[duration_idx:]
				html_duration = html_duration[:html_duration.find(",")]
				duration = int(html_duration.split(":")[1])
				duration_in_sec = duration / 1000
				minutes = int(duration_in_sec / 60)  
				seconds = int(duration_in_sec - (minutes*60))
				duration_str = "{:2}:{:02}".format(minutes,seconds)
				result['Duration'] = duration_str
			except:
				result['Duration'] = None
				continue

			# Get the artist
			artist_idx = html_raw.find("byArtist")
			artist_html = html_raw[artist_idx:].split('/div>')[0].strip()
			artist_html = artist_html.split('content="')[1]
			artist = artist_html.split('"')[0].strip()
			result['Artist'] = artist

		true_results = []
		for result in base_results:
			if result['Duration']:
				true_results.append(result)

		return true_results

	def _download_file(self, result, artist, name):   
                scdl.main(result['Link'].replace("www.",""), name, artist)	
