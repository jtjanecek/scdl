if [ "$EUID" -ne 0 ]
  then echo "Please run as root!"
  exit
fi

if [ -f /bin/scdl ]; then
	rm -rf /bin/scdl
	echo "Removed /bin/scdl"
fi

if [ -d /bin/scdl_files/ ]; then
	rm -rf /bin/scdl_files/
	echo "Removed /bin/scdl_files"
fi

cp scdl /usr/local/bin/scdl
chmod a+rx /usr/local/bin/scdl

echo "Installed!"
