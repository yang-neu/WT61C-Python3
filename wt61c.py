#!/usr/bin/python3
# -*- coding: utf-8 -*-

import math
import re
import serial
import struct
import time

#Variable
AngInit = b"\xff\xaa\x52"
AccCalib = b"\xff\xaa\x67"
feature = b"UQ(.{6,6}).{3,3}UR(.{6,6}).{3,3}US(.{6,6}).{3,3}"
fmt_B, fmt_h = "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", "<hhh"

#Serial Port Open
ser = serial.Serial('/dev/ttyUSB0',baudrate=115200)

#Serial Port Status Check
if ser.isOpen():
    print("success")
else:
    print("failed")

#Initialization
ser.write(AngInit)
ser.write(AccCalib)

#Main Loop
while True:
   imu_msg = ser.read(size=65)
   result = re.search(feature, imu_msg)
   if result:
        frame = struct.unpack(fmt_B, result.group())
        sum_Q, sum_R, sum_S = 0, 0, 0
        for i in range(0, 10):
            sum_Q, sum_R, sum_S = sum_Q+frame[i], sum_R+frame[i+11], sum_S+frame[i+22]
            sum_Q, sum_R, sum_S = sum_Q&0x000000ff, sum_R&0x000000ff, sum_S&0x000000ff
        if (sum_Q==frame[10]) and (sum_R==frame[21]) and (sum_S==frame[32]):
            af, wf, ef = struct.unpack(fmt_h, result.group(1)), struct.unpack(fmt_h, result.group(2)), struct.unpack(fmt_h, result.group(3))
            af_l, wf_l, ef_l = [], [], []
            for i in range(0, 3):
                af_l.append(af[i]/32768.0*16*-9.8), wf_l.append(wf[i]/32768.0*2000*math.pi/180), ef_l.append(ef[i]/32768.0*math.pi)
            linear_acceleration_x, linear_acceleration_y, linear_acceleration_z = af_l[0], af_l[1], af_l[2]
            angular_velocity_x, angular_velocity_y, angular_velocity_z = wf_l[0], wf_l[1], wf_l[2]
            roll, pitch, yaw = ef_l[0], ef_l[1], ef_l[2]
            print(linear_acceleration_x,linear_acceleration_y,linear_acceleration_z)