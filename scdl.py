#!/usr/bin/env python3

import os
import re
import gc
import ssl
import sys
import json
import time
import stat
import shutil
import urllib
import codecs
import mutagen
import zipfile
import argparse
import requests
import platform
import tempfile
import subprocess
from mutagen.mp3 import EasyMP3
from urllib.parse import unquote
from mutagen.easyid3 import EasyID3
from joblib import Parallel, delayed
from mutagen.mp4 import MP4, MP4Cover
from pathlib import Path, PureWindowsPath
from mutagen.id3 import ID3, APIC, TIT2, TALB, TPE1, TPE2, COMM, USLT, TCOM, TCON, TDRC

'''
We have to use the client_id of another app as Soundcloud is no longer
taking requests for new user applications and therefore doesn't allow
us to create a new one that is made specifically for this program.
Instead, we have no other choice (if we don't want to keep updating the app
constantly) other than to use the client_id youtube-dl has embedded in
its source code. Can't believe I didn't think of this sooner (which is why it
kept breaking so freaking often).
'''

clientId = "iZIs9mchVcX5lhVRyQGGAYlNPVldzAoX"
appVersion = "1575626913"
lastTrackIndexFilePath = "last_track_index.txt"
lastTrackIndex = 0
ssl._create_default_https_context = ssl._create_unverified_context
debugFlag = False
resumeDownloadFlag = False
premiumClientId = "GSTMg2qyKgq8Ou9wvJfkxb3jk1ONIzvy"
premiumFlag = True
metadataFlag = 0
descriptionDisableFlag = 0
segmentsParallel = 1

def log_debug(message):
    if debugFlag == True:
        print(message)

log_debug(f"clientId = {clientId}")
log_debug(f"premiumClientId = {premiumClientId}")
log_debug(f"appVersion = {appVersion}")

def main(soundcloudUrl, title, artist):
    parseStuff()

    if updateLinuxFlag == True:
        print("Updating for Linux!")
        try:
            updateLinux()
        except:
            print("An error occured while updating!")            
        return

    if updateWindowsFlag == True:
        print("Updating for Windows!")
        try:
            updateWindows()
        except:
            print("An error occured while updating!")
        return

    if debugFlag == True:
        print("Debugging output enabled!")

    linkType, soundcloudUrl = linkDetection(soundcloudUrl)
    print("Link type: {}".format(linkType))
    print("URL: {}".format(soundcloudUrl))
    print("Title: {}".format(title))
    print("Artist: {}".format(artist))

    if linkType == 1:
        downloadSingleTrack(soundcloudUrl, "", 1, 0, title, artist)

    if linkType == 2:
        downloadPlaylist(soundcloudUrl, 1)

    if linkType == 3:
        downloadUserTracks(soundcloudUrl)

    if linkType == 4:
        downloadUserLikes(soundcloudUrl)

    print("Done!")

def updateLinux():
    log_debug(">> updateLinux()")
    if platform.system() != "Linux":
        print("You're not running Linux!")
        return
    if os.geteuid() != 0:
        log_debug("euid = {}".format(os.geteuid()))
        print("This needs to be run as root!")
        return
    print("Getting latest version from Github...")
    response  = requests.get("https://github.com/mrwnwttk/scdl/archive/master.zip")
    log_debug("URL: https://github.com/mrwnwttk/scdl/archive/master.zip")
    log_debug("Redirected to: {}".format(response.url))
    log_debug("Status code: {}".format(response.status_code))
    urllib.request.urlretrieve(response.url, "scdl-latest.zip")
    with zipfile.ZipFile("scdl-latest.zip", "r") as zip:
        log_debug("Files inside ZIP:")
        log_debug("{}".format(zip.namelist()))
        for file in zip.infolist():
            file.filename = os.path.basename(file.filename)
            if file.filename == "scdl" or file.filename == "install.sh":
                    zip.extract(file, os.getcwd())
    log_debug("Removing scdl-latest.zip...")
    os.remove("scdl-latest.zip")
    log_debug("Executing install.sh...")
    os.system("./install.sh")
    log_debug("Removing scdl file from current directory...")
    os.remove("scdl")
    log_debug("Removing install.sh file from current directory...")
    os.remove("install.sh")
    print("Updated!")

def updateWindows():
    print("Getting latest version from Github...")
    response = requests.get("https://github.com/mrwnwttk/scdl/archive/master.zip")
    urllib.request.urlretrieve(response.url, "scdl-latest.zip")
    print("Cleaning up directory...")
    files_to_delete = [
    'install.sh',
    '.gitignore',
    'scdl',
    'README.md',
    'bin/curl.exe'
    ]

    for file in files_to_delete:
        try:
            os.remove(file)
        except:
            pass
    shutil.rmtree("bin")

    try:
        shutil.move(".git", "git")
    except:
        pass
    try:
        shutil.rmtree('git', ignore_errors=True)
    except:
        pass

    with zipfile.ZipFile("scdl-latest.zip", "r") as zip:
        for file in zip.infolist():
            if file.filename[-1] == '/' or file.filename[0] == '.':
                continue
            file.filename = os.path.basename(file.filename)
            if file.filename == "scdl":
                zip.extract(file, os.getcwd())
            if file.filename == "README.md":
                zip.extract(file, os.getcwd())

    os.remove("scdl-latest.zip")
    try:
        shutil.rmtree("git", onerror=removeReadonly)
    except:
        pass

    os.system("python -m pip install --upgrade --user requests")
    os.system("python -m pip install --upgrade --user mutagen")
    os.system("python -m pip install --upgrade --user joblib")

    print("Updated!")

def removeReadonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def downloadEmbeddedFreeDownload(trackId):
    log_debug("downloadEmbeddedFreeDownload(trackId = {})".format(trackId))
    while True:
        try:
            r = requests.get("https://api-v2.soundcloud.com/tracks?ids={}&client_id={}&%5Bobject%20Object%5D=&app_version={}&app_locale=de".format(str(trackId), premiumClientId, appVersion),
                headers={
                "Sec-Fetch-Mode":"cors",
                "Origin": "https://soundcloud.com",
                "Authorization": "OAuth 2-290697-69920468-HvgOO5GJcVtYD39",
                "Content-Type": "application/json",
                "Accept": "application/json, text/javascript, */*; q=0.1",
                "Referer": "https://soundcloud.com/",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
                "DNT": "1",
                })
        except Exception as e:
            print(e)
        log_debug("URL: {}".format(r.url))
        log_debug("Status Code: {}".format(r.status_code))
        log_debug("Response: {}".format(r.text))
        if r.status_code == 200:
            break
        else:
            log_debug("Error: did not get Status code 200 (OK)... Trying again...")
            time.sleep(2)
    data = json.loads(r.text)

    if data[0]['downloadable'] == True:
        print("This track has the free download enabled!")
        if data[0]['has_downloads_left'] == False:
            print("The download has a restricted number of downloads, not available anymore :(")
            raise Exception("No free download available!")
        if data[0]['has_downloads_left'] == True:
            url = f"https://api-v2.soundcloud.com/tracks/{trackId}/download?client_id={clientId}&app_version={appVersion}&app_locale=de"
            while True:
                try:
                    r = requests.get(url)
                    log_debug("URL: {}".format(r.url))
                    log_debug("Status code: {}".format(r.status_code))
                    log_debug("Content: {}".format(r.content))
                    x = json.loads(r.content)
                    r = requests.head(x['redirectUri'],
                        headers={
                        "Sec-Fetch-Mode":"cors",
                        "Origin": "https://soundcloud.com",
                        "Authorization": "OAuth 2-290697-69920468-HvgOO5GJcVtYD39",
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/javascript, */*; q=0.1",
                        "Referer": "https://soundcloud.com/",
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
                        "DNT": "1",
                        })
                    try:
                        filename = r.headers['x-amz-meta-original-filename']
                    except:
                        try:
                            filename = re.findall("filename=\"(.+)\"", r.headers['content-disposition'])[0]
                            filename = unquote(filename)
                        except:
                            try:
                                filename = repairFilename(data[0]['title']) + "." + (filename.split('.'))[-1]
                            except:
                                log_debug("File has no extension, adding .unknown to the end of the file...")
                                filename = repairFilename(data[0]['title']) + ".unknown"
                    print("Filename: {}".format(filename))
                    try:
                        urllib.request.urlretrieve(x['redirectUri'], repairFilename(filename))
                        break
                    except:
                        log_debug("An error occured while downloading the file, trying again...")

                except Exception as e:
                    print(e)
                    time.sleep(2)
    else:
        raise Exception("No free download available!")

def linkDetection(soundcloudUrl):
    '''
    detects the type of link, as a fallback for a lack of playlist flag
    return 1 = single track
    return 2 = playlist
    '''

    # Fix a missing https://
    soundcloudUrl = soundcloudUrl.replace("http://", "https://")

    if not "https://" in soundcloudUrl:
        soundcloudUrl = "https://" + soundcloudUrl

    # Fix URL if it is a single track out of a playlist
    if '?in=' in soundcloudUrl:
        soundcloudUrl = soundcloudUrl.split('?in=')
        soundcloudUrl = soundcloudUrl[0]

    # Remove slash at the end to avoid errors while resolving URL
    if soundcloudUrl[-1] == '/':
        soundcloudUrl = soundcloudUrl[:-1]

    # URL is a playlist
    if '/sets' in soundcloudUrl:
        return 2, soundcloudUrl

    # URL for tracks of a user
    userReTracks1 = re.compile(r"^https:\/\/soundcloud.com\/[a-z\-_0-9]{1,}[\/]*$")
    if (userReTracks1.match(soundcloudUrl)):
        return 3, soundcloudUrl

    userReTracks2 = re.compile(r"^https:\/\/soundcloud.com\/[a-z\-_0-9]{1,}\/tracks[\/]*$")
    if (userReTracks1.match(soundcloudUrl)) or (userReTracks2.match(soundcloudUrl)):
        return 3, soundcloudUrl

    # URL for likes of a user
    userReLikes = re.compile(r"^https:\/\/soundcloud.com\/[a-z\-_0-9]{1,}\/likes$")
    if (userReLikes.match(soundcloudUrl)):
        return 4, soundcloudUrl

    # This is a single track
    else:
        return 1, soundcloudUrl

def downloadSingleTrack(soundcloudUrl, trackTitle, hqFlag, optionalAlbum, titleInput, artistInput):
    '''
    If you're downloading a playlist a string containing the playlist
    name will be passed to the function as optionalAlbum, otherwise 
    it is 0 and gets replaced by simple string
    '''
    if resumeDownloadFlag == True:
        alreadyDownloaded = False
    
    if optionalAlbum != 0:
        album = optionalAlbum
    else:
        album = "SoundCloud"

    '''
    m4a premium download, only happens when both flags are set
    '''
    log_debug("Getting Track ID for {}".format(soundcloudUrl))
    trackId = getTrackId(soundcloudUrl)
    if trackId == 0:
        print("Cannot download this track, skipping it!")
        return
    try:
        downloadEmbeddedFreeDownload(trackId)
        return
    except:
        log_debug("No free download available!")

    if premiumFlag == 1 and hqFlag == 1:
        size = 0
        m4aFailedFlag = 0
        if resumeDownloadFlag == True:
            if not os.path.exists(str(trackTitle) + '.m4a') and not os.path.exists(str(repairFilename(trackTitle)) + '.m4a'):
                try:
                    ret = downloadPremium(trackId)
                    if ret == -1:
                        return None
                    '''
                    A failed m4a download results in an empty file
                    due to the lack of audio streams, so we can just
                    check for the filesize to see if the download was
                    successful or not :)
                    '''
                    size = os.path.getsize(str(trackId) + ".m4a")
                    if size != 0:
                        '''
                        Set flag in case the download failed
                        '''
                        m4aFailedFlag = 0
                    else:
                        m4aFailedFlag = 1
                except:
                
                    '''
                    The track is either not publicly available or not
                    available as M4A.
                    '''
                    try:
                        downloadPremiumPrivate(trackId, soundcloudUrl)
                    except:
                        m4aFailedFlag = 1
                        try:
                            size = os.path.getsize(str(trackId) + ".m4a")
                        except:
                            size = 0
                            if size != 0:
                                '''
                                Set flag in case the download failed
                                '''
                                m4aFailedFlag = 0
                            else:
                                m4aFailedFlag = 1
            else:
                size = 1
                alreadyDownloaded = True
                print(str(repairFilename(trackTitle)) + " Already Exists")              
        else:
            try:
                ret = downloadPremium(trackId)
                if ret == -1:
                    return None
                '''
                A failed m4a download results in an empty file
                due to the lack of audio streams, so we can just
                check for the filesize to see if the download was
                successful or not :)
                '''
                size = os.path.getsize(str(trackId) + ".m4a")
                if size != 0:
                    '''
                    Set flag in case the download failed
                    '''
                    m4aFailedFlag = 0
                else:
                    m4aFailedFlag = 1
            except:
            
                '''
                The track is either not publicly available or not
                available as M4A.
                '''
                try:
                    downloadPremiumPrivate(trackId, soundcloudUrl)
                except:
                    m4aFailedFlag = 1
                    try:
                        size = os.path.getsize(str(trackId) + ".m4a")
                    except:
                        size = 0
                        if size != 0:
                            '''
                            Set flag in case the download failed
                            '''
                            m4aFailedFlag = 0
                        else:
                            m4aFailedFlag = 1

    '''
    The tagging procedure is similar for both file types, only
    the way the tags are applied is different.
    '''
    if resumeDownloadFlag == False:
        alreadyDownloaded = False
    if not alreadyDownloaded:           
        trackName, artist, coverFlag = getTags(soundcloudUrl)
        #if descriptionDisableFlag == 0:
        #    description = getDescription(soundcloudUrl)
        #else:
        #    description = ""
        description = ""
        '''
        #File gets renamed differently depending on whether or not it's
        #an m4a or mp3, obviously
        '''
        
        if m4aFailedFlag == 1 or hqFlag == 0:
            finishedDownloadFilename = renameFile(trackId, "{} - {}".format(artistInput, titleInput), 0)
        else:
            finishedDownloadFilename = renameFile(trackId, "{} - {}".format(artistInput, titleInput), 1)
     
        if premiumFlag ==  1 and hqFlag == 1 and m4aFailedFlag == 0:
            '''
            m4a
            '''
            addTags(finishedDownloadFilename, titleInput, artistInput, album, coverFlag, description, 1)
        else:
            '''
            mp3
            '''
            addTags(finishedDownloadFilename, titleInput, artistInput, album, coverFlag, description, 0)

    cleanUp(trackId, repairFilename(trackTitle))

def repairFilename(trackName):
    '''
    Filenames are problematic, Windows, Linux and macOS don't
    allow certain characters. This (mess) fixes that. Basically 
    every other character, no matter how obscure, is seemingly
    supported though.
    '''

    if u"/" in trackName:
        trackName = trackName.replace(u"/", u"-")
    if u"\\" in trackName:
        trackName = trackName.replace(u"\\", u"-")
    if u"|" in trackName:
        trackName = trackName.replace(u"|", u"-")
    if u":" in trackName:
        trackName = trackName.replace(u":", u"-")
    if u"?" in trackName:
        trackName = trackName.replace(u"?", u"-")
    if u"<" in trackName:
        trackName = trackName.replace(u"<", u"-")
    if u">" in trackName:
        trackName = trackName.replace(u">", u"-")
    if u'"' in trackName:
        trackName = trackName.replace(u'"', u"-")
    if u"*" in trackName:
        trackName = trackName.replace(u"*", u"-")
    if u"..." in trackName:
        trackName = trackName.replace(u"...", u"---")

    return trackName

def renameFile(trackId, trackName, premiumFlag):
    '''
    Using the trackId as the filename saves me lots
    of trouble compared to having to deal with the
    (sometimes) problematic titles as filenames.
    That way it's easier to just rename them afterwards.
    '''

    log_debug(">> renameFilename()")

    trackName = repairFilename(trackName)
    #We're dealing with a .m4a file here
    if premiumFlag == 1:  
        fileExtension = ".m4a"  
        oldFilename = str(trackId) + fileExtension
        newFilename = str(trackName) + fileExtension
    #We're dealing with a .mp3 file here
    if premiumFlag == 0:
        fileExtension = ".mp3"
        oldFilename = str(trackId) + fileExtension
        newFilename = str(trackName) + fileExtension
        
    newFixedFilename = ""
    if not os.path.exists(newFilename):
        os.rename(oldFilename, newFilename)
    else:
        ii = 1
        while True:
            newFixedFilename = str(trackName) + "_" + str(ii) + fileExtension
            if not os.path.exists(newFixedFilename):
                print("File with same filename exists, renaming current file to {}".format(newFixedFilename))
                os.rename(oldFilename, newFixedFilename)
                break
            ii += 1
    if newFixedFilename != "":
        newFilename = newFixedFilename
    return newFilename

def cleanUp(trackId, trackName):
    '''
    Removes all the leftover files, both the ones from the successful
    as well as the failed downloads which are basically just empty files
    '''
    if os.path.isfile("cover.jpg") == True:
        os.remove("cover.jpg")
    if os.path.isfile(str(trackId) + ".txt") == True:
        os.remove(str(trackId) + ".txt")
    if os.path.isfile(str(trackId) + ".m3u8") == True:
        os.remove(str(trackId) + ".m3u8")
    if os.path.isfile(str(trackId) + ".m4a") == True:
        os.remove(str(trackId) + ".m4a")
    if os.path.isfile(str(trackId) + ".mp3") == True:
        os.remove(str(trackId) + ".mp3")        

def changeDirectory(folderName):
    '''
    makes directory with the name of the album passed to it, creates it if needed
    '''
    folderName = repairFilename(folderName)
    if "/" in folderName:
        folderName.replace("/","-")
    if not os.path.exists(folderName):
        os.mkdir(folderName)
        os.chdir(folderName)
    else:
        os.chdir(folderName)

def getTrackId(soundcloudUrl):
    '''
    Self-explanatory.
    '''
    log_debug(">> getTrackId(soundcloudUrl = {})".format(soundcloudUrl))
    while True:
        try:
            s = requests.get("https://api-mobi.soundcloud.com/resolve?permalink_url={}&client_id={}&format=json&app_version={}".format(soundcloudUrl, clientId, appVersion))
            log_debug(s.status_code)
            if(s.status_code == 404):
                log_debug("Resolving URL returned 404 Not Found, skipping this track!")
                return 0
            if(s.status_code == 403):
                log_debug("Track not available! (Country?)")
                return 0
            log_debug(s.content)
            s = s.content
            trackId = json.loads(s)
            if trackId["duration"] == 0:
                print("Duration = 0")
                return 0
            trackId = trackId["id"]
            log_debug("Track ID: {}".format(trackId))
            return trackId
        except:
            time.sleep(2)
            continue
        break

def downloadPremium(trackId):
    '''
    saves the json file containing a link to the hls stream which
    contains the audio we want. I have no clue for how long this
    hacky solution will continue to work. Probably until I cancel
    my SoundCloud Go Plus subscription (or rather trial)
    '''
    log_debug(">> downloadPremium()")
    while True:
        try:
            r = requests.get("https://api-v2.soundcloud.com/tracks?ids={}&client_id={}&%5Bobject%20Object%5D=&app_version={}&app_locale=de".format(str(trackId), premiumClientId, appVersion),
                headers={
                "Sec-Fetch-Mode":"cors",
                "Origin": "https://soundcloud.com",
                "Authorization": "OAuth 2-290697-69920468-HvgOO5GJcVtYD39",
                "Content-Type": "application/json",
                "Accept": "application/json, text/javascript, */*; q=0.1",
                "Referer": "https://soundcloud.com/",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
                "DNT": "1",
                })
        except Exception as e:
            print(e)
        log_debug("Status Code: {}".format(r.status_code))
        log_debug("Response: {}".format(r.text))
        if r.status_code == 200:
            break
        else:
            time.sleep(2)
    data = json.loads(r.text)
    transcoding_index = 0
    if progressiveFlag == True:
        transcoding_index = 1
    if(data[0]['media']['transcodings'] == []):
        print("No audio streams available!")
        return -1
    url = data[0]['media']['transcodings'][transcoding_index]['url']

    '''
    In the words of Dillon Francis' alter ego DJ Hanzel: "van deeper"
    That link to the hls stream leads to yet another link, which
    contains yet another link, which contains...
    '''
    while True:
        try:   
            r = requests.get(url,
                headers={
                    "Sec-Fetch-Mode": "cors",
                    "Referer": "https://soundcloud.com/",
                    "Origin": "https://soundcloud.com",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
                    "Authorization": "OAuth 2-290697-69920468-HvgOO5GJcVtYD39",
                    "DNT": "1",
                })
        except Exception as e:
            print(e)
        log_debug("URL: {}".format(url))
        log_debug("Status Code: {}".format(r.status_code))
        log_debug("Response: {}".format(r.text))
        if r.status_code == 200:
            break
        if r.status_code == 500:
            log_debug("Got 500 Server-side error, trying next m3u8 playlist...")
            transcoding_index += 1
            url = data[0]['media'][transcoding_index]['url']
        else:
            time.sleep(2)

    data = json.loads(r.text)
    url = data['url']
    log_debug(f"URL: {url}")

    if transcoding_index == 1 or transcoding_index == 3:
        log_debug("Attempting to download progressive version...")
        urllib.request.urlretrieve(url, "{}.m4a".format(trackId))
        return 0

    '''
    Yet another really hacky solution, gets the .m3u8 file using curl,
    it basically only replicates excactly what a browser would do (go
    look at the network tab in the explore tool and see for yourself)
    '''

    while True:
        try:
            r = requests.get(url,
                headers={
                "Sec-Fetch-Mode": "cors",
                "Referer": "https://soundcloud.com",
                "Origin": "https://soundcloud.com",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
                "Authorization": "OAuth 2-290697-69920468-HvgOO5GJcVtYD39",
                "DNT": "1"
                })
        except Exception as e:
            print(e)
        log_debug("Status Code: {}".format(r.status_code))
        if r.status_code == 200:
            break
        else:
            time.sleep(2)

    downloadM3U8(trackId, r.text)
    return 0

