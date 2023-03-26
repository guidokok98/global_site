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

i2cBus = smbus.SMBus(1)
#bme680 = 0x77
tempRegs = [0x22, 0x23, 0x24]
humiRegs = [0x25, 0x26]
pressRegs = [0x1F, 0x20, 0x21]
gasRegs = [0x2A, 0x2B]

# Look up tables for the possible gas range values
const_array1_int = [2147483647, 2147483647, 2147483647, 2147483647,
        2147483647, 2126008810, 2147483647, 2130303777, 2147483647,
        2147483647, 2143188679, 2136746228, 2147483647, 2126008810,
        2147483647, 2147483647]

const_array2_int = [4096000000, 2048000000, 1024000000, 512000000,
        255744255, 127110228, 64000000, 32258064,
        16016016, 8000000, 4000000, 2000000,
        1000000, 500000, 250000, 125000]

#class for bme680 sensor
class bme680:
    addr = None
    adcTemp = None
    t_fine = None
    temp = 20.
    adcPress = None
    press = None
    adcHumi = None
    humi = None
    res_heat_x = None
    adcGas = None
    gasRes = None
    #temperature calibration data
    par_t1 = None
    par_t2 = None
    par_t3 = None
    #pressure calibration data
    par_p1 = None
    par_p2 = None
    par_p3 = None
    par_p4 = None
    par_p5 = None
    par_p6 = None
    par_p7 = None
    par_p8 = None
    par_p9 = None
    par_p10 = None
    #humidity calibration data
    par_h1 = None
    par_h2 = None
    par_h3 = None
    par_h4 = None
    par_h5 = None
    par_h6 = None
    par_h7 = None
    #gas calibration data
    par_g1 = None
    par_g2 = None
    par_g3 = None

    #when new class object is made, set temp,humi and press oversampling on 8 and IIR filter on 3
    def __init__(self, adress):
        self.addr = adress
        self.tempOversampling8()
        self.humiOversampling8()
        self.pressOversampling8()
        self.IIRfilter3()
        self.tempCalData()
        self.humiCalData()
        self.pressCalData()
        self.gasCalData()
        self.initGas(200)

    #reads out one register
    def readReg(self,reg):
        regVal = i2cBus.read_byte_data(self.addr, reg)
        return regVal

    #write data to one register
    def writeReg(self,reg,val):
        i2cBus.write_byte_data(self.addr, reg, val)

    #turns bit on specified location on high(1)
    def setBitHigh(self,reg,pos):
        regVal = self.readReg(reg)
        regVal = regVal | (1 << pos)
        self.writeReg(reg,regVal)
    #turns bit on specified location on low(0)
    def setBitLow(self,reg,pos):
        regVal = self.readReg(reg)
        regVal = regVal & ~(1<<pos)
        self.writeReg(reg,regVal)

    def convSignedData(self,val, bitsize = 16):
        if val & (1 << (bitsize - 1)) != 0:
            val = val - (1 << bitsize)
        return val
    #turns pressure oversampling on 8x
    def pressOversampling8(self):
        self.setBitLow(0x74, 2)
        self.setBitLow(0x74, 3)
        self.setBitHigh(0x74, 4)
    #reads out pressure calibration data
    def pressCalData(self):
        self.par_p1 = self.readReg(0x8F) << 8 | self.readReg(0x8E)
        self.par_p2 = self.convSignedData(self.readReg(0x91) << 8 | self.readReg(0x90)) #got 55111
        self.par_p3 = self.convSignedData(self.readReg(0x92),8)
        self.par_p4 = self.convSignedData(self.readReg(0x95) << 8 | self.readReg(0x94))
        self.par_p5 = self.convSignedData(self.readReg(0x97) << 8 | self.readReg(0x96))
        self.par_p6 = self.convSignedData(self.readReg(0x99),8)
        self.par_p7 = self.convSignedData(self.readReg(0x98),8)
        self.par_p8 = self.convSignedData(self.readReg(0x9D) << 8 | self.readReg(0x9C))
        self.par_p9 = self.convSignedData(self.readReg(0x9F) << 8 | self.readReg(0x9E)) #got 61746
        self.par_p10 = self.convSignedData(self.readReg(0xA0),8)

    #turns temperature oversampling on 8x
    def tempOversampling8(self):
        self.setBitLow(0x74, 5)
        self.setBitLow(0x74, 6)
        self.setBitHigh(0x74, 7)
    #readsout temperature calibration data
    def tempCalData(self):
        self.par_t1 = self.convSignedData(self.readReg(0xEA) << 8 | self.readReg(0xE9))
        self.par_t2 = self.convSignedData(self.readReg(0x8B) << 8 | self.readReg(0x8A))
        self.par_t3 = self.convSignedData(self.readReg(0x8C),8)
    #turns humidity oversampling on 8x
    def humiOversampling8(self):
        self.setBitLow(0x72, 0)
        self.setBitLow(0x72, 1)
        self.setBitHigh(0x72, 2)
    #readsout huminity calibration data
    def humiCalData(self):
        self.par_h1 = self.convSignedData(self.readReg(0xE3) << 4 | (self.readReg(0xE2)& 0b1111),12)
        self.par_h2 = self.convSignedData(self.readReg(0xE1) << 4 | (self.readReg(0xE2) >> 4),12)
        self.par_h3 = self.convSignedData(self.readReg(0xE4),8)
        self.par_h4 = self.convSignedData(self.readReg(0xE5),8)
        self.par_h5 = self.convSignedData(self.readReg(0xE6),8)
        self.par_h6 = self.convSignedData(self.readReg(0xE7),8)
        self.par_h7 = self.convSignedData(self.readReg(0xE8),8) #got 156
    #readsout gas calibration data
    def gasCalData(self):
        self.par_g1 = self.convSignedData(self.readReg(0xED),8)
        self.par_g2 = self.convSignedData(self.readReg(0xEC) << 8 | (self.readReg(0xEB)))
        self.par_g3 = self.convSignedData(self.readReg(0xEE),8)

    #turns IIRfilter on 3
    def IIRfilter3(self):
        self.setBitLow(0x75, 2)
        self.setBitHigh(0x75, 3)
        self.setBitLow(0x75, 4)

    #readsout temperature and calculates to degrees celcius
    def getTemp(self):
        #reads out MSB, LSB and XLSB of the temperature adc
        MSB = self.readReg(tempRegs[0])
        LSB = self.readReg(tempRegs[1])
        XLSB = self.readReg(tempRegs[2])
        #print(f'\t par_t1: {par_t1} \t par_t2: {par_t2} \t par_t3: {par_t3}')
        #convert MSB,LSB,XLSB into adc value
        self.adcTemp = (MSB << 12) | (LSB << 4) | (XLSB >> 4)
        #calculates temperature (see datasheet)
        var1 = (self.adcTemp >> 3) - (self.par_t1 << 1)
        var2 = (var1*self.par_t2) >> 11
        var3 = ((((var1 >> 1)*(var1 >> 1))>>12)*(self.par_t3<<4)) >>14
        self.t_fine = var2 + var3
        self.temp = (((self.t_fine*5)+128)>>8) /100
        return self.temp
    #readout adc and calculate the pressure
    def getPress(self):
        #reads out MSB, LSB and XLSB of the pressure adc
        MSB = self.readReg(pressRegs[0])
        LSB = self.readReg(pressRegs[1])
        XLSB = self.readReg(pressRegs[2])
        #print(f'p2 parts: {self.readReg(0x91)} \t{self.readReg(0x90)}')
        #convert MSB,LSB,XLSB into adc value
        self.adcPress = (MSB << 12) | (LSB << 4) | (XLSB >> 4)
        #print(f'temp: {self.t_fine} \t press_adc: {self.adcPress} \t par_p1: {par_p1} \t par_p2: {par_p2} \t par_p3: {par_p3} \t par_p4: {par_p4} \t par_p5: {par_p5}')
        #print(f'\t par_p6: {par_p6} \t par_p7: {par_p7} \t par_p8: {par_p8} \t par_p9: {par_p9} \t par_p10: {par_p10} ')
        #calculates the pressure (see datasheet)
        var1 = (self.t_fine >> 1) - 64000
        var2 = ((((var1 >> 2) *(var1>>2))>>11)*self.par_p6)>>2
        var2 = var2 + ((var1*self.par_p5)<<1)
        var2 = (var2>>2)+(self.par_p4<<16)
        var1 = (((((var1>>2)*(var1>>2))>>13)*(self.par_p3<<5))>>3)+((self.par_p2*var1)>>1);
        var1 = var1 >>18
        var1 = ((32768+var1)*self.par_p1)>>15
        press_comp = 1048576 - self.adcPress
        press_comp = ((press_comp-(var2>>12))*(3125))
        if (press_comp >=(1<<30)):
            press_comp = ((press_comp//var1)<<1)
        else:
            press_comp = ((press_comp<<1)/var1)
        var1 = (self.par_p9*(((press_comp>>3)*(press_comp>>3))>>13))>>12
        var2 = ((press_comp>>2)*self.par_p8)>>13
        var3 = ((press_comp>>8)*(press_comp>>8)*(press_comp>>8)*self.par_p10)>>17
        press_comp = (press_comp)+((var1+var2+var3+(self.par_p7<<7))>>4)
        self.press = press_comp/100
        return self.press

    #calculates the humidity
    def getHumi(self):
        temp = int(self.temp*100)
        #reads out MSB and LSB of the humidity adc
        MSB = self.readReg(humiRegs[0])
        LSB = self.readReg(humiRegs[1])
        #converts MSB and LSB into humidity adc
        self.adcHumi = (MSB << 8) | (LSB << 0)
        #print(f'temp: {temp} \t humi_adc: {self.adcHumi} \t par_h1: {par_h1} \t par_h2: {par_h2} \t par_h3: {par_h3} \t par_h4: {par_h4} \t par_h5: {par_h5} \t par_h6: {par_h6} \t par_h7: {par_h7}')
        #calculates the humidity (see datasheet)
        var1 = self.adcHumi - (self.par_h1 <<4) - (int((temp*self.par_h3) // (100))>>1)
        var2 = (self.par_h2*(((temp*self.par_h4)//(100))+
                        (((temp*((temp*self.par_h5)//(100)))>>6)//(100))+((1<<14))))>>10
        var3 = var1*var2
        var4 = ((self.par_h6 <<7)+((temp*self.par_h7)//(100))) >> 4
        var5 = ((var3 >> 14)*(var3>>14))>>10
        var6 = (var4*var5) >> 1
        self.humi_comp = (((var3+var6)>>10)*(1000))>>12
        self.humi = self.humi_comp/1000.
        return self.humi
    #calc the heat resistance value
    def calcHeatVal(self, target_temp):
        amb_temp = int(self.temp*100)
        res_heat_range = (self.readReg(0x02) >>4) &0b11
        res_heat_val = self.convSignedData(self.readReg(0x00),8)
        #print(f'heat_val: {res_heat_val} \t heat_range: {res_heat_range}')
        #print(f'amb_temp: {amb_temp} \t par_g3: {self.par_g3}')
        var1 = ((amb_temp*self.par_g3)//10)<<8
        var2 = (self.par_g1+784)*(((((self.par_g2+154009)*target_temp*5)//100)+3276800)//10)
        var3 = var1+(var2>>1)
        var4 = (var3//(res_heat_range +4))
        var5 = (131*res_heat_val)+65536
        res_heat_x100 = (((var4//var5)-250)*34)
        self.res_heat_x= ((res_heat_x100+50)//100)
    #calculates the gas resistance
    def getGasRes(self):
        if ((self.readReg(0x2B)&0b100000) == 0):
            return None
        MSB = self.readReg(gasRegs[0])
        LSB = self.readReg(gasRegs[1])
        gas_range = self.readReg(0x2B) & 0b1111
        range_switching_error = self.readReg(0x04)
        self.adcGas = (MSB << 2) | ((LSB >> 6)& 0b11)
        #print(f'adc: {self.adcGas} \t gasRange: {gas_range} \t switchingError: {range_switching_error} \t par_g1: {self.par_g1} \t par_g2: {self.par_g2} \t par_g3: {self.par_g3}')
        var1 = (((1340+(5*range_switching_error))*(const_array1_int[gas_range]))>>16)
        var2 = (self.adcGas << 15) - (1 <<24) +var1
        self.gasRes = ((((const_array2_int[gas_range]*var1)>>9)+(var2>>1))/var2)
        return self.gasRes
    #initialises the gas paramaters
    def initGas(self, temp):
        self.writeReg(0x6D, 0x59)
        self.calcHeatVal(temp)
        self.writeReg(0x63, self.res_heat_x)
        self.writeReg(71,0x10)

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
            row['temperature compensation'] = -5.
            row['time interval'] = 5.
            df = df.append(row, ignore_index=True)
        else:
            df = pd.DataFrame(columns=['date', 'timeStamp', 'temperature', 'outside temperature', 'humidity', 'pressure','gasResistance'])
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
    df = openDatabase(path, timeDate)
    dfParam = openDatabase(path, 'parameters')
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
        row['pressure'] = press
        row['gasResistance'] = gasRes
        #adds the value of bsec output to the database
        dfBsec = openDatabase((path+'/bsec/'), 'bsec_data')
        for val in dfBsec:
            row['bsec '+val] = dfBsec[val][0]
        df = df.append(row, ignore_index=True)
        closeDatabase(df,path, timeDate)
    time.sleep(dfParam['time interval'][0]*60)


