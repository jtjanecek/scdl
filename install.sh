#!/bin/bash

if [ "$EUID" -ne 0 ]
	then echo "This script needs to be run as root!"
	exit
fi

{
	which pip
} &> /dev/null

if [ $? ==  1 ]; then
	echo "Pip is not installed. Downloading it now."
	curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
	python get-pip.py
fi

if ! python -c "import requests" &> /dev/null; then
	echo "The requests module is missing. Installing it now..."
    python -m pip install requests
fi

if ! python -c "import mutagen" &> /dev/null; then
	echo "The mutagen module is missing. Installing it now..."
    python -m pip install mutagen
fi

if [ -f /bin/scdl ]; then
	rm -rf /bin/scdl
fi

if [ -d /bin/scdl_files/ ]; then
	rm -rf /bin/scdl_files/
fi

if [ -d /usr/local/bin/scdl ]; then
	rm -rf /usr/local/bin/scdl
fi

cp scdl /usr/local/bin/scdl
chmod a+rx /usr/local/bin/scdl

echo "Installed!"
