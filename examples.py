import serial
import modbusRTU

# Example usage
s = serial.Serial('/dev/ttyS11')
modbus_rtu = modbusRTU.ModbusRTU(s)
print(modbus_rtu.read_holding_registers(4, 40001, 2))
print(modbus_rtu.read_input_registers(4, 30001, 2))
print(modbus_rtu.write_single_register(4, 40001, 12345))
print(modbus_rtu.write_multiple_registers(4, 40001, [12345, 6789]))
print(modbus_rtu.read_coils(4, 0, 10))
print(modbus_rtu.read_discrete_inputs(4, 0, 10))
print(modbus_rtu.write_single_coil(4, 0, True))
print(modbus_rtu.write_multiple_coils(4, 0, [True, False, True, False, True, False, True, False, True, False]))
