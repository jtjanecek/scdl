#!/bin/bash

if [ "$EUID" -ne 0 ]
	then echo "This script needs to be run as root!"
	exit
fi

{
	which pip3
} &> /dev/null

if [ $? ==  1 ]; then
	echo "Pip3 is not installed. Please download and install it before proceeding."
	exit
fi

if ! python3 -c "import requests" &> /dev/null; then
	echo "The requests module is missing. Installing it now..."
    python3 -m pip install requests
fi

if ! python3 -c "import mutagen" &> /dev/null; then
	echo "The mutagen module is missing. Installing it now..."
    python3 -m pip install mutagen
fi

if ! python3 -c "import joblib" &> /dev/null; then
	echo "The joblib module is missing. Installing it now..."
    python3 -m pip install joblib
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

installerPath="${0%/*}"

cp "$installerPath"/scdl /usr/local/bin/scdl
chmod a+rx /usr/local/bin/scdl

echo "Installed!"