def downloadSegment(segment_urls, i, trackId, correctDirectory):
    '''
    This function randomly changes directories without telling it to,
    please don't ask me why. This fixes that.
    '''
    if (os.getcwd() != correctDirectory):
        os.chdir(correctDirectory)

    if platform.system() == 'Linux':
        print("\033[K\r", "Segment: [{} / {}]".format(i + 1, len(segment_urls)), "\r", end='')

    if platform.system() == 'Windows':
        print("\r Segment: [{} / {}]".format(i + 1, len(segment_urls)), "\r", end='')
    while True:
        try:
            urllib.request.urlretrieve(segment_urls[i], "{}-{}.m4a".format(trackId, i))
            break
        except:
            print("An error occured while downloading segment {}! Trying again...".format(i + 1), "\nCheck your connection or try running scdl with fewer segments in parallel (see --help)")
            if os.path.exists("{}-{}.m4a".format(trackId, i)):
                log_debug("Deleting failed file: {}-{}.m4a".format(trackId, i))
                os.remove("{}-{}.m4a".format(trackId, i))
            time.sleep(2)

def downloadM3U8(trackId, m3u8_file):
    segment_urls = []
    regex = re.compile('^.*https.*$')

    for line in m3u8_file.splitlines():
        if regex.search(line):
            line = line.replace('#EXT-X-MAP:URI=','')
            line = line.replace('"', '')
            line = line.replace('\n', '')
            segment_urls.append(line)

    log_debug("Segments: {}".format(segment_urls))

    Parallel(n_jobs=int(segmentsParallel))(delayed(downloadSegment)(segment_urls, i, trackId, os.getcwd()) for i in range(len(segment_urls)))

    print("\033[K\r", "                                   ", "\r", end='')

    segment_filenames = []
    for i in range(len(segment_urls)):
        segment_filenames.append("{}-{}.m4a".format(trackId, i))

    with open(str(trackId) + '.m4a', 'ab') as outfile:
        for file in segment_filenames:
            with open(file, "rb") as file2:
                outfile.write(file2.read())

    for file in segment_filenames:
        os.remove(file)

