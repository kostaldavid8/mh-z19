# -*- coding: utf-8 -*-
# original: https://raw.githubusercontent.com/UedaTakeyuki/slider/master/mh_z19.py
#
# © Takeyuki UEDA 2015 -

import serial
import time
import subprocess
import traceback
import getrpimodel
import struct
import platform

# setting

if getrpimodel.model() == "3 Model B":
  serial_dev = '/dev/ttyS0'
  stop_getty = 'sudo systemctl stop serial-getty@ttyS0.service'
  start_getty = 'sudo systemctl start serial-getty@ttyS0.service'
else:
  serial_dev = '/dev/ttyAMA0'
  stop_getty = 'sudo systemctl stop serial-getty@ttyAMA0.service'
  start_getty = 'sudo systemctl start serial-getty@ttyAMA0.service'

# major version of running python
p_ver = platform.python_version_tuple()[0]

def connect_serial():
  return serial.Serial(serial_dev,
                        baudrate=9600,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=1.0)

def mh_z19():
  try:
    ser = connect_serial()
    while 1:

      if p_ver == '2':
        result=ser.write("\xff\x01\x86\x00\x00\x00\x00\x00\x79")
      else:
        result=ser.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")

      s=ser.read(9)

      if p_ver == '2':
        if len(s) >= 4 and s[0] == "\xff" and s[1] == "\x86":
          return {'co2': ord(s[2])*256 + ord(s[3])}
        break
      else:
        if len(s) >= 4 and s[0] == 0xff and s[1] == 0x86:
          return {'co2': s[2]*256 + s[3]}
        break
  except:
     traceback.print_exc()

def read():
  p = subprocess.call(stop_getty, stdout=subprocess.PIPE, shell=True)
  result = mh_z19()
  p = subprocess.call(start_getty, stdout=subprocess.PIPE, shell=True)
  if result is not None:
    return result

def abc_on():
  ser = connect_serial()
  if p_ver == '2':
    result=ser.write("\xff\x01\x79\xa0\x00\x00\x00\x00\xe6")
  else:
    result=ser.write(b"\xff\x01\x79\xa0\x00\x00\x00\x00\xe6")
  ser.close()

def abc_off():
  ser = connect_serial()
  if p_ver == '2':
    result=ser.write("\xff\x01\x79\x00\x00\x00\x00\x00\x86")
  else:
    result=ser.write(b"\xff\x01\x79\x00\x00\x00\x00\x00\x86")
  ser.close()

def span_point_calibration(span):
  ser = connect_serial()
  if p_ver == '2':
    b3 = span / 256;
  else:
    b3 = span // 256;   
  byte3 = struct.pack('B', b3)
  b4 = span % 256; byte4 = struct.pack('B', b4)
  c = checksum([0x01, 0x88, b3, b4])
  if p_ver == '2':
    request = "\xff\x01\x88" + byte3 + byte4 + "\x00\x00\x00" + c
  else:
    request = b"\xff\x01\x88" + byte3 + byte4 + b"\x00\x00\x00" + c
  result = ser.write(request)
  ser.close()

def zero_point_calibration():
  ser = connect_serial()
  if p_ver == '2':
    request = "\xff\x01\x87\x00\x00\x00\x00\x00\x78"
  else:
    request = b"\xff\x01\x87\x00\x00\x00\x00\x00\x78"
  result = ser.write(request)
  ser.close()

def detection_range_5000():
  ser = connect_serial()
  if p_ver == '2':
    request = "\xff\x01\x99\x00\x00\x00\x13\x88\xcb"
  else:
    request = b"\xff\x01\x99\x00\x00\x00\x13\x88\xcb"
  result = ser.write(request)
  ser.close()

def detection_range_2000():
  ser = connect_serial()
  if p_ver == '2':
    request = "\xff\x01\x99\x00\x00\x00\x07\xd0\xc6"
  else:
    request = b"\xff\x01\x99\x00\x00\x00\x07\xd0\xc6"
  result = ser.write(request)
  ser.close()

def checksum(array):
  return struct.pack('B', 0xff - (sum(array) % 0x100) + 1)
