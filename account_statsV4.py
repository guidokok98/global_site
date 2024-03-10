# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 15:02:43 2021

@author: guido
To do:
 - loadDf start df with all champs/maps
"""
from riotwatcher import *
import pandas as pd
import time
import os
from pathlib import Path
from dfCombiner import *

#define your self
api_key = 'RGAPI-0f24618e-f080-457f-852d-bab56dc3b4cd'  #api key from riot from https://developer.riotgames.com/
path = str(Path(__file__).parent.absolute())
basedir = path+'/apps/databaseLoL/'           #where the data should be saved
watcher = LolWatcher(api_key)
my_region = 'euw1'

#sorting parameters
userChampsSort = ['winrate','played','won', 'damage_diff']
summonersSort = ['played_with', 'won_with', 'summoner_name']
champStatsSort = ['winrate','tot_played']
mapStatsSort = ['played', 'winrate']
champsInfoSort = ['chest_granted', 'champion_name']

#build up the champion dictionary
def champ_dict():
    # check league's latest version
    latest = watcher.data_dragon.versions_for_region(my_region)['n']['champion']
    # Lets get some champions static information
    static_champ_list = watcher.data_dragon.champions(latest, False, 'en_US')
    # champ static list data to dict for looking up
    champ_dict = {}
    #saves champions with id in a dictionary
    for key in static_champ_list['data']:
        row = static_champ_list['data'][key]
        champ_dict[row['key']] = row['id']
    # print('champs loaded')
    return champ_dict

def lol_version():
    latest = watcher.data_dragon.versions_for_region('euw1')['n']['champion']
    # print("lol version: ",latest)
    return latest
#build up the map dictionary
def map_dict():
    latest = watcher.data_dragon.versions_for_region(my_region)['n']['map']
    static_map_list = watcher.data_dragon.maps(latest, 'en_US')
    map_dict = {}
    for key in static_map_list['data']:
        row = static_map_list['data'][key]
        map_dict[row['MapId']] = row['MapName']
    # print('maps loaded')
    return map_dict

def folderScan(givenPath, csvDB):
    """
    scans through the given path and do tasks
    """
    try:
        for file in os.listdir(givenPath):
            # Inisiating the path of the file
            file_path = f"{givenPath}/{file}"
            # Check if file is a folder, if so go in that folder
            if os.path.isdir(file_path):
                newPath = givenPath + "/" + file
                csvDB = folderScan(newPath, csvDB)

            # check if file is a file, if so copy that file
            elif (file.endswith(".csv")):
                csvDB.append(file_path)
    #if there is an error, save it in txt file
    except Exception as error:
        print("path problem: ", str(error))
    return csvDB

class player:
    #info about the match
    matchesData = None
    matchData = None
    firstMatchId = None
    gameId = None
    matchDetails = None
    matchMetaData = None
    matchMap = None
    gameMode = None
    gameVersion = None
    #directories and databases
    direct = None
    lastGame = None
    selectedDf = None
    dfName = None
    dfNiv = None
    #participant data
    partData = None
    sumName = None
    #team info
    teamData = [0]
    winTeam = 0
    firstBloodTeam = 0
    firstTowerTeam = 0
    firstInhibTeam = 0
    #single player info
    playerChampId = 0
    playerChamp = 0
    playerTeam = 0
    playerWon = 0
    #user info
    userName = 0
    userData = 0
    userTeam = 0
    userWon = 0
    userNbr = 0
    userChampId = 0
    userChamp = 0
    userCampStats = 0
    #relation between the player and user
    sameTeam = 0
    playerUserRel= 0
    #stats of the user champions
    champsInfo=0
    champId = 0
    champName = 0
    champLvl = 0
    champPoints = 0
    chestGranted = 0
    tokensEarned = 0
    #defines the user
    def __init__(self, userName):
        self.userName = userName
        my_region = 'euw1'
        self.userData = watcher.summoner.by_name(my_region, self.userName)
        self.direct = basedir+self.userName
        self.loadLastGame()
        # self.mkdir(self.direct)
        # self.mkdir(self.direct+"/all")
        # self.mkdir(self.direct+"/all"+"/all")


    def mkdir(self, pth):
        print("making path: ", pth)
        try:
            os.makedirs(pth)
        except:
            None
    #load last game
    def loadLastGame(self):
        try:
            file2write=open(self.direct+'/'+self.userName+"_lastgame.txt",'r')
            self.lastGame = file2write.read()
            file2write.close()
        except:
            self.lastGame = 0
    #saves the first game played
    def saveFirstGame(self):
        # print("open: ", ""+self.direct+'/'+self.userName+"_lastgame.txt")
        self.firstMatchId =  self.matchesData[0]
        file2write=open(""+self.direct+'/'+self.userName+"_lastgame.txt",'w')
        file2write.write(str(self.firstMatchId))
        file2write.close()

    #loads the given Df
    def loadDf(self, dfName, version, subversion):
        if self.dfNiv == "all":
            version = "all"
            subversion = "all"
            loadFromPath = self.direct+"/"
        elif self.dfNiv == "version":
            subversion = "all"
            version = "v"+version
            loadFromPath = self.direct+"/"+version+"/"
        else:
            version = "v"+version
        # print("loading df: ",self.direct+"/"+ version+"/"+subversion+'/'+self.userName+'_'+dfName+'.csv')
        try:
            self.selectedDf = pd.read_csv(r''+self.direct+"/"+version+"/"+subversion+'/'+self.userName+'_'+dfName+'.csv')
        except:
            if self.dfNiv == "all" or self.dfNiv == "all":
                self.mkdir(self.direct+"/"+ version+"/"+subversion+'/')
                print("loading failed")
                csvDB = folderScan(loadFromPath,[])
                self.selectedDf = dfCombiner(csvDB, dfName.split("_")[-2], dfName.split("_")[-1])
            else:
                self.selectedDf = pd.DataFrame()
        # print("loaded: \n",  self.selectedDf)
        return self.selectedDf
    #saves the given df
    def saveDf(self, dfName, sort, version, subversion, ascending = False):
        if self.dfNiv == "all":
            version = "all"
            subversion = "all"
        elif self.dfNiv == "version":
            version = "v"+version
            subversion = "all"
        else:
            version = "v"+version
        # print("saving: ",  self.selectedDf)
        try:
            os.makedirs(self.direct+"/"+version+'/'+subversion)
        except:
            None
        try:
            os.makedirs(self.directself.dfNiv+ version+'/'+"all")
        except:
            None
        saved = False
        self.selectedDf = self.selectedDf.sort_values(by=sort, ascending = ascending)
        saveName = r''+self.direct+"/"+version+"/"+subversion+'/'+self.userName+'_'+dfName+'.csv'
        # print("saving df: ",saveName)
        while saved == False:
            try:
                self.selectedDf.to_csv(saveName, index=False)
                saved = True
            except:
                time.sleep(1)
    #get last 100 games of the player
    def FmatchesData(self):
        done = False
        while done == False:
            try:
                self.matchesData = watcher.match.matchlist_by_puuid(my_region, self.userData['puuid'])
                done = True
            except:
                print('cant get matchlist')
                time.sleep(10)
    #save one specific match
    def FmatchData(self, matchCode):
        self.gameId = matchCode
        # print("gameID: ", self.gameId)
        matchData = watcher.match.by_id(my_region, matchCode)
        self.matchData = matchData
    #sets the gameId
    def FgameId(self):
        self.gameId = self.matchData['gameId']
    #get the match details
    def FmatchDetail(self):
        done = False
        while done == False:
            try:
                allMightyData = watcher.match.by_id(my_region, self.gameId)
                self.matchDetails = allMightyData['info']
                self.matchMetaData = allMightyData['metadata']
                done = True
            except:
                print('cant get matchdetails')
                time.sleep(10)
    #get the played map
    def FmatchMap(self):
        retry = True
        while retry == True:
            try:
                self.matchMap = map_dict[str(self.matchDetails['mapId'])]
                retry = False
            except:
                time.sleep(60)
                updateDicts()
                self.matchMap = 'unknown'
                retry = True
    #get game mode
    def FgameMode(self):
        retry = True
        while retry == True:
            try:
                self.gameMode = self.matchDetails['gameMode']
                # print('gameVersion ', ".".join(self.matchDetails['gameVersion'].split(".")[0:2]))
                retry = False
            except:
                time.sleep(60)
                updateDicts()
                self.gameMode = 'unknown'
                retry = True
    def FgameVersion(self):
        retry = True
        while retry == True:
            try:
                self.gameVersion = ".".join(self.matchDetails['gameVersion'].split(".")[0:2])
                # print('gameVersion ', ".".join(self.matchDetails['gameVersion'].split(".")[0:2]))
                retry = False
            except:
                time.sleep(60)
                updateDicts()
                self.gameMode = 'unknown'
                retry = True
#get info of al the owned champions
    def FchampInfo(self):
        done = False
        while done == False:
            try:
                self.champInfo = watcher.champion_mastery.by_summoner(my_region, self.userData['puuid'])
                done = True
            except:
                print('cant get champs info')
                time.sleep(10)

    #team stats
    #cycle trough the teams to get their stats
    def FteamStats(self):
        for self.teamData in self.matchDetails['teams']:
            self.FwinTeam()
            self.FfirstBloodTeam()
            self.FfirstTowerTeam()
            self.FfirstInhibTeam()
    #get team that won
    def FwinTeam(self):
        if self.teamData['win'] == True:
            self.winTeam = self.teamData['teamId']
    #get team that got first blood
    def FfirstBloodTeam(self):
        if self.teamData['objectives']['champion']['first'] == True:
            self.firstBloodTeam = self.teamData['teamId']
    #get team that got first tower
    def FfirstTowerTeam(self):
        if self.teamData['objectives']['tower']['first'] == True:
            self.firstTowerTeam = self.teamData['teamId']
    #get team that got first inib
    def FfirstInhibTeam(self):
        if self.teamData['objectives']['inhibitor']['first'] == True:
            self.firstInhibTeam = self.teamData['teamId']


    #user
    #finds the user
    def FfindUser(self):
        for i in range(0,len(self.matchDetails['participants']),1):
            self.partData = self.matchDetails['participants'][i]
            self.FsumName()
            if self.sumName == self.userName:
                self.userNbr = i
                break
        self.Fteam()
        self.userTeam = self.playerTeam
        self.FplayerWon()
        self.userWon = self.playerWon
        self.Fchamp()
        self.userChampId = self.playerChampId
        self.userChamp = self.playerChamp
        self.FuserChampStats()
    #saves the champ stats of the user
    def FuserChampStats(self):
        self.selectedDf = self.loadDf(self.gameMode+'_'+'userChamps', self.gameVersion.split(".")[0], self.gameVersion)
        self.dfName = 'userChamps'
        self.userCampStats = self.matchDetails['participants'][self.userNbr]
        self.selectedDf =self.FaddVal('champion_name', self.userChamp, 'played', 1)
        self.selectedDf =self.FaddVal('champion_name', self.userChamp, 'won', 0)
        if self.userWon == True:
            self.selectedDf =self.FaddVal('champion_name', self.userChamp, 'won', 1)
        self.selectedDf =self.FaddVal('champion_name', self.userChamp, 'kills', self.userCampStats['kills'])
        self.selectedDf =self.FaddVal('champion_name', self.userChamp, 'deaths', self.userCampStats['deaths'])
        self.selectedDf =self.FaddVal('champion_name', self.userChamp, 'assists', self.userCampStats['assists'])
        self.selectedDf =self.FgemVal('champion_name', self.userChamp, 'average_damage_dealt', self.userCampStats['totalDamageDealtToChampions'])
        self.selectedDf =self.FgemVal('champion_name', self.userChamp, 'average_damage_taken', self.userCampStats['totalDamageTaken'])
        self.selectedDf =self.FgemVal('champion_name', self.userChamp, 'damage_diff', (self.userCampStats['totalDamageDealtToChampions']-self.userCampStats['totalDamageTaken']))
        self.selectedDf =self.FaddVal('champion_name', self.userChamp, 'double_kills', self.userCampStats['doubleKills'])
        self.selectedDf =self.FaddVal('champion_name', self.userChamp, 'triple_kills', self.userCampStats['tripleKills'])
        self.selectedDf =self.FaddVal('champion_name', self.userChamp, 'quadra_kills', self.userCampStats['quadraKills'])
        self.selectedDf =self.FaddVal('champion_name', self.userChamp, 'penta_kills', self.userCampStats['pentaKills'])
        self.selectedDf =self.FaddVal('champion_name', self.userChamp, 'unreal_kills', self.userCampStats['unrealKills'])
        self.selectedDf =self.FgemVal('champion_name', self.userChamp, 'average_healing_done', self.userCampStats['totalHeal'])
        self.selectedDf =self.FgemVal('champion_name', self.userChamp, 'cc_score', self.userCampStats['timeCCingOthers'])

        totPlayed =self.FreadDf(self.selectedDf,'champion_name', self.userChamp, 'played')
        totWon = self.FreadDf(self.selectedDf,'champion_name', self.userChamp, 'won')
        winRate = round(((totWon/totPlayed)*100.),2)
        self.selectedDf = self.FoverwriteVal('champion_name', self.userChamp, 'winrate', winRate)
        self.saveDf((self.gameMode+'_'+'userChamps'),userChampsSort, self.gameVersion.split(".")[0], self.gameVersion)

    #players
    #cycle through the players in the match
    def FplayersCycle(self):
        self.FfindUser()
        for i in range(0,len(self.matchDetails['participants']),1):
            self.partData = self.matchDetails['participants'][i]
            self.FsumName()
            self.Fchamp()
            self.Fteam()
            self.FsameTeam()
            self.FplayerUserRel()
            self.FchampsStats()
    #get summonersname of the player
    def FsumName(self):
        self.sumName = self.partData['summonerName']
    #get played champ of the player
    def Fchamp(self):
        self.playerChampId = self.partData['championId']
        retry = True
        while retry == True:
            try:
                self.playerChamp = champ_dict[str(self.playerChampId)]
                retry = False
            except:    
                self.playerChamp = 'unknown'
                time.sleep(60)
                updateDicts()
                retry = True
    #get the team of the player
    def Fteam(self):
        self.playerTeam = self.partData['teamId']
    #checks if the player won
    def FplayerWon(self):
        if self.playerTeam == self.winTeam:
            self.playerWon = True
        else:
            self.playerWon = False
    #player-user
    #checks if the team is the same as the user
    def FsameTeam(self):
        if (self.playerTeam == self.userTeam):
            self.sameTeam = True
        else:
            self.sameTeam = False
    #relationship between user and player
    def FplayerUserRel(self):
        self.dfName = 'summoners'
        self.selectedDf = self.loadDf(self.gameMode+'_'+'summoners', self.gameVersion.split(".")[0], self.gameVersion)
        if self.sameTeam == True:
            self.selectedDf = self.FaddVal('summoner_name', self.sumName, 'played_with', 1)
            self.selectedDf = self.FaddVal('summoner_name', self.sumName, 'won_with', 0)
            self.selectedDf = self.FaddVal('summoner_name', self.sumName, 'played_against', 0)
            self.selectedDf = self.FaddVal('summoner_name', self.sumName, 'lost_against', 0)
            if self.userWon == True:
                self.selectedDf = self.FaddVal('summoner_name', self.sumName, 'won_with', 1)

        elif self.sameTeam == False:
            self.selectedDf = self.FaddVal('summoner_name', self.sumName, 'played_with', 0)
            self.selectedDf = self.FaddVal('summoner_name', self.sumName, 'won_with', 0)
            self.selectedDf = self.FaddVal('summoner_name', self.sumName, 'played_against', 1)
            self.selectedDf = self.FaddVal('summoner_name', self.sumName, 'lost_against', 0)
            if self.userWon == False:
                self.selectedDf = self.FaddVal('summoner_name', self.sumName, 'lost_against', 1)
                
        t = time.localtime(time.time())
        date = str(t.tm_mday)+'-'+str(t.tm_mon)+'-'+str(t.tm_year)+' '+str(t.tm_hour)+':'+str(t.tm_min)
        self.selectedDf = self.FoverwriteVal('summoner_name', self.sumName, 'date', date)
        self.selectedDf = self.FoverwriteVal('summoner_name', self.sumName, 'last_played', self.playerChamp)
        self.saveDf((self.gameMode+'_'+'summoners'), summonersSort, self.gameVersion.split(".")[0], self.gameVersion)
    #get stats with or against the champs the user wins with or loses
    def FchampsStats(self):
        global totPlayed, totWon
        self.dfName = 'champStats'
        self.selectedDf = self.loadDf(self.gameMode+'_'+'champStats', self.gameVersion.split(".")[0], self.gameVersion)
        if self.sameTeam == True:
            self.selectedDf=self.FaddVal('champion_name', self.playerChamp, 'played_with', 1)
            self.selectedDf=self.FaddVal('champion_name', self.playerChamp, 'won_with', 0)
            self.selectedDf=self.FaddVal('champion_name', self.playerChamp, 'played_against', 0)
            self.selectedDf=self.FaddVal('champion_name', self.playerChamp, 'lost_against', 0)
            if self.userWon == True:
                self.selectedDf=self.FaddVal('champion_name', self.playerChamp, 'won_with', 1)
        elif self.sameTeam == False:
            self.selectedDf=self.FaddVal('champion_name', self.playerChamp, 'played_with', 0)
            self.selectedDf=self.FaddVal('champion_name', self.playerChamp, 'won_with', 0)
            self.selectedDf=self.FaddVal('champion_name', self.playerChamp, 'played_against', 1)
            self.selectedDf=self.FaddVal('champion_name', self.playerChamp, 'lost_against', 0)
            if self.userWon == False:
                self.selectedDf=self.FaddVal('champion_name', self.playerChamp, 'lost_against', 1)
        totPlayed =self.FreadDf(self.selectedDf,'champion_name', self.playerChamp, 'played_with') + self.FreadDf(self.selectedDf,'champion_name', self.playerChamp, 'played_against')
        totWon = self.FreadDf(self.selectedDf,'champion_name', self.playerChamp, 'won_with') + self.FreadDf(self.selectedDf,'champion_name', self.playerChamp, 'lost_against')
        winRate = round(((totWon/totPlayed)*100.),2)
        self.selectedDf = self.FoverwriteVal('champion_name', self.playerChamp, 'winrate', winRate)
        self.selectedDf = self.FoverwriteVal('champion_name', self.playerChamp, 'tot_played', totPlayed)
        self.saveDf((self.gameMode+'_'+'champStats'), champStatsSort, self.gameVersion.split(".")[0], self.gameVersion)
    #map
    #get map stats
    def FmapStats(self):
        self.dfName = 'mapStats'
        self.selectedDf = self.loadDf('mapStats', self.gameVersion.split(".")[0], self.gameVersion)
        self.selectedDf= self.FaddVal('map', self.gameMode, 'played', 1)
        self.selectedDf=self.FaddVal('map', self.gameMode, 'won', 0)
        self.selectedDf=self.FaddVal('map', self.gameMode, 'won_with_first_blood', 0)
        self.selectedDf=self.FaddVal('map', self.gameMode, 'lost_with_first_blood', 0)
        self.selectedDf=self.FaddVal('map', self.gameMode, 'won_with_first_tower', 0)
        self.selectedDf=self.FaddVal('map', self.gameMode, 'lost_with_first_tower', 0)
        self.selectedDf=self.FaddVal('map', self.gameMode, 'won_with_first_b&t', 0)
        self.selectedDf=self.FaddVal('map', self.gameMode, 'lost_with_first_b&t', 0)
        self.selectedDf=self.FaddVal('map', self.gameMode, 'won_with_first_inibitor', 0)
        self.selectedDf=self.FaddVal('map', self.gameMode, 'lost_with_first_inibitor', 0)
        self.selectedDf=self.FaddVal('map', self.gameMode, 'won_with_all', 0)
        self.selectedDf=self.FaddVal('map', self.gameMode, 'lost_with_all', 0)
        if self.userWon == True:
            self.selectedDf=self.FaddVal('map', self.gameMode, 'won', 1)
            if self.userTeam == self.firstBloodTeam:
                self.selectedDf=self.FaddVal('map', self.gameMode, 'won_with_first_blood', 1)
            if self.userTeam == self.firstTowerTeam:
                self.selectedDf=self.FaddVal('map', self.gameMode, 'won_with_first_tower', 1)
            if self.userTeam == self.firstInhibTeam:
                self.selectedDf=self.FaddVal('map', self.gameMode, 'won_with_first_inibitor', 1)
            if self.userTeam == self.firstBloodTeam and self.userTeam == self.firstTowerTeam:
                self.selectedDf=self.FaddVal('map', self.gameMode, 'won_with_first_b&t', 1)
            if self.userTeam == self.firstBloodTeam and self.userTeam == self.firstTowerTeam and self.userTeam == self.firstInhibTeam:
                self.selectedDf=self.FaddVal('map', self.gameMode, 'won_with_all', 1)

        if self.userWon == False:
            self.selectedDf=self.FaddVal('map', self.gameMode, 'won', 0)
            if self.userTeam == self.firstBloodTeam:
                self.selectedDf=self.FaddVal('map', self.gameMode, 'lost_with_first_blood', 1)
            if self.userTeam == self.firstTowerTeam:
                self.selectedDf=self.FaddVal('map', self.gameMode, 'lost_with_first_tower', 1)
            if self.userTeam == self.firstInhibTeam:
                self.selectedDf=self.FaddVal('map', self.gameMode, 'lost_with_first_inibitor', 1)
            if self.userTeam == self.firstBloodTeam and self.userTeam == self.firstTowerTeam:
                self.selectedDf=self.FaddVal('map', self.gameMode, 'lost_with_first_b&t', 1)
            if self.userTeam == self.firstBloodTeam and self.userTeam == self.firstTowerTeam and self.userTeam == self.firstInhibTeam:
                self.selectedDf=self.FaddVal('map', self.gameMode, 'lost_with_all', 1)

        totPlayed =self.FreadDf(self.selectedDf,'map', self.gameMode, 'played')
        totWon = self.FreadDf(self.selectedDf,'map', self.gameMode, 'won')
        try:
            winRate = round(((totWon/totPlayed)*100.),2)
        except:
            print(f'\n cant calculate winrate: {totPlayed}, {totWon} \n')
            winRate =-1
        self.selectedDf = self.FoverwriteVal('map', self.gameMode, 'winrate', winRate)
        self.saveDf('mapStats', mapStatsSort, self.gameVersion.split(".")[0], self.gameVersion)

    def FchampsInfo(self):
        self.dfName = 'champsInfo'
        self.selectedDf = self.loadDf('champsInfo', self.gameVersion.split(".")[0], self.gameVersion)
        self.FchampInfo()
        for champ in self.champInfo:
            self.champId = champ['championId']
            self.champName = champ_dict[str(self.champId)]
            self.champLvl = champ['championLevel']
            self.champPoints = champ['championPoints']
            self.tokensEarned = champ['tokensEarned']
            self.chestGranted = champ['chestGranted']
            if self.chestGranted == True:
                self.chestGranted = 'yes'
            else:
                self.chestGranted = 'no'
            self.selectedDf = self.FoverwriteVal('champion_name', self.champName, 'champion_level', self.champLvl)
            self.selectedDf = self.FoverwriteVal('champion_name', self.champName, 'champion_points', self.champPoints)
            self.selectedDf = self.FoverwriteVal('champion_name', self.champName, 'tokens_earned', self.tokensEarned)
            self.selectedDf = self.FoverwriteVal('champion_name', self.champName, 'chest_granted', self.chestGranted)

        self.saveDf('champsInfo', champsInfoSort, self.gameVersion.split(".")[0], self.gameVersion)

    #functions to edit database
    #add value to the cell, if not excist make a new row
    def FaddVal(self, rowColumnName, rowValue, columnName, val):
        df = self.selectedDf
        df = self.FcheckColumn(df, columnName)
        oldVal = self.FreadDf(df, rowColumnName, rowValue, columnName)
        if oldVal == 'None':
            oldVal = 0
            df = self.FaddRow(df)

        newVal = oldVal + val
        df=self.FeditDf(df, rowColumnName, rowValue, columnName, newVal)
        return df

    #add value to the cell, if not excist make a new row
    def FoverwriteVal(self, rowColumnName, rowValue, columnName, val):
        df = self.selectedDf
        df = self.FcheckColumn(df, columnName)
        oldVal = self.FreadDf(df, rowColumnName, rowValue, columnName)
        if oldVal == 'None':
            df = self.FaddRow(df)

        newVal = val
        df=self.FeditDf(df, rowColumnName, rowValue, columnName, newVal)
        return df

    #calculates the averages value to the cell, if not excist make a new row
    def FgemVal(self, rowColumnName, rowValue, columnName, val):
        df = self.selectedDf
        df = self.FcheckColumn(df, columnName)
        oldVal = self.FreadDf(df, rowColumnName, rowValue, columnName)
        timesPlayed = self.FreadDf(df, rowColumnName, rowValue, 'played')
        if oldVal == 'None':
            oldVal = 0
            df = self.FaddRow(df)
        try:
            newVal = oldVal + ((val-oldVal)/timesPlayed)
        except:
            print(f' \n failed newVal: {oldVal}, {val}, {timesPlayed} \n')
        df=self.FeditDf(df, rowColumnName, rowValue, columnName, newVal)
        return df
    #checks if given column exist, if not make the column
    def FcheckColumn(self,df, columnName):
        try:
            df[columnName]
        except:
            df = self.FnewColumn(df, columnName)
        return df

    #readout database
    def FreadDf(self, df, rowColumnName, rowValue, columnName):
        rowNumber = self.FfindRow(df, rowColumnName, rowValue)
        if rowNumber == 'None':
            value = 'None'
        else:
            value = df[columnName][rowNumber]
        return value
    #change given value in the new value
    def FeditDf(self, df, rowColumnName, rowValue, columnName, value):
        rowNumber = self.FfindRow(df, rowColumnName, rowValue)
        try:
            df.at[rowNumber, columnName] = value #changes the value to the new value
        except:
            if isinstance(value, str):
                df[columnName] = df[columnName].astype(str)
                df.at[rowNumber, columnName] = value #changes the value to the new value
        return df
    #find an certian value and returns the row number
    def FfindRow(self, df, rowColumnName, rowValue):
        rowNumber = 'None'
        try:
            rowNumber = (df[df[rowColumnName] == rowValue].index.values[0])
        except:
            if isinstance(rowNumber, str):
                rowNumber = 'None'
        return rowNumber
    #adds a row and puts the row name in it
    def FaddRow(self, df):
        toAdd = []
        df = self.FnewRow(df)
        if self.dfName == 'userChamps':
            df = self.FcheckColumn(df, 'champion_id')
            df = self.moveColumn(df, 'champion_id', 0)
            df = self.FcheckColumn(df, 'champion_name')
            df = self.moveColumn(df, 'champion_name', 1)
            df.champion_name = df.champion_name.astype(str)
            toAdd.append(['champion_id', self.userChampId, 'champion_id', 0])
            toAdd.append(['champion_name', self.userChamp, 'champion_name', '0'])

        elif self.dfName == 'summoners':
            df = self.FcheckColumn(df, 'summoner_name')
            df = self.moveColumn(df, 'summoner_name', 0)
            df.summoner_name = df.summoner_name.astype(str)
            toAdd.append(['summoner_name', self.sumName, 'summoner_name', '0'])

        elif self.dfName == 'mapStats':
            df = self.FcheckColumn(df, 'map')
            df = self.moveColumn(df, 'map', 0)
            df.map = df.map.astype(str)
            toAdd.append(['map', self.gameMode, 'map', '0'])

        elif self.dfName == 'champStats':
            df = self.FcheckColumn(df, 'champion_id')
            df = self.moveColumn(df, 'champion_id', 0)
            df = self.FcheckColumn(df, 'champion_name')
            df = self.moveColumn(df, 'champion_name', 1)
            df.champion_name = df.champion_name.astype(str)
            toAdd.append(['champion_id', self.playerChampId, 'champion_id', 0])
            toAdd.append(['champion_name', self.playerChamp, 'champion_name', '0'])

        if self.dfName == 'champsInfo':
                    df = self.FcheckColumn(df, 'champion_id')
                    df = self.moveColumn(df, 'champion_id', 0)
                    df = self.FcheckColumn(df, 'champion_name')
                    df = self.moveColumn(df, 'champion_name', 1)
                    df.champion_name = df.champion_name.astype(str)
                    toAdd.append(['champion_id', self.champId, 'champion_id', 0])
                    toAdd.append(['champion_name', self.champName, 'champion_name', '0'])

        for add in toAdd:
            df = self.FeditDf(df, add[2], add[3], add[0], add[1])
        return df
    #add new column to the database
    def FnewColumn(self, df,columnName):
        column = []
        for i in range(0, df.shape[0],1):
            column.append(0)
        df[columnName] = column
        return df
    #add new row to the database
    def FnewRow(self, df):
        row = {}
        for i in df.columns:
            row[i] = 0
        df = df.append(row, ignore_index=True)
        return df

    def moveColumn(self, df, columnName, newPos):
        column = df.pop(columnName)
        df.insert(newPos, columnName, column)
        return df

#main function
def getStats(username):
    try:
        global user
        global curVersion
        if curVersion != lol_version():
            updateDicts()
        user = player(username)
        user.FmatchesData()
        for match in user.matchesData:
            doneMain = False
            # while doneMain == False:
            try:
                user.FmatchData(match)
                # user.FgameId()
                print(f'gameId = {user.gameId}')
                if user.gameId == user.lastGame:
                    break;
                user.FmatchDetail()
                #loop here through the big files
                for dfNiv in ["subversion", "version", "all"]: #
                    print("doing: ",dfNiv)
                    user.dfNiv = dfNiv
                    user.FmatchMap()
                    user.FgameMode()
                    user.FgameVersion()
                    user.FmatchMap()
                    print(f'gamemode: {user.gameMode} \t map: {user.matchMap}')
                    user.FteamStats()
                    user.FplayersCycle()
                    user.FmapStats()
                    time.sleep(190/120)
                
                doneMain = True
            except:
                time.sleep(190/120)
        user.saveFirstGame()
        # user.FchampsInfo()
        del user
    except Exception as error:
        print("failed! error: ", error)

def updateDicts():
    global champ_dict, map_dict, my_region, curVersion
    try:
        
        my_region = 'euw1'
        champ_dict = champ_dict()
        map_dict = map_dict()
        curVersion = lol_version()
        my_region = 'europe'
    except:
        None

updateDicts()
print("dicts updated")
getStats('ironsuperhulk')