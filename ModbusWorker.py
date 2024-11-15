import logging
import logging.handlers as Handlers
from datetime import datetime
from queue import Queue
from threading import Thread
from ModbusReader import ModbusReader
from pymodbus import ModbusException
import Constants

class ModbusWorker(Thread):
    _log = logging.getLogger(__name__)
    
    def __init__(self, port, baudrate, bytesize, stopbits, parity, anfrage_queue, antwort_queue, loglevel=logging.INFO, log_maxbytesize=4*1024):
        Thread.__init__(self)
        ## eigenes Logging
        self._log.setLevel(loglevel)
        log_handler = logging.handlers.RotatingFileHandler('modbusWorker.log', maxBytes=log_maxbytesize)
        log_formatter = logging.Formatter("%(asctime)s %(levelname)-5s %(module)s:%(lineno)s %(message)s")
        log_handler.setFormatter(log_formatter)
        self._log.addHandler(log_handler)
        ## Modbus vorbereiten
        self._log.info('ModbusReader connected to Port {0} with baudrate {1}'. format(port, baudrate))
        self._modbusReader = ModbusReader(port, baudrate, bytesize, stopbits, parity)
        ## Queues merken
        self._anfrageQueue = anfrage_queue
        self._antwortQueue = antwort_queue
        self._log.info('ModbusWorker initiated')

    def run(self):
        isRunning = True
        self._log.info('ModbusWorker starts running')
        while isRunning:
            item = self._anfrageQueue.get()
            if isinstance(item, str) and item == Constants.STOP:
                self._log.info('STOP received')
                isRunning = False
                self._modbusReader.close()
                self._antwortQueue.put(item)
            else:
                uniqueId  = item[Constants.UNIQUE_ID]
                self._log.debug('get value for unique_id {0}'.format(uniqueId))
                slave     = item[Constants.SLAVE]
                del item[Constants.SLAVE]
                address   = item[Constants.ADDRESS]
                del item[Constants.ADDRESS]
                data_type = item[Constants.DATA_TYPE]
                if Constants.COUNT in item.keys():
                    count = item[Constants.COUNT]
                    del item[Constants.COUNT]
                else:
                    count = 1
                if data_type != 'string':
                    if Constants.PRECISION in item.keys():
                        precision = item[Constants.PRECISION]
                        del item[Constants.PRECISION]
                    else:
                        precision = 1
                    if Constants.SCALE in item.keys():
                        scale = item[Constants.SCALE]
                        del item[Constants.SCALE]
                    else:
                        scale = 1
                try:
                    ergebnis = self._modbusReader.readRegister(address, slave, data_type, count)
                    item[Constants.TIMESTAMP] = datetime.now()
                    if data_type == 'string':
                        item[Constants.VALUE] = ergebnis
                    else:
                        item[Constants.VALUE] = round(ergebnis * scale, precision)
                    self._log.debug('value for unique_id {0} is {1}'.format(uniqueId, item[Constants.VALUE]))
                    self._antwortQueue.put(item)
                except ModbusException as exc:
                    item[Constants.VALUE] = None
                    item['error'] = exc
                    print(f'Die UniqueId {uniqueId} erzeugt Fehler {exc}')
                    self._log.error('error at unique_id ' + uniqueId + ': ' + str(exc))
            self._anfrageQueue.task_done()


