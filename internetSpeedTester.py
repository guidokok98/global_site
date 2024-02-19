# -*- coding: utf-8 -*-
"""
Created on Sat Feb  3 15:09:32 2024

@author: Guido
"""
import speedtest

def getNetSpeed():
    #devide values by (1024*1024)
    speedTestHelper = speedtest.Speedtest()
    
    speedTestHelper.get_best_server()

    #Check download speed 
    speedTestHelper.download()

    #Check upload speed
    speedTestHelper.upload()

    #generate shareable image
    speedTestHelper.results.share()

    #fetch result
    # return all the information
    # return speedTestHelper.results.dict()
    downloadSpeed = speedTestHelper.results.dict()["download"]/(1024*1024) 
    uploadSpeed = speedTestHelper.results.dict()["upload"]/(1024*1024)
    ping = speedTestHelper.results.dict()["ping"]
    return downloadSpeed, uploadSpeed, ping


# resultDownload, resultUpload, ping = getNetSpeed()
# print("down: ",resultDownload, "\t upload: ",resultUpload, "\t ping: ",ping)