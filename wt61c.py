#!/usr/bin/env python3
import math
import re
import serial
import struct

#Variable
AngInit = b"\xff\xaa\x52"
AccCalib = b"\xff\xaa\x67"
# UQ Accelaration
# UR Angular Velocity Output
# US Angle Output
feature = b"UQ(.{6,6}).{3,3}UR(.{6,6}).{3,3}US(.{6,6}).{3,3}"
fmt_B, fmt_h = "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", "<hhh"

# distance
s_x, s_y, s_z = 0.0, 0.0, 0.0

#Serial Port Open
#ser = serial.Serial('/dev/ttyUSB0',baudrate=115200)
ser = serial.Serial('/dev/ttyS0',baudrate=115200)

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
        # sample data
        # 55 51 00 00 ff ff 07 08 7a 03 30 55 52 00 00 00 00 00 00 7a 03 24 55 53 f7 ff 0b 00 00 00 7a 03 26
        # 0x55 = U 0x51 = Q Accelaration
        # 0x55 = U 0x52 = R Angular Velocity Output
        # 0x55 = U 0x53 = S Angle Output
        frame = struct.unpack(fmt_B, result.group())
        hex_string = "".join("%02x " % b for b in frame)
        print(hex_string)
        sum_Q, sum_R, sum_S = 0, 0, 0
        for i in range(0, 10):
            sum_Q, sum_R, sum_S = sum_Q+frame[i], sum_R+frame[i+11], sum_S+frame[i+22]
            sum_Q, sum_R, sum_S = sum_Q&0x000000ff, sum_R&0x000000ff, sum_S&0x000000ff

        # varify the check sum
        if (sum_Q==frame[10]) and (sum_R==frame[21]) and (sum_S==frame[32]):
            # af acceleration
            # wf angular velocity
            # ef angle
            af, wf, ef = struct.unpack(fmt_h, result.group(1)), struct.unpack(fmt_h, result.group(2)), struct.unpack(fmt_h, result.group(3))
            print(af)
            print(wf)
            print(ef)


            af_l, wf_l, ef_l = [], [], []
            for i in range(0, 3):
                #af_l.append(af[i]/32768.0*16*-9.8), wf_l.append(wf[i]/32768.0*2000*math.pi/180), ef_l.append(ef[i]/32768.0*math.pi)

                # Accelerometer Accuracy: 0.01g
                # Angle/ Inclinometer Accuracy:X, Y-axis: 0.05° Z-axis: 1°(after magnetic calibration)
                af_l.append(round(af[i]/32768.0*16,2)*9.8), wf_l.append(wf[i]/32768.0*2000), ef_l.append(round(ef[i]/32768.0*180,2))

            # m/s^2
            linear_acceleration_x, linear_acceleration_y, linear_acceleration_z = af_l[0], af_l[1], af_l[2]

            # delta t = 0.01s (100Hz)
            s_x = s_x + linear_acceleration_x * 0.01
            s_y = s_y + linear_acceleration_y * 0.01
            s_z = s_z + (linear_acceleration_z - 9.8) * 0.01

            # degree/s
            angular_velocity_x, angular_velocity_y, angular_velocity_z = wf_l[0], wf_l[1], wf_l[2]

            # degree
            roll, pitch, yaw = ef_l[0], ef_l[1], ef_l[2]
            #print(linear_acceleration_x,linear_acceleration_y,linear_acceleration_z)
            print("==============================")
            print(linear_acceleration_x)
            print(linear_acceleration_y)
            print(linear_acceleration_z)
            print("----------distance------------")
            print(s_x,s_y,s_z)
            print("--------------w---------------")
            print(angular_velocity_x,angular_velocity_y,angular_velocity_z)
            print("------------angle-------------")
            print(roll,pitch,yaw)
            print("==============================")
