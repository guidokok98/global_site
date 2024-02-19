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
from sds011 import *
from internetSpeedTester import *

def tryXpect(function, params):
    try:
        return function(params)
    except:
        return "error"
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
            df = pd.DataFrame(columns=['date', 'timeStamp', 'temperature', 'outside temperature', 'humidity', 'co2', 'pm2.5', 'pm10', 'pressure','gasResistance'])
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

startTime = time.time()
hasInternet = True
while(connect() != True):
    if time.time() > startTime+60:
        hasInternet = False
        break
        
#function to retreive local temperature of delft
owm = OWM('6b01603dd0364a5ed1d2c2939e45380e')
mgr = owm.weather_manager()
    
def localTemp():
    try:
        weather = mgr.weather_at_place('Delft,NL').weather
        temp = float(weather.temperature('celsius')['temp'])
    except:
        temp = -1.69420
    return temp


path = str(Path(__file__).parent.absolute())
path = path+'/apps/database_roomAnalyzer'
bme680 = bme680(0x77)
co2Sensor = mh_z19c()
try:
	dustSensor = sds011()
except:
	dustSensor = 'error'
#set sensor in force mode
bme680.setBitHigh(0x74, 0)
while((bme680.readReg(0x1D)&0b100000) == 1):
    None

while True:
    startTime = time.time()
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
    co2Val = co2Sensor.read_concentration()
    if dustSensor != 'error':
        pm25, pm100 = dustSensor.readout()
    else:
        pm25= -1.0
        pm100= -1.0
    try:
        resultDownload, resultUpload, ping = getNetSpeed()
    except:
        resultDownload = -1.0
        resultUpload = -1.0
        ping = -1.0

    if localTemp1 != 'None':
        outsideTemp = localTemp1
    print(f'temp: {temp}C \t humi: {humi}% \t co2: {co2Val} \t pm25: {pm25} \t pm100: {pm100} \t press: {press}Pa \t gasRes: {gasRes} Ohm \t outside temp: {outsideTemp} C')
    if humi <= 100.0:
        row['date'] =timeDate
        row['timeStamp'] =timeHMS
        row['temperature'] = temp + dfParam['temperature compensation'][0]
        row['outside temperature'] = outsideTemp
        row['humidity'] = humi
        row['co2'] = co2Val
        row['pm2.5'] = pm25
        row['pm10'] = pm100
        row['pressure'] = press
        row['gasResistance'] = gasRes
        row['download speed'] = resultDownload
        row['upload speed'] = resultUpload
        row['ping'] = ping
        #adds the value of bsec output to the database
       # dfBsec = openDatabase((path+'/bsec/'), 'bsec_data')
       # for val in dfBsec:
       #     row['bsec '+val] = dfBsec[val][0]
        
        df = openDatabase(pathLoc, timeDate)
        df = df.append(row, ignore_index=True)
        closeDatabase(df,pathLoc, timeDate)
    while (time.time() < (startTime+dfParam['time interval'][0]*60)):
        None    
        
    # time.sleep(dfParam['time interval'][0]*60)
