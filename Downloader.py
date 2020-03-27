import os, sys
from SoundCloudAPI import SoundCloudAPI
from YouTubeAPI import YouTubeAPI
from texttable import Texttable

class Downloader():
	def __init__(self):
		# Initialize APIs
		self._scAPI = SoundCloudAPI()
		self._ytAPI = YouTubeAPI()

	def _print_options(self, results):

		header = ["Idx", "Name", "Artist", "Duration", "Plays/Views", "DL"]
		table = Texttable()
		table.add_row(header)

		for i, result in enumerate(results):
			this_result = [result[key] for key in header]
			table.add_row(this_result)

		print(table.draw())

	def _get_input(self, prompt):
		input_text = input(prompt).strip()
		if input_text == 'q':
			print("Exiting...")
			sys.exit()
		return input_text


	def download(self, search_query: str):
		'''
		Display options from youtube and soundcloud, then
		download one of them based on user input

		params:
			search_query: string query from user
		'''
		
		print("*** Querying SoundCloud...")
		sc_results = self._scAPI.query(search_query)
		print("*** Querying YouTube...")
		yt_results = self._ytAPI.query(search_query)
		yt_results = []

		results = sc_results + yt_results 

		# Update indices of results
		for i, result in enumerate(results):
			result['Idx'] = i+1

		# If no results
		if len(results) == 0:
			print("No results found.")
			return

		# Print the options
		self._print_options(results)

		pick = int(self._get_input("Song pick: ")) - 1

		result_picked = results[pick]
		print("Selected Song: {}\nArtist: {}".format(result_picked['Name'], result_picked['Artist']))
		print("=================================")

		artist = self._get_input("Artist name: ")
		song   = self._get_input("Song name: ")

		cwd = os.getcwd()
		os.chdir("../Library/Downloads")
		result_picked['Downloader']._download_file(result_picked, artist, song)
		os.chdir(cwd)

		return