def downloadPremiumPrivate(trackId, soundcloudUrl):
    log_debug("downloadPremiumPrivate()")
    secretToken = soundcloudUrl.split("/")[5]
    log_debug(f"secretToken: {secretToken}")
    log_debug(f"trackId: {trackId}")

    while True:
        try:
            r = requests.get("https://api-mobi.soundcloud.com/tracks/soundcloud:tracks:{}?secret_token={}&client_id={}&&app_version={}&app_locale=de".format(trackId, secretToken, clientId, appVersion),
                headers={
                "Connection": "keep-alive",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Authorization": "OAuth 2-290697-69920468-HvgOO5GJcVtYD39",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36",
                "DNT": "1",
                "Sec-Fetch-Site": "same-site",
                "Sec-Fetch-Mode": "cors",
                "Referer": "https://soundcloud.com/",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
                })
        except Exception as e:
            print(e)
        log_debug("Status Code: {}".format(r.status_code))
        log_debug("Response: {}".format(r.content))
        if r.status_code == 200:
            break
        else:
            time.sleep(2)

    data = json.loads(r.text)
    log_debug("Loaded JSON data...")
    transcoding_index = 0
    if progressiveFlag == True:
        transcoding_index = 1
    url = data['media']['transcodings'][transcoding_index]['url']

    '''
    In the words of Dillon Francis' alter ego DJ Hanzel: "van deeper"
    That link to the hls stream leads to yet another link, which
    contains yet another link, which contains...
    '''
    while True:
        try:   
            r = requests.get(url,
                headers={
                    "Sec-Fetch-Mode": "cors",
                    "Referer": "https://soundcloud.com/",
                    "Origin": "https://soundcloud.com",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
                    "Authorization": "OAuth 2-290697-69920468-HvgOO5GJcVtYD39",
                    "DNT": "1",
                })
        except Exception as e:
            print(e)
        log_debug("URL: {}".format(url))
        log_debug("Status Code: {}".format(r.status_code))
        log_debug("Response: {}".format(r.text))
        if r.status_code == 200:
            break
        if r.status_code == 500:
            log_debug("Got 500 Server-side error, trying next m3u8 playlist...")
            transcoding_index += 1
            url = data[0]['media'][transcoding_index]['url']
        else:
            time.sleep(2)

    data = json.loads(r.text)
    url = data['url']
    log_debug(f"URL: {url}")

    if transcoding_index == 1 or transcoding_index == 3:
        log_debug("Attempting to download progressive version...")
        urllib.request.urlretrieve(url, "{}.m4a".format(trackId))
        return

    '''
    Yet another really hacky solution, gets the .m3u8 file using curl,
    it basically only replicates excactly what a browser would do (go
    look at the network tab in the explore tool and see for yourself)
    '''
    while True:
        try:
            r = requests.get(url,
                headers={
                "Sec-Fetch-Mode": "cors",
                "Referer": "https://soundcloud.com",
                "Origin": "https://soundcloud.com",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
                "Authorization": "OAuth 2-290697-69920468-HvgOO5GJcVtYD39",
                "DNT": "1"
                })
        except Exception as e:
            print(e)
        log_debug("Status Code: {}".format(r.status_code))
        if r.status_code == 200:
            break
        else:
            time.sleep(2)


    downloadM3U8(trackId, r.text)

