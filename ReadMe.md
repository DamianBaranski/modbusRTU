# ModbusRTU Library

## Overview

The ModbusRTU library provides a lightweight Python interface for communication with Modbus RTU devices over a serial connection. This library is designed to be easy to use and suitable for embedded systems such as MicroPython.

## Features

- Read coils
- Read discrete inputs
- Read holding registers
- Read input registers
- Write single coil
- Write multiple coils
- Write single register
- Write multiple registers

## Usage

```python
import serial
from ModbusRTU import ModbusRTU

# Initialize serial connection
ser = serial.Serial('/dev/ttyS11', baudrate=9600, timeout=1)

# Create ModbusRTU instance
modbus_rtu = ModbusRTU(ser)

# Example usage
print(modbus_rtu.read_holding_registers(1, 40001, 2))
print(modbus_rtu.write_single_register(1, 40001, 12345))
Installation
To install the ModbusRTU library, you can clone this repository and import the ModbusRTU class into your project.
```

##Dependencies

-Python 3.x
-PySerial

##Compatibility

This library is lightweight and suitable for use with MicroPython and other embedded systems. It has minimal dependencies and is designed to work efficiently in resource-constrained environments.

#License

This library is licensed under the MIT License.
