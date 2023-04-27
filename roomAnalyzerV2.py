# -*- coding: utf-8 -*-
#
# by: Guido Kok

import smbus
import time
from pathlib import Path
import pandas as pd
from pyowm.owm import OWM
import urllib.request
import os #use os.system('sudo shutdown -r now') to reboot if error encountered
from bme680 import *
from mh_z19c import *

#converts time from epoch to date and Hours Minutes and Seconds
def convTimeStamp():
    storedTime = time.time()
    timeDate = time.strftime('%Y-%m-%d', time.localtime(storedTime))
    timeHMS = time.strftime('%H:%M:%S', time.localtime(storedTime))
    return timeDate, timeHMS

#loads the database
def openDatabase(path, name):
    try:
        #if database exists
        file = path+'/'+name+'.csv'
        df = pd.read_csv(path+'/'+name+'.csv')
    except:
        #if database doesnt exists
        print('no files')
        if name == "parameters":
            print('parameters selected')
            df = pd.DataFrame(columns=['temperature compensation', 'time interval'])
            row['temperature compensation'] = -2.
            row['time interval'] = 5.
            row['location'] = 'home'
            df = df.append(row, ignore_index=True)
        else:
            df = pd.DataFrame(columns=['date', 'timeStamp', 'temperature', 'outside temperature', 'humidity', 'co2', 'pressure','gasResistance'])
    return df
#saves the database into csv
def closeDatabase(df, path, name):
        df.to_csv(path+'/'+name+'.csv', index=False)


#check internet connection
def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False

while(connect() != True):
    None
#function to retreive local temperature of delft
owm = OWM('6b01603dd0364a5ed1d2c2939e45380e')
mgr = owm.weather_manager()
def localTemp():
    try:
        weather = mgr.weather_at_place('Delft,NL').weather
        temp = float(weather.temperature('celsius')['temp'])
    except:
        temp = 'None'
    return temp


path = str(Path(__file__).parent.absolute())
path = path+'/apps/database_roomAnalyzer'
bme680 = bme680(0x77)
co2Sensor = mh_z19c()
#set sensor in force mode
bme680.setBitHigh(0x74, 0)
while((bme680.readReg(0x1D)&0b100000) == 1):
    None
temp = bme680.getTemp()
humi = bme680.getHumi()
press = bme680.getPress()
gasRes = bme680.getGasRes()

while 1:
    timeDate, timeHMS = convTimeStamp()
    dfParam = openDatabase(path, 'parameters')
    pathLoc = path+'/'+dfParam['location'][0]
    row = {}
    bme680.setBitHigh(0x74, 0)
    while((bme680.readReg(0x1D)&0b100000) == 1):
        None
    temp = bme680.getTemp()
    humi = bme680.getHumi()
    press = bme680.getPress()
    gasRes = bme680.getGasRes()
    localTemp1 = localTemp()
    if localTemp1 != 'None':
        outsideTemp = localTemp1
    #print(f'temp: {temp}C \t humi: {humi}% \t press: {press}Pa \t gasRes: {gasRes}Ohm \t outside temp: {outsideTemp} C')
    if humi <= 100.0:
        row['date'] =timeDate
        row['timeStamp'] =timeHMS
        row['temperature'] = temp + dfParam['temperature compensation'][0]
        row['outside temperature'] = outsideTemp
        row['humidity'] = humi
        row['co2'] = co2Sensor.read_concentration()
        row['pressure'] = press
        row['gasResistance'] = gasRes
        #adds the value of bsec output to the database
        dfBsec = openDatabase((path+'/bsec/'), 'bsec_data')
        for val in dfBsec:
            row['bsec '+val] = dfBsec[val][0]
        
        df = openDatabase(pathLoc, timeDate)
        df = df.append(row, ignore_index=True)
        closeDatabase(df,pathLoc, timeDate)
    time.sleep(dfParam['time interval'][0]*60)