def getTags(soundcloudUrl):
    '''
    Get the big json file containing basically all the metadata using the API
    '''
    log_debug(f"getTags(soundcloudUrl = {soundcloudUrl})")
    while True:
        try:
            a = requests.get("https://api-mobi.soundcloud.com/resolve?permalink_url={}&client_id={}&format=json&app_version={}".format(soundcloudUrl, clientId, appVersion))
            log_debug(f"URL: {a.url}")
            log_debug(f"Status code: {a.status_code}")
            a = a.content
            tags = json.loads(a)
            trackName = tags["title"]
        except:
            time.sleep(2)
            continue
        break

    log_debug("Got tags!")

    if(metadataFlag == 1):
        metadataFilename = repairFilename(trackName) + "_" + str(tags["id"]) + "_metadata.json"
        print("Writing metadata to file: ", metadataFilename)
        try:
            with open(metadataFilename, 'w') as json_file:
                json.dump(tags, json_file, sort_keys=True, indent=4)
        except:
            print("An error occured while writing the metadata to a file!")

    try:
        print("trackName: {}".format(trackName))
    except :
        raise
    
    artist = tags["user"]["username"]

    print("Artist: {}".format(artist))

    '''
    the json file doesn't reveal the biggest available cover art, 
    but we can fix that ourselves!
    '''
    cover = tags["artwork_url"]
    if cover != None:
        log_debug("Cover URL (large) for track present!")
        coverFlag = 1
        cover = cover.replace("large", "t500x500")
        try:
            urllib.request.urlretrieve(cover, "cover.jpg")
            log_debug("Cover URL (500x500) for track present!")
        except:
            try:
                coverFlag = 1
                cover = tags["user"]["avatar_url"]
                cover = cover.replace("large", "t500x500")
                urllib.request.urlretrieve(cover, "cover.jpg")
                log_debug("Got 500x500 cover from track!")
            except urllib.error.HTTPError:
                log_debug("An error occured while attempting to download the cover from the track! (Can be the case for ancient tracks)")
                coverFlag = 0
    else:
        '''
        some tracks don't have any kind of cover art, the
        avatar of the user is shown instead. We can implement that
        here. Once again the full size picture is not in the json file...
        '''
        log_debug("Attempting to get cover art from artist profile picture...")
        try:
            coverFlag = 1
            cover = tags["user"]["avatar_url"]
            cover = cover.replace("large", "t500x500")
            urllib.request.urlretrieve(cover, "cover.jpg")
            log_debug("Got cover art from artist!")
        except urllib.error.HTTPError:
            log_debug("Error while getting cover from artist profile picture")
            coverFlag = 0

    return trackName, artist, coverFlag

def getDescription(soundcloudUrl):
    '''
    gets the description separately
    '''
    log_debug(f">> getDescription(soundcloudUrl = {soundcloudUrl})")
    a = requests.get("https://api.soundcloud.com/resolve.json?url=" + soundcloudUrl + "&client_id=" + clientId)
    log_debug(f"URL: {a.url}")
    log_debug(f"Status code: {a.status_code}")
    a = a.text
    try:
        tags = json.loads(a)
        description = tags["description"]
        log_debug("Got description!")
    except:
        description = ""
    return description

def addTags(filename, trackName, artist, album, coverFlag, description, m4aFlag):
    '''
    Adds tags to the M4A file. 
    All of these are supported by iTunes and should
    therefore not cause much trouble with other media
    players. If you're downloading a playlist, then the
    album name will be the name of the playlist instead of
    "SoundCloud"
    '''
    log_debug(f"addTags(filename = {filename}, trackName = {trackName}, artist = {artist}, album = {album}, coverFlag = {coverFlag}, m4aFlag = {m4aFlag})")
    with open("{}".format(filename), "rb") as f:
        f.seek(0)
        first_few_bytes = f.read(24)
    if first_few_bytes == b'\x00\x00\x00\x18ftypiso5\x00\x00\x02\x00iso6mp41':
        if debugFlag == True:
            os.system("ffmpeg -y -i \"{}\" -c copy \"new_{}\"".format(filename, filename))
        else:
            os.system("ffmpeg -y -loglevel panic -i \"{}\" -c copy \"new_{}\"".format(filename, filename))
        os.remove("{}".format(filename))
        os.rename("new_{}".format(filename), "{}".format(filename))

    if m4aFlag == 1:
        log_debug("Tagging .m4a...")
        try:
            tags = MP4(filename).tags
            if description != None:
                tags["desc"] = description
            tags["\xa9nam"] = trackName
            if album != 0:
                tags["\xa9alb"] = album
            else:
                tags["\xa9alb"] = "SoundCloud"
            tags["\xa9ART"] = artist

            with open("cover.jpg", "rb") as f:
                tags["covr"] = [
                    MP4Cover(f.read(), imageformat=MP4Cover.FORMAT_JPEG)
                ]
            tags.save(filename)
        except Exception as e:
            log_debug("Nevermind...")
            os.rename(filename, filename[:-4] + ".mp3")
            filename = filename[:-4] + ".mp3"
            m4aFlag = 0

    if m4aFlag == 0:
        log_debug("Tagging .mp3...")
        try:
            audio = EasyMP3(filename)
        except:
            print("Something went wrong while tagging the file!")
            print("Neither M4A or MP3 worked, so I can only assume that the file is corrupt in some way")
            print("Please check the file using MediaInfo, VLC, mpv, spek and/or Mp3tag for erros.")
            print("There's nothing I can do about this :(")
            return
        audio['title'] = trackName
        audio['artist'] = artist

        if album != 0:
            audio['album'] = album
        else:
            audio['album'] = u"SoundCloud"
        audio.save(v2_version=3)

        if coverFlag != 0:
            audio = ID3(filename)
            if description != None:
                audio.add(
                USLT(
                    encoding=3,
                    lang=u'eng',
                    desc=u'desc',
                    text=description
                    )
                )
            with open('cover.jpg', 'rb') as albumart:     
                audio.add(
                APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=albumart.read()
                    )
                )
            audio.save(v2_version=3)

