from pymodbus.client.sync import ModbusTcpClient
from pymodbus.bit_read_message import ReadCoilsResponse
from pymodbus.register_read_message import ReadInputRegistersResponse
from pymodbus.exceptions import ConnectionException      # 连接失败，用于异常处理

host = '192.168.0.102'
port = 502
client = ModbusTcpClient(host, port)


# 写入线圈
client.write_coil(1, True)
client.write_coil(2, False)
client.write_coil(3, True)

# 读取线圈    注意对于离散量的读取，第二个参数cout是有坑的，必须为8的倍数个
result:ReadCoilsResponse = client.read_coils(address=1,cout=8)     # 从地址1开始读，读取8个线圈，一次读8的倍数个线圈，不设置为8的倍数可能会出现问题
print(result.isError())

# 不建议使用
print(result.getBit(7))            # 这里的参数address不是plc里的地址，而是python列表的address，

print('read_coils ')

# 建议使用
print(result.bits)        # 打印读取结果，一共8位
# 读取其中的位
print(                   
    result.bits[0],
    result.bits[1],
    result.bits[2]
    )         # 相当于result.getBit(0)


# 读取数字输入
result = client.read_discrete_inputs(address=10001,count=8)    # 从10001开始读，读取8位
print(result.bits)


# 读取模拟输入寄存器
input_register_result:ReadInputRegistersResponse = client.read_input_registers(1,count=8)
# print(f'is_error:{input_register_result.isError()}')
print('read_input_registers ')
print(input_register_result.registers)   
print(input_register_result.getRegister(0))   


# 读写保持寄存器
client.write_register(address=40001,value=100)
result:ReadInputRegistersResponse = client.read_holding_registers(address=40001,count=1)
print('read_holding_registers ')
print(result.registers)

#关闭连接
client.close()


