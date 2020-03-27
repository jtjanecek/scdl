
from Downloader import Downloader

# Downloader app

def main():
	# Keep downloading songs
	
	downloader = Downloader()

	while True:
		input_text = input("Search terms: ")
		if input_text.strip() == 'q':
			print("Quitting...")
			break
		else:
			downloader.download(input_text)		
		

if __name__ == '__main__':
	main()
