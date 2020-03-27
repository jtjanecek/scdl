
import subprocess
import os, sys
from texttable import Texttable
from glob import glob

root_dir = "/Users/tyler/Music/Library"

# This will return absolute paths
globber = "{}/**/*.m4a".format(root_dir)
file_list = [f for f in glob(globber, recursive=True) if os.path.isfile(f)]

# Print table
header = ["Idx", "Quality", "Name", "Path"]
table = Texttable()
table.add_row(header)

for i, result in enumerate(file_list):
	idx = i+1
	name = os.path.basename(result)	
	path = result

	# Run afinfo
	bashCommand = ['afinfo', path]
	process = subprocess.Popen(bashCommand, stdout=subprocess.PIPE)
	out, err = process.communicate()
	out = str(out)
	bit_idx = out.find("bit rate:")
	out = out[bit_idx:]
	bits = int(int(out.split("bits")[0].strip().split()[2]) / 1000)
	quality = str(bits) + " kbps" 

	this_song = [idx, quality, name, path]
	table.add_row(this_song)

print(table.draw())

