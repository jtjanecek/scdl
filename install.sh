if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi
sudo mkdir /bin/scdl_files/
sudo cp ./scdl /bin
sudo chmod +x /bin/scdl
sudo chmod 775 /bin/scdl
sudo cp ./scdl.py /bin/scdl_files/
echo "Installed!"