def downloadPlaylist(soundcloudUrl, hqFlag):
    log_debug(f">> downloadPlaylist(soundcloudUrl = {soundcloudUrl}, hqFlag = {hqFlag})")
    try:
        secretToken = soundcloudUrl.split("/")[6]
    except:
        secretToken = "0"
    log_debug("Secret token: {}".format(secretToken))
    playlistId = getPlaylistId(soundcloudUrl)
    print("Playlist ID: {}".format(playlistId))
    permalinkUrl, album = getPlaylistTracks(playlistId, secretToken)
    if descriptionDisableFlag == 0:
        description = getPlaylistDescriptions(playlistId, secretToken)
    else:
        description = ""

    changeDirectory(album)
    
    if not os.path.exists(lastTrackIndexFilePath):
        lastTrackIndexFile = open(lastTrackIndexFilePath, 'w+')
        lastTrackIndex = 0
        lastTrackIndexFile.write(str(lastTrackIndex))
    else:
        lastTrackIndexFile = open(lastTrackIndexFilePath, 'r')
        lastTrackIndex = int(lastTrackIndexFile.read())
    
    for index in range(lastTrackIndex, len(permalinkUrl)):
        downloadSingleTrack(permalinkUrl[index], "", 1, album)
        lastTrackIndexFile = open(lastTrackIndexFilePath, 'w')
        lastTrackIndexFile.write(str(index))
        lastTrackIndexFile.close()
    log_debug("Download of playlist finished, deleting last_track_index.txt ...")
    os.remove("last_track_index.txt")

def getPlaylistId(soundcloudUrl):
    '''
    The name says it all, that's really all there is to it.
    '''
    log_debug(f">> getPlaylistId(soundcloudUrl = {soundcloudUrl})")
    playlistIdRequest = requests.get("https://api-mobi.soundcloud.com/resolve?permalink_url={}&client_id={}&format=json&app_version={}".format(soundcloudUrl, clientId, appVersion))
    log_debug("Status code: {}".format(playlistIdRequest.status_code))
    playlistIdRequest = json.loads(playlistIdRequest.content)
    log_debug("Content: {}".format(playlistIdRequest))
    return playlistIdRequest["id"]

def getPlaylistTracks(playlistId, secretToken):
    '''
    Gets the links to all the tracks in a playlist together with their
    names as well as their IDs, all of which are necessary to download
    the track seamlessly.
    '''
    log_debug(f">> getPlaylistTracks(playlistId = {playlistId}, secretToken = {secretToken})")
    if secretToken != "0":
        playlistUrls = requests.get("http://api-v2.soundcloud.com/playlists/{}?client_id={}&secret_token={}".format(playlistId, clientId, secretToken))
    else:
        playlistUrls = requests.get("http://api-v2.soundcloud.com/playlists/{}?client_id={}".format(playlistId, clientId))

    log_debug(f"Playlist URL: {playlistUrls.url}")
    log_debug(f"Status code: {playlistUrls.status_code}")
    permalinkUrls = json.loads(playlistUrls.content)
    album = permalinkUrls["title"]
    print(f"Album: {album}")
    trackId = []
    trackCount = int(permalinkUrls["track_count"])
    log_debug(f"trackCount = {trackCount}")
    missingTracks = 0

    for i in range(trackCount):
        try:
            trackId.append(permalinkUrls["tracks"][i]["id"])
        except:
            missingTracks += 1
    if(missingTracks > 0):
        print("Sorry, can only download {} out of {} tracks of this playlist.".format(trackCount - missingTracks, trackCount))

    log_debug("{}".format(trackId))
    log_debug("Number of tracks with track IDs: {}".format(len(trackId)))
    log_debug("Crafting fancy URL...")

    fancyPlaylistUrl = "https://api-mobi.soundcloud.com/tracks?client_id={}&format=json&app_version={}&ids=".format(clientId, appVersion)
    for i in trackId:
        fancyPlaylistUrl = "{}{}{}".format(fancyPlaylistUrl, i, "%2C")
    fancyPlaylistUrl = fancyPlaylistUrl[:-3]
    fancyPlaylistUrl = "{}&playlistId={}&playlistSecretToken=".format(fancyPlaylistUrl, playlistId)
    if secretToken != "0":
        fancyPlaylistUrl = "{}{}".format(fancyPlaylistUrl, secretToken)
    else:
        fancyPlaylistUrl = "{}{}".format(fancyPlaylistUrl, "null")
    log_debug("New crafted URL = {}".format(fancyPlaylistUrl))

    pl = requests.get(fancyPlaylistUrl)
    log_debug(pl.status_code)
    playlist_json = json.loads(pl.content)
    permalink_url_list = []

    for i in range(len(playlist_json)):
        permalink_url_list.append(playlist_json[i]['permalink_url'])
        log_debug(playlist_json[i]['permalink_url'])
    return permalink_url_list, album

