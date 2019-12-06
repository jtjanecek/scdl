# scdl - a simple SoundCloud downloader
You run it, give it a track link or a playlist link and it gets downloaded. It's as simple as that.
Can also download 256kbps m4a files, not just 128kbps mp3 files! You do **NOT** need to own a premium account to use this tool.
## Usage
```
usage: scdl [-h] [-p] [-pl] [-m]

optional arguments:
  -h, --help       show this help message and exit
  -p, --premium    Use to download 256kbps M4A files
  -pl, --playlist  Download a playlist instead of a single track
  -m, --metadata   Write track metadata to a separate file
```

## Compatibility
This script has been tested on Ubuntu 19.10 and Windows 10 (1903).

## Requirements

* Python3.6
* ffmpeg
* pip3

## Installation
Linux:
```
sudo bash install.sh
scdl -p
```
Windows:
```
Install ffmpeg and add it to PATH
python -m pip install --user mutagen
python -m pip install --user requests
python scdl -p
```

## Disclaimer
If a track says “NOT AVAILABLE IN YOUR COUNTRY”, then this tool can’t download the track without a VPN/Proxy/whatever and I can’t change that. Use said tools to get around this.
