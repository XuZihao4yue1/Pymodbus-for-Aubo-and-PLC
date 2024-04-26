import struct
import matplotlib.pyplot as plt
import math
import threading
from pymodbus.client.sync import \
    ModbusTcpClient  # 请注意次数的Client 表示的不是从站设备而是希望链接的设备，开始我就以为是把PLC设置为从站模式，后来看官网文档才知道是要链接的下位机设备，

aubo = "192.168.0.101"  # 机械臂IP地址
plc = "192.168.0.102"  # 西门子PLC IP 地址
import time


def float_to_registers(float_value):
    """Convert a float into two 16-bit integer values."""
    # Convert the float into a 32-bit integer representation
    int_value = struct.unpack('I', struct.pack('f', float_value))[0]

    # Split the 32-bit integer into two 16-bit integer values
    register1 = int_value & 0xFFFF
    register2 = (int_value >> 16) & 0xFFFF

    return register1, register2

def write_float_to_registers(client, address, float_value):
    """Write a float value into two consecutive Modbus registers."""
    # Convert the float into two 16-bit integer values
    register1, register2 = float_to_registers(float_value)

    # Write the two 16-bit integer values into two consecutive Modbus registers
    client.write_registers(address, [register1, register2])

def int2float(a, b):
    f = 0
    try:
        z0 = hex(a)[2:].zfill(4)  # 取0x后边的部分 右对齐 左补零
        z1 = hex(b)[2:].zfill(4)  # 取0x后边的部分 右对齐 左补零
        z = z1 + z0  # 高字节在前 低字节在后
        # z=z0+z1 #低字节在前 高字节在后
        # print (z)
        f = struct.unpack('!f', bytes.fromhex(z))[0]  # 返回浮点数
    except BaseException as e:
        print(e)
    return f
# 创建一个条件变量
condition = threading.Condition()
# 创建一个字典来存储数据
data = {"plc_float": None}





def connect_to_aubo(server_ip, server_port):
    client = ModbusTcpClient(server_ip, server_port)
    client.connect()
    print(f"Connected to server {server_ip}:{server_port}")

    try:
        while True:
            with condition:
                # 等待数据准备好
                condition.wait()

                # 从字典中获取数据
                plc_float = data["plc_float"]
                print(f"Received PLC float value: {plc_float}")
            start_time = time.perf_counter_ns()
            result_input = client.read_input_registers(32, 24)
            # 创建一个空列表来存储浮点数
            print(result_input.registers)
            aubo_float_values_input = []

            # 使用一个循环，每次迭代取出两个寄存器的值
            for i in range(0, len(result_input.registers), 2):
                # 使用int2float函数将这两个寄存器的值转换为一个浮点数
                float_value = int2float(result_input.registers[i], result_input.registers[i + 1])
                # 将浮点数添加到列表中
                aubo_float_values_input.append(float_value)
            print(aubo_float_values_input)
            #
            # #检测PLC的输入
            # if plc_float > 5:
            #     client.write_register()
            # client.write_register(242, math.pi*float_values[-1]/180+10)
            address2 = 200
            count2 = 44
            result1 = client.read_holding_registers(address2,
                                                    count2)  # 施耐德PLC的保持型寄存器的起始地址为设置的为%WM1000 数据类型INT， 读取三个字节地址为%WM1000,%WM1001,%WM1002  对应Modbus OX03功能码
            print(result1.registers)  # 打印输出值
            for i in range(6):
                write_float_to_registers(client, 216+i*2, aubo_float_values_input[i])
            for i in range(6, 12):
                radian_value = math.pi * aubo_float_values_input[i] / 180
                write_float_to_registers(client, 232+(i-6)*2, radian_value)
            register242 = client.read_holding_registers(242, 2)
            register242_value = int2float(register242.registers[0], register242.registers[1])
            if plc_float > 5:
                register242_value += 0.5
            elif plc_float < 5:
                register242_value -= 0.5

            write_float_to_registers(client, 242, register242_value)

            #设置机械臂轴动模式
            client.write_register(202, 1)
            register202 = client.read_holding_registers(202, 1)
            print(register202.registers)

            end_time = time.perf_counter_ns()
            elapsed_time = (end_time - start_time)/ 1000000
            print(f"Time taken to read data: {elapsed_time} milliseconds")

            #读取变化
            result1_reread = client.read_holding_registers(232, 12)
            aubo_float_values_reread = []

            # 使用一个循环，每次迭代取出两个寄存器的值
            for i in range(0, len(result1_reread.registers), 2):
                # 使用int2float函数将这两个寄存器的值转换为一个浮点数
                float_value1 = int2float(result1_reread.registers[i], result1_reread.registers[i + 1])
                # 将浮点数添加到列表中
                aubo_float_values_reread.append(float_value1)
            print(aubo_float_values_reread)

            # 你可以在这里添加一个适当的条件来停止循环
            # if some_condition:
            #     break

            # 休眠一段时间，然后再次读取数据
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        client.close()



def connect_to_plc(server_ip, server_port):
    client = ModbusTcpClient(server_ip, server_port)
    client.connect()
    print(f"Connected to server {server_ip}:{server_port}")
    data_timestamp_list = []
    try:
        while True:

            # 获取开始时间
            start_time = time.perf_counter_ns()

            # 执行读取寄存器的操作
            torque = client.read_holding_registers(0, 2)

            # 获取结束时间
            end_time = time.perf_counter_ns()

            # 计算并打印所需的时间（以毫秒为单位）
            elapsed_time = (end_time - start_time) / 1_000_000
            print(f"Time taken to read the register: {elapsed_time} milliseconds")

            if not torque.isError():
                combined = (torque.registers[0] << 16) + torque.registers[1]

                bytes_value = combined.to_bytes(4, byteorder='big')

                plc_float = struct.unpack('>f', bytes_value)[0]

                print(" torque: ", plc_float)
                with condition:
                    # 将数据存储到字典中
                    data["plc_float"] = plc_float
                    # 通知另一个线程数据已经准备好
                    condition.notify_all()
                timestamp = time.time()
                data_timestamp_plc = (timestamp, plc_float)
                data_timestamp_list.append(data_timestamp_plc)


            else:
                print('Error reading holding registers')

            # 你可以在这里添加一个适当的条件来停止循环
            # if some_condition:
            #     break

            # 休眠一段时间，然后再次读取数据
    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        client.close()

    return data_timestamp_list




# Server IP addresses and ports
aubo_ip = "192.168.0.101"  # 机械臂IP地址
aubo_port = 502
plc_ip = "192.168.0.102"  # 西门子PLC IP 地址
plc_port = 502

# Create two threads
# thread1 = threading.Thread(target=connect_to_aubo, args=(aubo_ip, aubo_port))
thread2 = threading.Thread(target=connect_to_plc, args=(plc_ip, plc_port))

timestamps, plc_values1 = zip(*connect_to_plc(plc_ip, plc_port))
print("PLC values:", plc_values1)
print("Timestamps:", timestamps)
plt.plot(timestamps, plc_values1)
plt.xlabel('Time')
plt.ylabel('PLC Value')
plt.show()


# Start the threads
# thread1.start()
thread2.start()

# Wait for both threads to finish
# thread1.join()
thread2.join()

print("Both connections are closed.")
