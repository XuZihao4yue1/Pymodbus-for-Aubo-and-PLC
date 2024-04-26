import struct
import math
from pymodbus.client.sync import ModbusTcpClient  # 请注意次数的Client 表示的不是从站设备而是希望链接的设备，开始我就以为是把PLC设置为从站模式，后来看官网文档才知道是要链接的下位机设备，
aubo = "192.168.0.101" # 机械臂IP地址
PLC = "192.168.0.102"  # 西门子PLC IP 地址
import time

# PLC的端口号默认为502，注意也偶尔也有不是的，我这就碰到了查看发现端口号是139，后再重新下载程序时改了下IP地址，断电重启，然后打开施耐德网关托盘程序中 网关管理控制台
# 点开Static Remote Connections选项卡 在Remote IP address 栏输入PLC的IP地址然后点击add.再断电重启PLC然后使用端口号502就正常了
port = 502
client = ModbusTcpClient(aubo, port)  # 下位机（AUBO）建立链接端口，
client.connect()  # 连接PLC

# # 读取施耐德TM251 PLC的输入模块TM3DI16TG模块输入信号数据(输入模块只是可读不可写）  起始位为%IX0.0 读取整个模块16位数据   对应Modbus OX02功能码
# io_in = client.read_discrete_inputs(20, 16)  # 读取输入模块起始地址为0的bit字节数据 ，读取16位数据 将结果存入io_in
# print(io_in.bits[0])  # 打印第4位数据 对应PLC的%IX0.0的值， 如果有输出则打印结果为 True 如果没有输出 则打印结果为 False
# print(io_in.bits[4])  # 打印第4位数据 对应PLC的%IX0.4的值， 如果有输出则打印结果为 True 如果没有输出 则打印结果为 False
#
# # 读取施耐德TM251 PLC的输出模块TM3DQ16TG模块输出线圈数据 起始位为%QW0：包含个%QX0.0到%QX0.7七个数据   对应Modbus OX01功能码
# io_out = client.read_coils(0, 1)  # 读取输出模块起始地址为0的int字节数据 ，True:读取1个字节的数据,如果读取2个字节就写2(整个16点输出模块的状态） 将结果存入io_out
# print(io_out.bits[0])  # 打印0字节数据的第0位 对应PLC的%QX0.0的值，如果有输出则打印结果为 True 如果没有输出 则打印结果为 False
# print(io_out.bits[1])  # 打印0字节数据的第0位 对应PLC的%QX0.1的值，如果有输出则打印结果为 True 如果没有输出 则打印结果为 False

# 读保持寄存器


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


result = client.read_input_registers(32, 26)

# 创建一个空列表来存储浮点数
float_values = []

# 使用一个循环，每次迭代取出两个寄存器的值
for i in range(0, len(result.registers), 2):
    # 使用int2float函数将这两个寄存器的值转换为一个浮点数
    float_value = int2float(result.registers[i], result.registers[i+1])
    # 将浮点数添加到列表中
    float_values.append(float_value)

# 打印所有的浮点数
print(float_values)







# 读取PLC的保持性寄存器的数据
address = 200
count = 30
result1 = client.read_holding_registers(address, count)  # 施耐德PLC的保持型寄存器的起始地址为设置的为%WM1000 数据类型INT， 读取三个字节地址为%WM1000,%WM1001,%WM1002  对应Modbus OX03功能码
print(result1.registers)  # 打印输出值


# 施耐德TM251 PLC的保持型寄存器1002 写收数值（PLC侧程序当数值大于20，Q0.1输出高电平置1，模块上指示灯亮起，小于等于20 Q0.1输出低电平置0 模块指示灯熄灭  对应Modbus OX06功能码
# io_out_write = client.write_register(1002, 21)  # 读取输入模块起始地址为0的bit字节数据 ，读取16位数据 将结果存入io_in
# print(io_out_write.value)  # 打印输出值，
time.sleep(0.5)  # 这个可以删除，

client.close()
# ————————————————
#
# 版权声明：本文为博主原创文章，遵循
# CC
# 4.0
# BY - SA
# 版权协议，转载请附上原文出处链接和本声明。
#
# 原文链接：https: // blog.csdn.net / u010271276 / article / details / 136044399