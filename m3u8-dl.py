#!/usr/bin/env python3

import sys
import requests
import tempfile
import os
import time

from urllib.request import urlretrieve
from requests.compat import urljoin

def usage():
    print('Usage: python3 m3u8.py M3U8_URL OUTPUT')

if len(sys.argv) < 3:
    usage()
    exit(1)

SOURCE = sys.argv[1]
OUTPUT = sys.argv[2]

# Downloading the playlist
def extract_videos(playlist_url):
    playlist = requests.get(playlist_url).text
    lines = playlist.splitlines()
    videos = filter(lambda l: len(l.strip()) > 0 and l.strip()[0] != '#', lines)
    full_urls = map(lambda l: urljoin(playlist_url, l), videos)
    return list(full_urls)

print('Downloading the playlist...')
videos = extract_videos(SOURCE)

# Downloading individual videos
segments = []

print('Need to download %d video segments' % len(videos))
for i in range(len(videos)):
    print('Downloading %03d/%03d' % (i + 1, len(videos)))
    segment = tempfile.NamedTemporaryFile(suffix='.ts')
    segments.append(segment)
    urlretrieve(videos[i], segment.name)

# Merging segments
list_file = tempfile.NamedTemporaryFile()
for segment in segments:
    list_file.write(("file '%s'\n" % segment.name).encode())
    list_file.flush()

print('Merging...')
command = "ffmpeg -f concat -safe 0 -i %s -c copy %s" % (list_file.name, OUTPUT)
os.system(command)
