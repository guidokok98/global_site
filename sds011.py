# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 11:26:51 2023

- set data reporting mode to query
- check the checksum byte! alles bij elkaar opgeteld %0x100

working process:
    - set to work
    - wait 30 seconds
    - send Query data command
    - set to sleep
    - wait given time


@author: Guido
"""

import serial
import time

#class for sds011 sensor
class sds011:
    partial_serial_dev = None
    serial_dev = None
    ser = None
    retry_count = 3
    baudrate = 9600
    headByte = b'\xAA'
    commandIdByte = b'\xB4'
    tailByte= b'\xAB'
    allSensorsByte = b'\xFF'
    pm25 = None
    pm100 = None
    
    #when new class object is made, set temp,humi and press oversampling on 8 and IIR filter on 3
    def __init__(self):
        self.partial_serial_dev = 'ttyUSB0'
        self.serial_dev = '/dev/%s' % self.partial_serial_dev
        # self.serial_dev = 'COM4'
        #set query mode! and sleep
        self.setSleepOrWork('sleep')
        self.setDataReportingMode('query')
        
    #deconstructor
    def __del__(self):
        self.ser.close()
        
    #connect to serial
    def connect_serial(self):
        self.ser =  serial.Serial(self.serial_dev,
                            baudrate=self.baudrate,
                            bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            timeout=1.0
                            )
    #send the payload
    def sendBytes(self, toSend):
        # print('to send: ',toSend)
        self.ser.write(toSend)

    #read out serial for set amount of bytes
    def readSerial(self, numberOfBytes):
        s=self.ser.read(numberOfBytes)
        # print('reading from serial: ',s)
        if len(s) >0:
            print('checksup checks out: ', self.checkCheckSum(s))
        return s
    
    def makePayload(self, dataBytes):
        command = self.headByte +self.commandIdByte + dataBytes + self.calcCheckSum(dataBytes)+ self.tailByte
        # print('payload made: ',command)
        return command
    
    #calculate the checkSum
    def calcCheckSum(self, dataBytes):
        bytesSum = 0
        for byte in dataBytes:
            bytesSum += byte
        
        checkSum = bytesSum % 0x100
        return checkSum.to_bytes(1, 'big')
        
    def checkCheckSum(self, payload):
        dataBytes = payload[2:-2]
        checkSum = payload[-2]
        checkSumCalc = self.calcCheckSum(dataBytes)
        # print('recCheckSum: ', checkSum)
        # print('CalcedCheckSum: ', int.from_bytes(checkSumCalc, "big"))
        return (checkSum == int.from_bytes(checkSumCalc, "big"))
        
    def setDataReportingMode(self, mode):
        self.connect_serial()
        if mode == 'query':
            dataBytes = b"\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF"
        if mode == 'active':
            dataBytes = b"\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF"
        command = self.makePayload(dataBytes)
        self.sendBytes(command)
        notUsed = self.readSerial(10)
        # print(notUsed)
        self.ser.close()

    def setSleepOrWork(self, mode):
        self.connect_serial()
        if mode == 'sleep':
            dataBytes = b"\x06\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF"
        if mode == 'work':
            dataBytes = b"\x06\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF"
            
        command = self.makePayload(dataBytes)
        self.sendBytes(command)
        notUsed = self.readSerial(10)
        # print(notUsed) 
        self.ser.close()           
        
    def processData(self, data):
        pm25LowByte =  data[2]
        pm25HighByte = data[3]
        pm25 =( (pm25HighByte << 8) | pm25LowByte)/10.0 #micro g/m^3
        print('pm2.5: ', pm25)
        pm100LowByte =  data[4]
        pm100HighByte = data[5]
        pm100 = ((pm100HighByte << 8) | pm100LowByte)/10.0 #micro g/m^3
        print('pm10: ', pm100)
        return pm25, pm100
        
    def queryDataCmd(self):
        self.connect_serial()
        dataBytes = b"\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF"
        command = self.makePayload(dataBytes)
        self.sendBytes(command)
        data = self.readSerial(10)
        self.ser.close() 
        self.processData(data)
    
    def readout(self):
        self.setSleepOrWork('work')
        time.sleep(35)
        self.queryDataCmd()
        self.setSleepOrWork('sleep')
        return self.pm25, self.pm100
        
        
        
dustSensor = sds011()
pm25, pm100 = dustSensor.readout()
# dustSensor.setDataReportingMode('query')