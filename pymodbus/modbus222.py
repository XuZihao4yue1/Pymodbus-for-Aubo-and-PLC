#!/usr/bin/python3
from pymodbus.client.sync import ModbusTcpClient
import time
import datetime
import struct


# 读保持寄存器
def read_AI():
    AI = {}

    master_0 = mt.TcpMaster(
        "192.168.1.111",
        502
    )
    master_0.set_timeout(5.0)

    try:
        a_0 = master_0.execute(1, md.READ_HOLDING_REGISTERS, 512, 3)

        # AI[0] = a_0[0]
        # AI[1] = a_0[1]
        # AI[2] = a_0[2]

        AI[0] = float('%.2f' % int2float(a_0[0], a_0[1]))  # 锅炉蒸发量
        AI[1] = float(a_0[2] / 100.0)  # 转速

    except BaseException as e:
        print(e)
    return (AI)
# 浮点数转换
def int2float(a,b):
    f=0
    try:
        z0=hex(a)[2:].zfill(4) #取0x后边的部分 右对齐 左补零
        z1=hex(b)[2:].zfill(4) #取0x后边的部分 右对齐 左补零
        z=z1+z0 #高字节在前 低字节在后
        #z=z0+z1 #低字节在前 高字节在后
        #print (z)
        f=struct.unpack('!f', bytes.fromhex(z))[0] #返回浮点数
    except BaseException as e:
        print(e)
    return f

