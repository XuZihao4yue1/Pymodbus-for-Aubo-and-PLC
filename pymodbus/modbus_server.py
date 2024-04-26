'''
 * @Author: liuzhao 
 * @Last Modified time: 2022-10-05 09:56:13 
'''

from pymodbus.server.sync import (
    StartTcpServer,
)
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.version import version

datablock = ModbusSequentialDataBlock.create()
context = ModbusSlaveContext(
    di=datablock,
    co=datablock,
    hr=datablock,
    ir=datablock,
    )
single = True

# Build data storage
store = ModbusServerContext(slaves=context, single=single)


if __name__ == '__main__':

	address = ("0.0.0.0", 503)
	StartTcpServer(
	    context=store,  # Data storage
	    address=address,  # listen address
	  	allow_reuse_address=True,  # allow the reuse of an address
	)

