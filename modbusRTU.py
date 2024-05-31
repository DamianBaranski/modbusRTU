import time

class ModbusRTU:
    MODBUS_READ_COILS = 0x01
    MODBUS_READ_DISCRETE_INPUTS = 0x02
    MODBUS_READ_HOLDING_REGISTERS = 0x03
    MODBUS_READ_INPUT_REGISTERS = 0x04
    MODBUS_WRITE_SINGLE_COIL = 0x05
    MODBUS_WRITE_SINGLE_REGISTER = 0x06
    MODBUS_WRITE_MULTIPLE_COILS = 0x0F
    MODBUS_WRITE_MULTIPLE_REGISTERS = 0x10
    REGISTER_OFFSET_HOLDING = 40001
    REGISTER_OFFSET_INPUT = 30001
    RESPONSE_TIMEOUT = 1
    MIN_RESPONSE_LENGTH = 5
    HEADER_LENGTH = 3
    CRC_LENGTH = 2
    WRITE_RESPONSE_LENGTH = 8
    ADDRESS_INDEX = 0
    FUNCTION_CODE_INDEX = 1
    DATA_LENGTH_INDEX = 2
    DATA_START_INDEX = 3
    WRITE_RESPONSE_DATA_START_INDEX = 2
    WRITE_RESPONSE_DATA_END_INDEX = 4
    
    def __init__(self, uart):
        self.uart = uart
        
    def read_coils(self, address, coil, length):
        coil_address = coil
        data = coil_address.to_bytes(2, 'big') + length.to_bytes(2, 'big')
        self._send_data(address, self.MODBUS_READ_COILS, data)
        response = self._receive_data(address, self.MODBUS_READ_COILS, self.MIN_RESPONSE_LENGTH + (length + 7) // 8)
        if response:
            return response
        return None

    def read_discrete_inputs(self, address, input, length):
        input_address = input
        data = input_address.to_bytes(2, 'big') + length.to_bytes(2, 'big')
        self._send_data(address, self.MODBUS_READ_DISCRETE_INPUTS, data)
        response = self._receive_data(address, self.MODBUS_READ_DISCRETE_INPUTS, self.MIN_RESPONSE_LENGTH + (length + 7) // 8)
        if response:
            return response
        return None

    def write_single_coil(self, address, coil, value):
        coil_address = coil
        data = coil_address.to_bytes(2, 'big') + (0xFF00 if value else 0x0000).to_bytes(2, 'big')
        self._send_data(address, self.MODBUS_WRITE_SINGLE_COIL, data)
        response = self._receive_data(address, self.MODBUS_WRITE_SINGLE_COIL, self.WRITE_RESPONSE_LENGTH)
        return response is not None

    def write_multiple_coils(self, address, coil, values):
        coil_address = coil
        length = len(values)
        byte_count = (length + 7) // 8
        coil_data = bytearray()
        for i in range(byte_count):
            byte = 0
            for j in range(8):
                if (i * 8 + j) < length and values[i * 8 + j]:
                    byte |= (1 << j)
            coil_data.append(byte)
        data = coil_address.to_bytes(2, 'big') + length.to_bytes(2, 'big') + byte_count.to_bytes(1, 'big') + coil_data
        self._send_data(address, self.MODBUS_WRITE_MULTIPLE_COILS, data)
        response = self._receive_data(address, self.MODBUS_WRITE_MULTIPLE_COILS, self.WRITE_RESPONSE_LENGTH)
        return response is not None

    def read_holding_registers(self, address, register, length):
        registers = []
        register_address = register - self.REGISTER_OFFSET_HOLDING
        data = register_address.to_bytes(2, 'big') + length.to_bytes(2, 'big')
        self._send_data(address, self.MODBUS_READ_HOLDING_REGISTERS, data)
        response = self._receive_data(address, self.MODBUS_READ_HOLDING_REGISTERS, self.MIN_RESPONSE_LENGTH + length * 2)
        if response:
            for i in range(0, len(response), 2):
                registers.append(int.from_bytes(response[i:i+2], "big", signed=True))
        return registers

    def read_input_registers(self, address, register, length):
        registers = []
        register_address = register - self.REGISTER_OFFSET_INPUT
        data = register_address.to_bytes(2, 'big') + length.to_bytes(2, 'big')
        self._send_data(address, self.MODBUS_READ_INPUT_REGISTERS, data)
        response = self._receive_data(address, self.MODBUS_READ_INPUT_REGISTERS, self.MIN_RESPONSE_LENGTH + length * 2)
        if response:
            for i in range(0, len(response), 2):
                registers.append(int.from_bytes(response[i:i+2], "big", signed=True))
        return registers

    def write_single_register(self, address, register, value):
        register_address = register - self.REGISTER_OFFSET_HOLDING
        data = register_address.to_bytes(2, 'big') + value.to_bytes(2, 'big')
        self._send_data(address, self.MODBUS_WRITE_SINGLE_REGISTER, data)
        response = self._receive_data(address, self.MODBUS_WRITE_SINGLE_REGISTER, self.WRITE_RESPONSE_LENGTH)
        return response is not None

    def write_multiple_registers(self, address, register, values):
        register_address = register - self.REGISTER_OFFSET_HOLDING
        length = len(values)
        data = register_address.to_bytes(2, 'big') + length.to_bytes(2, 'big') + (length * 2).to_bytes(1, 'big')
        for value in values:
            data += value.to_bytes(2, 'big')
        self._send_data(address, self.MODBUS_WRITE_MULTIPLE_REGISTERS, data)
        response = self._receive_data(address, self.MODBUS_WRITE_MULTIPLE_REGISTERS, self.WRITE_RESPONSE_LENGTH)
        return response is not None
   
    def _send_data(self, address, function_code, data):
        frame = bytearray([address, function_code]) + data
        frame += self._calculate_crc(frame)
        print("Send: ", frame.hex())
        self.uart.write(frame)

    def _receive_data(self, address, function_code, expected_length):
        start_time = time.time()
        response = bytearray()

        while len(response) < expected_length:
            if time.time() - start_time > self.RESPONSE_TIMEOUT:
                print("Timeout while waiting for response")
                return None

            bytes_waiting = self.uart.in_waiting
            if bytes_waiting > 0:
                response += self.uart.read(bytes_waiting)
            else:
                time.sleep(0.01) 
        
        print(response.hex())
        
        if len(response) < expected_length:
            print("Wrong response length") 
            return None

        if response[self.ADDRESS_INDEX] != address or response[self.FUNCTION_CODE_INDEX] != function_code:
            print("Wrong response address")
            return None

        if function_code in [self.MODBUS_READ_HOLDING_REGISTERS, self.MODBUS_READ_INPUT_REGISTERS, self.MODBUS_READ_COILS, self.MODBUS_READ_DISCRETE_INPUTS]:
            data_length = response[self.DATA_LENGTH_INDEX]
            if len(response) != data_length + self.HEADER_LENGTH + self.CRC_LENGTH:
                print("Wrong response data length")
                return None
            data = response[self.DATA_START_INDEX:self.DATA_START_INDEX+data_length]
        else:
            if len(response) != self.WRITE_RESPONSE_LENGTH:
                print("Wrong response data length")
                return None
            data = response[self.WRITE_RESPONSE_DATA_START_INDEX:self.WRITE_RESPONSE_DATA_END_INDEX]

        received_crc = response[-self.CRC_LENGTH:]
        if received_crc != self._calculate_crc(response[:-self.CRC_LENGTH]):
            print("Wrong response crc")
            return None

        return data

    def _calculate_crc(self, msg):
        crc = 0xFFFF
        for byte in msg:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc.to_bytes(2, 'little')
