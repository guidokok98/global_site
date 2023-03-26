# -*- coding: utf-8 -*-
"""
Created on Fri Jun 11 21:13:12 2021

@author: guido
"""

import pytube
import os
import re
from redvid import Downloader
reddit = Downloader(max_q=True)

def simpleTitle(title):
    title = title.split('.')
    title = title[0:(len(title)-1)]
    str1 = ''
    title=str1.join(title)
    title = re.sub('[^a-zA-Z.\d\s]', '', title)
    return title

def makeVidList(DIR):
    vidNames = []
    for file in os.listdir(DIR):
        # Instantiating the path of the file
        file_path = f'{DIR}/{file}'

        # Checking whether the given file is a directory or not
        if os.path.isfile(file_path):
            fileName = simpleTitle(file)
            vidNames.append(fileName)
    return vidNames

def chkIfDownloaded(vidsList, vidName):
    for vid in vidsList:
        if vid == vidName:
            # print("already downloaded")
            return True

    # print("Not downloaded")
    return False

def makePath(Loc):
    try:
        os.makedirs(Loc)
    except:
        None

def downloadReddit(url,DIR):
    reddit.path = DIR+'/reddit'
    reddit.url = url
    reddit.download()

#Looks if its a single video or a playlist
def downloadTheLink(link, baseDir):
    global succes
    global failed
    global existed
    makePath(baseDir)
    succes = 0
    failed = 0
    existed = 0
    try:
        plName = pytube.Playlist(link).title
        downloadPlaylist(link, baseDir, plName)
    except:
        downloadVideo(link, baseDir)
    return succes, failed, existed
    
def downloadPlaylist(plUrl, baseDir, plName):
    # for plUrl in playlists:
        DIR = baseDir+plName
        makePath(DIR)
        urls = pytube.Playlist(plUrl)
        print(plName)
        for url in urls:
            downloadVideo(url, DIR)

def downloadVideo(url, DIR):
    global succes
    global failed
    global existed
    vidsList = makeVidList(DIR)
    if url.find('reddit.com') > 0:
        try:
            downloadReddit(url, DIR)
            succes += 1
        except:
            failed +=1
    else:
        try:
            yt = pytube.YouTube(url)
            vidTitle = simpleTitle(yt.title+'.mp4')
    
            if chkIfDownloaded(vidsList, vidTitle) == False:
                print(f'downloading: {vidTitle} ({yt.title})')
                yt.title = vidTitle
                ys = yt.streams.get_highest_resolution()
                ys.download(DIR)
                succes += 1
            else:
                existed += 1
    
        except:
            print('cant find vid :(')
            failed += 1