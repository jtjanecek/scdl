# scdl - a simple SoundCloud downloader
You run it, give it a track link or a playlist link and it gets downloaded. It's as simple as that.
Can also download 256kbps m4a files, not just 128kbps mp3 files! You do **NOT** need to own a premium account to use this tool.
## Usage
```
usage: scdl [-h] [-p] [-pl]

optional arguments:
  -h, --help       show this help message and exit
  -p, --premium    Use to download 256kbps M4A files
  -pl, --playlist  Download a playlist instead of a single track
```

## Compatibility
I've only tested this on Linux, but if you can get ffmpeg as well as the various modules installed it should work just fine. Don't blame me though in case anything breaks.

Note:
```
Windows does not ship with a compatible version of curl (W10: 7.55.1 afaik) and needs to be updated (preferably to 7.66.0), because it does not support the --compressed parameter.
```
## Requirements

* Python 3
* ffmpeg
* pip3

## Installation
```
sudo bash install.sh
scdl
```

## Disclaimer
If a track says “NOT AVAILABLE IN YOUR COUNTRY”, then this tool can’t download the track without a VPN/Proxy/whatever and I can’t change that. Use said tools to get around this.
