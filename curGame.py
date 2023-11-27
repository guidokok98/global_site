# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 10:40:32 2021

@author: guido
"""
from riotwatcher import *
import pandas as pd
import time
import os
import numpy as np #adding a new colom
from pathlib import Path
#define your self
api_key = 'RGAPI-0f24618e-f080-457f-852d-bab56dc3b4cd'  #api key from riot from https://developer.riotgames.com/
watcher = LolWatcher(api_key)
my_region = 'euw1'

#load the csv file in. if this is not possible return the given dataframe
def readCSV(dfName):
    global path
    file = path+dfName
    try:
        tempDf = pd.read_csv(file)
    except:
        tempDf = pd.DataFrame()
    return tempDf

def checkSummoners(userName, gameMode, sumName):
    global df
    df = readCSV(userName+'_'+gameMode+"_summoners.csv")
    rowNumber = 0
    try:
       rowNumber = df[df["summoner_name"] == sumName].index.values[0]
       plWith = df['played_with'][rowNumber]
       plWon = df['won_with'][rowNumber]
       if plWith != 0:
           plWinRate = round((plWon/plWith)*100,2)
       else:
           plWinRate = 0
       plAgainst = df['played_against'][rowNumber]
       plLost = df['lost_against'][rowNumber]
       if plAgainst !=0:
           plLoseRate = round((plLost/plAgainst)*100,2)
       else:
           plLoseRate = 0
       plLastChamp = df['last_played'][rowNumber]
       plLastDate = df['date'][rowNumber]
       sumString = sumName+": played with "+str(int(plWith))+"   win rate: "+str(plWinRate)+"   played against: "+str(int(plAgainst))+"   lose rate: "+str(plLoseRate)+"   last played: "+plLastChamp +' on: '+plLastDate
       return sumString
    except:
        None

def checkInGamePlayers(userName):
    global path
    global inGame
    sumCode = watcher.summoner.by_name(my_region, userName)['id']
    path = str(Path(__file__).parent.absolute())
    path = path+'/apps/databaseLoL/'+userName+'/'
    playersList = []
    try:
        inGame = watcher.spectator.by_summoner(my_region,sumCode)
        gameMode = inGame['gameMode']
        champion = inGame['participants'][0]['championId']
        playersList.append('In game :)')
        for pl in inGame['participants']:
            if pl['summonerName'] != userName:
                returnedPlayer = checkSummoners(userName, gameMode, pl['summonerName'])
                if returnedPlayer != None:
                    playersList.append(returnedPlayer)
    except:
            playersList.append('Not in game :(')
    return playersList
