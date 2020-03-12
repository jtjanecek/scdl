# scdl - a simple SoundCloud downloader
You run it, give it a track link or a playlist link and it gets downloaded. It's as simple as that.
Can also download 256kbps m4a files, not just 128kbps mp3 files! You do **NOT** need to own a premium account to use this tool.
## Usage
```
usage: scdl [-h] [-m] [-dd] [-r] [--update-linux] [--update-windows] [--debug]
            [-s SEGMENTSPARALLEL] [-f FFMPEGPATH] [--progressive]

optional arguments:
  -h, --help            show this help message and exit
  -m, --metadata        Write track metadata to a separate file
  -dd, --disable-description
                        Disable reading and writing of description ID3 tag /
                        JSON
  -r, --resume          Resume download of playlist
  --update-linux        Updates (and installs) scdl to the newest version
  --update-windows      Updates scdl to the newest version (within the current
                        folder)
  --debug               Show output for debugging
  -s SEGMENTSPARALLEL, --segments SEGMENTSPARALLEL
                        Set number of segments that will be downloaded in
                        parallel (default = 16)
  -f FFMPEGPATH, --ffmpeg-location FFMPEGPATH
                        Path to ffmpeg. Can be the containing directory or
                        ffmpeg executable itself
  --progressive         Download progressive audio files in one go instead of
                        segments
```
By default the higher quality 256kbps M4A file will be downloaded (whenever it's available), mp3 is only used as a fallback. If there is a free download available (enabled by the artist and accessible under the "More..." button), then both .m4a and .mp3 will be skipped.

In case you happen to have a slow or unstable internet connection, please adjust the amount of segments downloaded in parallel accordingly. urllib has trouble keeping up with failing connections, there's not much I can do beyond handling the exceptions and trying again (which doesn't always work).

## Examples

Downloading a single track (works for both public and private tracks):
```
x1c4@z8f6Px98Co76fb: ~ $ scdl
Please enter a URL: https://soundcloud.com/olswel/woomp-feat-inimicvs
```
Downloading a playlist:
```
x1c4@z8f6Px98Co76fb: ~ $ scdl
Please enter a URL: https://soundcloud.com/inimicvs/sets/mojave
```
Downloading all tracks of one user:
```
x1c4@z8f6Px98Co76fb: ~ $ scdl
Please enter a URL: https://soundcloud.com/kaytranada
```
Downloading all tracks liked by a user:
```
x1c4@z8f6Px98Co76fb: ~ $ scdl
Please enter a URL: https://soundcloud.com/kaytranada/likes
```

## Compatibility
This script has been tested on Ubuntu 19.10 and Windows 10 (1903). Mac should work too, but the installation procedure might vary (from Linux).

## Requirements

* Python 3.6 (or higher)
* python3-pip
* FFmpeg

## Installation
Linux:
```
sudo ./install.sh
scdl
```
Windows:
```
# Add FFmpeg to PATH
python -m pip install --user mutagen
python -m pip install --user requests
python -m pip install --user joblib
python scdl
```

## Disclaimer
If a track says “NOT AVAILABLE IN YOUR COUNTRY”, then this tool can’t download the track without a VPN/Proxy/whatever and I can’t change that. Use said tools to get around this.