if __name__ == '__main__':
    anfrageQueue = Queue()
    antwortQueue = Queue()
    anfrageQueue.put({ Constants.NAME: 'Inverter Model',
                       Constants.UNIQUE_ID: 'foxess_inv1_model',
                       Constants.SCAN_INTERVAL: 600,
                       Constants.SLAVE: 247,
                       Constants.ADDRESS: 30000,
                       Constants.COUNT: 16,
                       Constants.STATE_CLASS: 'measurement',
                       Constants.DATA_TYPE: 'string',
                       Constants.INPUT_TYPE: 'holding'
                     })
    anfrageQueue.put({ Constants.NAME: 'PV1-Current',
                       Constants.UNIQUE_ID: 'foxess_inv1_pv1_current',
                       Constants.SLAVE: 247,
                       Constants.ADDRESS: 31001,
                       Constants.STATE_CLASS: 'measurement',
                       Constants.UNIT_OF_MEASUREMENT: 'A',
                       Constants.DATA_TYPE: 'int16',
                       Constants.SCALE: 0.1,
                       Constants.PRECISION: 1,
                       Constants.DEVICE_CLASS: 'current'
                     })
    anfrageQueue.put({ Constants.NAME: 'Available import power',
                       Constants.UNIQUE_ID: 'foxess_inv1_avail_import_power',
                       Constants.DATA_TYPE: 'uint32',
                       Constants.UNIT_OF_MEASUREMENT: 'W',
                       Constants.SCALE: 1,
                       Constants.PRECISION: 1,
                       Constants.SCAN_INTERVAL: '30',
                       Constants.SLAVE: 247,
                       Constants.ADDRESS: 31092,
                       Constants.COUNT: 2,
                       Constants.INPUT_TYPE: 'holding',
                       Constants.DEVICE_CLASS: 'power'
                     })
    anfrageQueue.put({ Constants.NAME: 'Total Load Power',
                       Constants.UNIQUE_ID: 'foxess_inv1_total_load_power',
                       Constants.DATA_TYPE: 'int32',
                       Constants.UNIT_OF_MEASUREMENT: 'W',
                       Constants.SCALE: 1,
                       Constants.PRECISION: 1,
                       Constants.SCAN_INTERVAL: 30,
                       Constants.SLAVE: 247,
                       Constants.ADDRESS: 31097,
                       Constants.COUNT: 2,
                       Constants.INPUT_TYPE: 'holding',
                       Constants.DEVICE_CLASS: 'power'
                     })
    anfrageQueue.put({ Constants.NAME: 'Cell Temperature High',
                       Constants.UNIQUE_ID: 'foxess_inv1_cell_temp_high',
                       Constants.DATA_TYPE: 'int16',
                       Constants.UNIT_OF_MEASUREMENT: '°C',
                       Constants.SCALE: 0.1,
                       Constants.SCAN_INTERVAL: 30,
                       Constants.SLAVE: 247,
                       Constants.ADDRESS: 31102,
                       Constants.INPUT_TYPE: 'holding',
                       Constants.DEVICE_CLASS: 'temperature'
                     })
    anfrageQueue.put({  Constants.NAME: 'Inverter Fault 1 Code',
                        Constants.UNIQUE_ID: 'foxess_inv1_fault1_code',
                        Constants.SCAN_INTERVAL: 60,
                        Constants.SLAVE: 247,
                        Constants.ADDRESS: 31044,
                        Constants.STATE_CLASS: 'measurement',
                        Constants.DATA_TYPE: 'uint16',
                        Constants.INPUT_TYPE: 'holding',
                        Constants.DEVICE_CLASS: 'error',
                        Constants.ERROR_BITS: [
                            { Constants.BIT: 0, Constants.FAULT_MESSAGE: 'GridLostFault', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 1, Constants.FAULT_MESSAGE: 'GridVoltFault', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 2, Constants.FAULT_MESSAGE: 'GridFreqFault', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 3, Constants.FAULT_MESSAGE: 'Grid10minVoltFault', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 4, Constants.FAULT_MESSAGE: 'PPL_OverTime', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 5, Constants.FAULT_MESSAGE: 'SWInvCurFault', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 6, Constants.FAULT_MESSAGE: 'DciFault', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 7, Constants.FAULT_MESSAGE: 'PhaseAngleFault', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 8, Constants.FAULT_MESSAGE: 'HardwareTrip', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 9, Constants.FAULT_MESSAGE: 'SwBusVoltFault', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 10, Constants.FAULT_MESSAGE: 'BatVoltFault', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 11, Constants.FAULT_MESSAGE: 'SwBatCurFault', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 12, Constants.FAULT_MESSAGE: 'IsoFault', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 13, Constants.FAULT_MESSAGE: 'ResCurFault', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 14, Constants.FAULT_MESSAGE: 'PvVoltFault', Constants.SEVERITY: 'minor' },
                            { Constants.BIT: 15, Constants.FAULT_MESSAGE: 'SwPvCurFault', Constants.SEVERITY: 'minor' }
                        ]
                     })
    anfrageQueue.put({ Constants.NAME: 'Inverter Model',
                       Constants.UNIQUE_ID: 'foxess_inv1_model',
                       Constants.SCAN_INTERVAL: 600,
                       Constants.SLAVE: 247,
                       Constants.ADDRESS: 30000,
                       Constants.COUNT: 18,
                       Constants.STATE_CLASS: 'measurement',
                       Constants.DATA_TYPE: 'string',
                       Constants.INPUT_TYPE: 'holding'
                     })
    print('AnfrageQueue.Size', antwortQueue.qsize())
    anfrageQueue.put(Constants.STOP)
    modbusWorker = ModbusWorker('COM4', 9600, 8, 1, 'N', anfrageQueue, antwortQueue)
    modbusWorker.run()
    
    print('AntwortQueue.Size', antwortQueue.qsize())
    isRunning = True
    while isRunning:
        item = antwortQueue.get()
        if isinstance(item, str) and item == Constants.STOP:
            isRunning = False
        else:
            print('<--', item[Constants.UNIQUE_ID], item[Constants.VALUE], item[Constants.TIMESTAMP].strftime('%H:%M:%S'))
        antwortQueue.task_done()
    print('AntwortQueue.Size', antwortQueue.qsize())