def getPlaylistDescriptions(playlistId, secretToken):
    '''
    Get individual descriptions for all the track in a playlist.
    I have yet to figure out why the getTags function refuses
    to pass the description string as an argument but this 
    seprate function works just fine for the time being. Sure,
    it's not efficient but one more API request on top of countless
    other ones won't hurt.
    '''
    log_debug(f">> getPlaylistDescriptions(playlistId = {playlistId})")
    if secretToken != "0":
        playlistUrls = requests.get("http://api.soundcloud.com/playlists/{}?client_id={}&secret_token={}".format(playlistId, clientId, secretToken))
    else:
        playlistUrls = requests.get("http://api.soundcloud.com/playlists/{}?client_id={}".format(playlistId, clientId))
    log_debug(f"Playlist URL: {playlistUrls.url}")
    log_debug(f"Status code: {playlistUrls.status_code}")
    permalinkUrls = json.loads(playlistUrls.content)
    description = []

    log_debug("Number of tracks: {}".format(int(permalinkUrls["track_count"])))
    for i in range(int(permalinkUrls["track_count"])):
        try:
            description.append(i)
            description[i] = permalinkUrls["tracks"][i]["description"]
        except IndexError:
            log_debug(f"Error on description (index {i}")
            log_debug("Setting description to empty string")
            description[i] = ""

    return description

def get_user_id(profile_url):
    resolve_url = "https://api-mobi.soundcloud.com/resolve?permalink_url=" + profile_url + "&client_id=iZIs9mchVcX5lhVRyQGGAYlNPVldzAoX&format=json&app_version=1582537945"
    r = requests.get(resolve_url)
    r = r.content
    x = json.loads(r)
    return x["id"]

def get_tracks_account(link):
    return get_tracks_account_rec("https://api-mobi.soundcloud.com/users/{}/profile?client_id={}&format=json&app_version={}".format(get_user_id(link), clientId, appVersion))

def get_tracks_account_rec(resolve_url):
    r = requests.get(resolve_url)
    r = r.content
    x = json.loads(r)
    songs = []
    try:
        for i in x["posts"]["collection"]:
            try:
                if i["type"] == "track":
                    songs.append(i["track"]["permalink_url"])
            except:
                pass
    except:
        pass

    try:
        for i in x["collection"]:
            try:
                if i["type"] == "track":
                    songs.append(i["track"]["permalink_url"])
            except:
                pass
    except:
        pass
    try:
        if x["posts"]["next_href"] is not None:
            return songs + get_tracks_account_rec(re.sub(r'limit=', r'limit=100', x["posts"]["next_href"])  + "&client_id=iZIs9mchVcX5lhVRyQGGAYlNPVldzAoX&format=json&app_version=1582537945")
    except:
        if x["next_href"] is not None:
            return songs + get_tracks_account_rec(re.sub(r'limit=', r'limit=100', x["next_href"])  + "&client_id={}&format=json&app_version={}".format(clientId, appVersion))

    return songs

def get_account_name(link):
    resolve_url = "https://api-mobi.soundcloud.com/resolve?permalink_url=" + link + "&client_id=iZIs9mchVcX5lhVRyQGGAYlNPVldzAoX&format=json&app_version=1582537945"
    r = requests.get(resolve_url)
    r = r.content
    x = json.loads(r)
    try:
        return x["user"]["permalink"]
    except:
        return x['permalink']

def downloadUserTracks(soundcloudUrl):
    print("This is a user!")
    print("URL: {}".format(soundcloudUrl))
    while True:
        try:
            account_tracks = get_tracks_account(soundcloudUrl)
            break
        except:
            time.sleep(2)

    changeDirectory(get_account_name(soundcloudUrl))
    
    if resumeDownloadFlag is True:
        if not os.path.exists(lastTrackIndexFilePath):
            lastTrackIndexFile = open(lastTrackIndexFilePath, 'w+')
            lastTrackIndex = 0
            lastTrackIndexFile.write(str(lastTrackIndex))
        else:
            lastTrackIndexFile = open(lastTrackIndexFilePath, 'r')
            lastTrackIndex = int(lastTrackIndexFile.read())
    else:
        lastTrackIndex = -1
        if not os.path.exists(lastTrackIndexFilePath):
            lastTrackIndexFile = open(lastTrackIndexFilePath, 'w+')
            lastTrackIndexFile.write(str(lastTrackIndex))

    index = 0
    for x in account_tracks:
        try:
            if index > lastTrackIndex:
                downloadSingleTrack(x, "", 1, 0)
                lastTrackIndexFile = open(lastTrackIndexFilePath, 'w')
                lastTrackIndexFile.write(str(index))
                lastTrackIndexFile.close()
        except Exception as e: 
            print(e)
        index += 1
    log_debug("Download of playlist finished, deleting last_track_index.txt ...")
    os.remove("last_track_index.txt")

def downloadUserLikes(soundcloudUrl):
    if '/likes' in soundcloudUrl:
        soundcloudUrl = soundcloudUrl.split('/likes')[0]
    log_debug("Getting user ID for {}".format(soundcloudUrl))
    user_id = get_user_id(soundcloudUrl)
    log_debug("User ID: {}".format(user_id))

    liked_tracks = getUserLikesTracksRec("https://api-mobi.soundcloud.com/users/{}/likes?offset=0&limit=300&client_id={}&format=json&app_version={}".format(user_id, clientId, appVersion))
    print("Liked tracks: {}".format(len(liked_tracks)))
    liked_playlists = getUserLikesPlaylistsRec("https://api-mobi.soundcloud.com/users/{}/likes?offset=0&limit=300&client_id={}&format=json&app_version={}".format(user_id, clientId, appVersion))
    print("Liked playlists: {}".format(len(liked_playlists)))
    print("Enter a number:")
    print("    [1] Only download liked tracks")
    print("    [2] Only download liked playlists")
    print("    [3] Download both liked tracks and liked playlists")
    menu_choice = input()

    if menu_choice == "1":
        print("Downloading only tracks!")
        changeDirectory("{}_likes".format(get_account_name(soundcloudUrl)))

        if resumeDownloadFlag is True:
            if not os.path.exists(lastTrackIndexFilePath):
                lastTrackIndexFile = open(lastTrackIndexFilePath, 'w+')
                lastTrackIndex = 0
                lastTrackIndexFile.write(str(lastTrackIndex))
            else:
                lastTrackIndexFile = open(lastTrackIndexFilePath, 'r')
                lastTrackIndex = int(lastTrackIndexFile.read())
        else:
            lastTrackIndex = -1
            if not os.path.exists(lastTrackIndexFilePath):
                lastTrackIndexFile = open(lastTrackIndexFilePath, 'w+')
                lastTrackIndexFile.write(str(lastTrackIndex))

        index = 0
        for i in liked_tracks:
            try:
                if index > lastTrackIndex:
                    downloadSingleTrack(i, "", 1, 0)
                    lastTrackIndexFile = open(lastTrackIndexFilePath, 'w')
                    lastTrackIndexFile.write(str(index))
                    lastTrackIndexFile.close()
            except Exception as e: 
                print(e)
            index += 1
        log_debug("Download of playlist finished, deleting last_track_index.txt ...")
        os.remove("last_track_index.txt")

    if menu_choice == "2":
        changeDirectory("{}_likes".format(get_account_name(soundcloudUrl)))
        for i in liked_playlists:
            downloadPlaylist(i, 1)
            os.chdir(os.path.dirname(os.getcwd()))

    if menu_choice == "3":
        print("Downloading only tracks!")
        changeDirectory("{}_likes".format(get_account_name(soundcloudUrl)))

        if resumeDownloadFlag is True:
            if not os.path.exists(lastTrackIndexFilePath):
                lastTrackIndexFile = open(lastTrackIndexFilePath, 'w+')
                lastTrackIndex = 0
                lastTrackIndexFile.write(str(lastTrackIndex))
            else:
                lastTrackIndexFile = open(lastTrackIndexFilePath, 'r')
                lastTrackIndex = int(lastTrackIndexFile.read())
        else:
            lastTrackIndex = -1
            if not os.path.exists(lastTrackIndexFilePath):
                lastTrackIndexFile = open(lastTrackIndexFilePath, 'w+')
                lastTrackIndexFile.write(str(lastTrackIndex))

        index = 0
        for i in liked_tracks:
            try:
                if index > lastTrackIndex:
                    downloadSingleTrack(i, "", 1, 0)
                    lastTrackIndexFile = open(lastTrackIndexFilePath, 'w')
                    lastTrackIndexFile.write(str(index))
                    lastTrackIndexFile.close()
            except Exception as e: 
                print(e)
            index += 1
        log_debug("Download of playlist finished, deleting last_track_index.txt ...")
        os.remove("last_track_index.txt")

        for i in liked_playlists:
            downloadPlaylist(i, 1)
            os.chdir(os.path.dirname(os.getcwd()))

