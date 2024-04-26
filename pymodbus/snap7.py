import snap7
import struct

def read_real(plc, byte_index, db_number):
    # 读取4个字节的数据
    data = plc.db_read(db_number, byte_index, 4)
    # 将这4个字节的数据解析为real型变量
    real_value = struct.unpack('>f', data)[0]
    return real_value

# 创建一个PLC对象
plc = snap7.client.Client()

# 连接到PLC
plc.connect('192.168.0.102', 0, 1)

# 读取DB1中的real型变量，该变量的起始字节索引为0
real_value = read_real(plc, 0, 1)

print(f'Real value: {real_value}')

# 断开与PLC的连接
plc.disconnect()