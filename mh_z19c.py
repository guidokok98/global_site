# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 11:26:51 2023

@author: Guido
"""

import serial
import struct
import traceback

#class for mh_z19c sensor
class mh_z19c:
    partial_serial_dev = None
    serial_dev = None
    retry_count = 3
    ser = None
    
    #when new class object is made, set temp,humi and press oversampling on 8 and IIR filter on 3
    def __init__(self):
        self.partial_serial_dev = 'ttyS0'
        self.serial_dev = '/dev/%s' % self.partial_serial_dev

    def connect_serial(self):
        self.ser= serial.Serial(self.serial_dev,
                            baudrate=9600,
                            bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            timeout=1.0)
  
    def checksum(self, array):
      csum = sum(array) % 0x100
      if csum == 0:
        return struct.pack('B', 0)
      else:
        return struct.pack('B', 0xff - csum + 1)
    
    def read_concentration(self):
      try:
        self.connect_serial()
        for retry in range(self.retry_count):
          result=self.ser.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
          s=self.ser.read(9)
        self.ser.close()
        if len(s) >= 4 and s[0] == 0xff and s[1] == 0x86 and ord(self.checksum(s[1:-1])) == s[-1]:
          return (s[2]<<8) + s[3]
      except:
         traceback.print_exc()
      return -1