def getUserLikesTracksRec(resolve_url):
    r = requests.get(resolve_url)
    r = r.content
    r = json.loads(r)
    songs = []
    playlists = []

    try:
        for index in r['collection']:
            try:
                songs.append(index['track']['permalink_url'])
            except:
                pass
    except:
        pass

    if r['next_href'] is not None:
        return songs + getUserLikesTracksRec("{}&client_id={}&format=json&app_version={}".format(r['next_href'], clientId, appVersion))
    else:
        return songs

def getUserLikesPlaylistsRec(resolve_url):
    r = requests.get(resolve_url)
    r = r.content
    r = json.loads(r)
    playlists = []

    try:
        for index in r['collection']:
            try:
                playlists.append(index['playlist']['permalink_url'])
            except:
                pass
    except:
        pass

    if r['next_href'] is not None:
        return playlists + getUserLikesPlaylistsRec("{}&client_id={}&format=json&app_version={}".format(r['next_href'], clientId, appVersion))
    else:
        return playlists

def parseStuff():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-m','--metadata',
        help="Write track metadata to a separate file",
        action="store_true",
        dest="metadataArg",
        )
    parser.add_argument(
        '-dd','--disable-description',
        help="Disable reading and writing of description ID3 tag / JSON",
        action="store_true",
        dest="descriptionFlag"
        )
    parser.add_argument(
        '-r', '--resume',
        help="Resume download of playlist",
        action="store_true",
        dest="resumeDownloadFlag"
        )
    parser.add_argument(
        '--update-linux',
        help="Updates (and installs) scdl to the newest version",
        action="store_true",
        dest="updateLinuxFlag"
        )
    parser.add_argument(
        '--update-windows',
        help="Updates scdl to the newest version (within the current folder)",
        action="store_true",
        dest="updateWindowsFlag"
        )
    parser.add_argument(
        '--debug',
        help="Show output for debugging",
        action="store_true",
        dest="debugFlag"
        )
    parser.add_argument(
        '-s', '--segments',
        help="Set number of segments that will be downloaded in parallel (default = 16)",
        action="store",
        dest="segmentsParallel"
        )
    parser.add_argument(
        '-f','--ffmpeg-location',
        help="Path to ffmpeg. Can be the containing directory or ffmpeg executable itself",
        action="store",
        dest="ffmpegPath"
    )
    parser.add_argument(
        '--progressive',
        help="Download progressive audio files in one go instead of segments",
        action="store_true",
        dest="progressiveFlag"


        )

    args = parser.parse_args()

    global debugFlag
    if args.debugFlag is True:
        debugFlag = True
    else:
        debugFlag = False

    global updateLinuxFlag
    if args.updateLinuxFlag is True:
        updateLinuxFlag = True
    else:
        updateLinuxFlag = False

    global updateWindowsFlag
    if args.updateWindowsFlag is True:
        updateWindowsFlag = True
    else:
        updateWindowsFlag = False

    global descriptionDisableFlag
    if args.descriptionFlag is True:
        descriptionDisableFlag = True
    else:
        descriptionDisableFlag = False

    global metadataFlag
    if args.metadataArg is True:
        metadataFlag = True
    else:
        metadataFlag = False

    global segmentsParallel
    if args.segmentsParallel:
        segmentsParallel = args.segmentsParallel

    global resumeDownloadFlag
    if args.resumeDownloadFlag is True:
        resumeDownloadFlag = True
    else:
        resumeDownloadFlag = False

    global ffmpegPath
    if args.ffmpegPath:
        ffmpegPath = os.path.abspath(args.ffmpegPath)
        if os.path.exists(ffmpegPath):
            if os.path.isdir(ffmpegPath):
                ffmpegPath = os.path.join(ffmpegPath, "ffmpeg")
        else:
            print("ffmpeg-location is incorrect - path \"" + ffmpegPath + "\" does not exist")
            exit()
    else:
        ffmpegPath = "ffmpeg"

    global progressiveFlag
    if args.progressiveFlag is True:
        progressiveFlag = True
    else:
        progressiveFlag = False

    log_debug(f"debugFlag = {debugFlag}")
    log_debug(f"updateLinuxFlag = {updateLinuxFlag}")
    log_debug(f"updateWindowsFlag = {updateWindowsFlag}")
    log_debug(f"descriptionDisableFlag = {descriptionDisableFlag}")
    log_debug(f"premiumFlag = {premiumFlag}")
    log_debug(f"metadataFlag =  {metadataFlag}")
    log_debug(f"segmentsParallel = {segmentsParallel}")
    log_debug(f"resumeDownloadFlag = {resumeDownloadFlag}")
    log_debug(f"progressiveFlag = {progressiveFlag}")
    log_debug(f"ffmpegPath = {ffmpegPath}")

