import logging
import logging.handlers as Handlers
import time
import os
import os.path
from datetime import datetime
from queue import Queue
from threading import Thread
import Constants

class InquiryWorker(Thread):
    _log = logging.getLogger(__name__)
    
    def __init__(self, anfrage_queue, scan_interval, sensors, ende_datei, loglevel=logging.INFO, log_maxbytesize=4*1024):
        Thread.__init__(self)
        ## eigenes Logging
        self._log.setLevel(loglevel)
        log_handler = logging.handlers.RotatingFileHandler('inquiryWorker.log', maxBytes=log_maxbytesize)
        log_formatter = logging.Formatter("%(asctime)s %(levelname)-5s %(module)s:%(lineno)s %(message)s")
        log_handler.setFormatter(log_formatter)
        self._log.addHandler(log_handler)
        ## Queues merken
        self._anfrageQueue = anfrage_queue
        self._scan_interval = scan_interval
        self._sensors = sensors
        self._ende_datei = ende_datei
        self._log.info('InquiryWorker initiated')

    def run(self):
        isRunning = True
        self._log.info('InquiryWorker starts running')
        # Initialisierung
        for k in self._sensors.keys():
            if Constants.SCAN_INTERVAL not in self._sensors[k].keys():
                self._log.warning('UniqueId {0} has no scan_interval.'.format(k))
                self._sensors[k][Constants.SCAN_INTERVAL] = 300
            if Constants.SCAN_OFFSET in self._sensors[k].keys():
                self._sensors[k][Constants.ACTUAL_TIMER] = self._sensors[k][Constants.SCAN_OFFSET]
            else:
                self._sensors[k][Constants.ACTUAL_TIMER] = 0
        # Lauf
        while isRunning:
            for k in self._sensors.keys():
                actual_timer = int(self._sensors[k][Constants.ACTUAL_TIMER])
                if actual_timer <= 0:
                    actual_timer = self._sensors[k][Constants.SCAN_INTERVAL]
                    self._log.info('UniqueId {0} put in queue.'.format(k))
                    self._anfrageQueue.put(self._sensors[k].copy())
                else:
                    actual_timer -= self._scan_interval
                self._sensors[k][Constants.ACTUAL_TIMER] = actual_timer
            time.sleep(self._scan_interval)
            isRunning = not os.path.isfile(self._ende_datei)
        self._anfrageQueue.put(Constants.STOP)
        os.remove(self._ende_datei)


if __name__ == '__main__':
    anfrageQueue = Queue()
    sensors = { 'foxess_inv1_model' : { Constants.NAME: 'Inverter Model',
                       Constants.UNIQUE_ID: 'foxess_inv1_model',
                       Constants.SCAN_INTERVAL: 600,
                       Constants.SLAVE: 247,
                       Constants.ADDRESS: 30000,
                       Constants.COUNT: 16,
                       Constants.STATE_CLASS: 'measurement',
                       Constants.DATA_TYPE: 'string',
                       Constants.INPUT_TYPE: 'holding'
                     }, 
                'foxess_inv1_pv1_current' : { Constants.NAME: 'PV1-Current',
                       Constants.UNIQUE_ID: 'foxess_inv1_pv1_current',
                       Constants.SLAVE: 247,
                       Constants.ADDRESS: 31001,
                       Constants.SCAN_INTERVAL: 90,
                       Constants.STATE_CLASS: 'measurement',
                       Constants.UNIT_OF_MEASUREMENT: 'A',
                       Constants.DATA_TYPE: 'int16',
                       Constants.SCALE: 0.1,
                       Constants.PRECISION: 1,
                       Constants.DEVICE_CLASS: 'current'
                },
                'foxess_inv1_avail_import_power' : { Constants.NAME: 'Available import power',
                       Constants.UNIQUE_ID: 'foxess_inv1_avail_import_power',
                       Constants.DATA_TYPE: 'uint32',
                       Constants.UNIT_OF_MEASUREMENT: 'W',
                       Constants.SCALE: 1,
                       Constants.PRECISION: 1,
                       Constants.SCAN_INTERVAL: 30,
                       Constants.SLAVE: 247,
                       Constants.ADDRESS: 31092,
                       Constants.COUNT: 2,
                       Constants.INPUT_TYPE: 'holding',
                       Constants.DEVICE_CLASS: 'power'
                },
                'foxess_inv1_fault1_code' : {  Constants.NAME: 'Inverter Fault 1 Code',
                        Constants.UNIQUE_ID: 'foxess_inv1_fault1_code',
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
                }
              }
    
    
    inquiryWorker = InquiryWorker(anfrageQueue, sensors)
    inquiryWorker.run()
    isRunning = True
    while isRunning:
        item = anfrageQueue.get()
        if isinstance(item, str) and item == Constants.STOP:
            isRunning = False
        else:
            print('<--', item[Constants.UNIQUE_ID])
        anfrageQueue.task_done()
