import logging
import logging.handlers
import pymodbus.client as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from pymodbus import (
    ModbusException,
    FramerType,
    pymodbus_apply_logging_config,
)

class ModbusReader:
    _log = logging.getLogger(__name__)
    def __init__(self, port, baudrate, bytesize, stopbits, parity, loglevel=logging.INFO, log_maxbytesize=4*1024):
        self._log.setLevel(loglevel)
        log_handler = logging.handlers.RotatingFileHandler('modbusReader.log', maxBytes=log_maxbytesize)
        log_formatter = logging.Formatter("%(asctime)s %(levelname)-5s %(module)s:%(lineno)s %(message)s")
        log_handler.setFormatter(log_formatter)
        self._log.addHandler(log_handler)

        log = logging.getLogger('pymodbus.logging')
        log.setLevel(loglevel)
        log_handler = logging.handlers.RotatingFileHandler('modbusClient.log', maxBytes=log_maxbytesize)
        log_formatter = logging.Formatter("%(asctime)s %(levelname)-5s %(module)s:%(lineno)s %(message)s")
        log_handler.setFormatter(log_formatter)
        log.addHandler(log_handler)
        self._client = ModbusClient.ModbusSerialClient(
            port,
            framer=FramerType.RTU,
            baudrate=baudrate,
            bytesize=bytesize,
            stopbits=stopbits,
            parity=parity,
            timeout=2,
            # retries=3,
            # handle_local_echo=False,
        )
        self._client.connect()

    def restart(self):
        self._log.warning('Restart requested')
        self._client.close()
        self._client.connect()

    def close(self):
        self._log.info('Close')
        self._client.close()

    def readRegister(self, register, slave, data_type='uint16', length=1):
        self._log.info('Read Register {0}'.format(register))
        try:
            reg_read = self._client.read_holding_registers(register, count=length, slave=slave)
        except ModbusException as exc:
            self._log.error('Error reading Register {0}: {1}'.format(register, exc))
            raise exc
        if reg_read.isError():
            self._log.error('Error reg_read for Register {0}'.format(register))
            raise ModbusException(f"Fehler im Register {register}")
        if data_type=='string':
            decoder = BinaryPayloadDecoder.fromRegisters(reg_read.registers, byteorder=Endian.BIG, wordorder=Endian.LITTLE)
            return str(decoder.decode_string(size=length), encoding='utf-8')
        else:
            decoder = BinaryPayloadDecoder.fromRegisters(reg_read.registers, byteorder=Endian.BIG, wordorder=Endian.BIG)
            if data_type=='int32':
                print(reg_read.registers)
                return decoder.decode_32bit_int()
            elif data_type=='uint32':
                return decoder.decode_32bit_uint()
            elif data_type=='int16':
                return decoder.decode_16bit_int()
            else:
                return decoder.decode_16bit_uint()

if __name__ == '__main__':
    slave=0xF7
    modbusReader = ModbusReader('COM4', 9600, 8, 1, 'N')
    print(modbusReader.readRegister(30000, slave, 'string', 16))
    #print(modbusReader.readRegister(31002, slave))
    #modbusReader.restart()
    print(modbusReader.readRegister(31015, slave, 'int16'))
    #print(modbusReader.readRegister(30000, slave, 'string', 18))
    modbusReader.close()
