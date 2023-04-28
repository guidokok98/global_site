# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 11:26:51 2023

@author: Guido
"""

import serial
import struct
import traceback

def connect_serial():
    partial_serial_dev = 'ttyS0'
    serial_dev = '/dev/%s' % partial_serial_dev
    return serial.Serial(serial_dev,
                        baudrate=9600,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=1.0)
#class for bme680 sensor
class mh_z19c:
    partial_serial_dev = None
    serial_dev = None
    baudrate = 9600
    retry_count = 3
    
    #when new class object is made, set temp,humi and press oversampling on 8 and IIR filter on 3
    def __init__(self):
        partial_serial_dev = 'ttyS0'
        serial_dev = '/dev/%s' % partial_serial_dev

  
    def checksum(self, array):
      csum = sum(array) % 0x100
      if csum == 0:
        return struct.pack('B', 0)
      else:
        return struct.pack('B', 0xff - csum + 1)
    
    def read_concentration(self):
      try:
        ser = connect_serial()
        for retry in range(self.retry_count):
          result=ser.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
          s=ser.read(9)
        if len(s) >= 4 and s[0] == 0xff and s[1] == 0x86 and ord(self.checksum(s[1:-1])) == s[-1]:
          return s[2]*256 + s[3]
      except:
         traceback.print_exc()
      return ""
  
co2Sensor = mh_z19c()
print(co2Sensor.read_concentration())