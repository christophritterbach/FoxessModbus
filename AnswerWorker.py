import logging
import logging.handlers as Handlers
from datetime import datetime
from queue import Queue
from threading import Thread
from ModbusHomematicHandler import ModbusHomematicHandler
import json
import Constants

class AnswerWorker(Thread):
    _log = logging.getLogger(__name__)
    _handlers = []

    def __init__(self, antwort_queue, loglevel=logging.INFO, log_maxbytesize=4*1024):
        Thread.__init__(self)
        ## eigenes Logging
        self._log.setLevel(loglevel)
        log_handler = logging.handlers.RotatingFileHandler('logging/answerWorker.log', maxBytes=log_maxbytesize)
        log_formatter = logging.Formatter("%(asctime)s %(levelname)-5s %(module)s:%(lineno)s %(message)s")
        log_handler.setFormatter(log_formatter)
        self._log.addHandler(log_handler)
        ## Queues merken
        self._antwortQueue = antwort_queue
        ## Datenspeicher (DICT) ablegen
        self._datenSpeicher = dict()
        self._log.info('AnswerWorker initiated')

    def addHandler(self, handler):
        self._handlers.append(handler)

    def getMeaningFromGivenValue(self, item):
        aktuellerWert = item[Constants.VALUE]
        if Constants.DEVICE_CLASS_GIVEN == item[Constants.DEVICE_CLASS] and Constants.VALUES in item.keys():
            allValues = item[Constants.VALUES]
            if aktuellerWert in allValues.keys():
                aktuellerWert = allValues[aktuellerWert]
            else:
                self._log.debug('ID: {0}, GIVEN_VALUE nicht definiert fuer {1}'.format(item[Constants.UNIQUE_ID], aktuellerWert))
        elif Constants.DEVICE_CLASS_BATTERY_VERSION == item[Constants.DEVICE_CLASS]:
            zahlen = []
            for i in range (0, 4):
                zahlen.append((aktuellerWert >> (i*4)) & 0x000F)
            aktuellerWert = f"{zahlen[3]:02d}.{zahlen[2]:02d}.{zahlen[1]:02d}.{zahlen[0]:02d}"

        return aktuellerWert

    def run(self):
        isRunning = True
        self._log.info('AnswerWorker starts running')
        while isRunning:
            item = self._antwortQueue.get()
            if isinstance(item, str) and item == Constants.STOP:
                self._log.info('STOP received')
                isRunning = False
            else:
                doHandleItem = False
                uniqueId = item[Constants.UNIQUE_ID]
                self._log.debug('Get data for UniqueId: {0}'.format(uniqueId))
                aktuellerWert = self.getMeaningFromGivenValue(item)
                if item[Constants.DEVICE_CLASS] in [Constants.DEVICE_CLASS_GIVEN, Constants.DEVICE_CLASS_BATTERY_VERSION]:
                    item[Constants.VALUE] = aktuellerWert
                if uniqueId in self._datenSpeicher.keys():
                    letzterWert = self._datenSpeicher[uniqueId][Constants.VALUE]
                    self._log.debug('ID: {0}, letzter: {1}, aktueller {2}'.format(uniqueId, letzterWert, aktuellerWert))
                    if aktuellerWert != letzterWert:
                        self._datenSpeicher.update({uniqueId: item})
                        doHandleItem = True
                else:
                    self._log.debug('neue ID: {0}'.format(uniqueId))
                    self._datenSpeicher[uniqueId] = item
                    doHandleItem = True
                if doHandleItem:
                    for handler in self._handlers:
                        handler.doHandleItem(item)

            self._antwortQueue.task_done()

    def readDatenspeicher(self, uniqueId=None):
        if self._datenSpeicher:
            if uniqueId:
                if uniqueId in self._datenSpeicher.keys():
                    return self._datenSpeicher[uniqueId]
                else:
                    return None
            else:
                return self._datenSpeicher
        else:
            return None

if __name__ == '__main__':
    antwortQueue = Queue()
    speicher = dict()
    answerWorker = AnswerWorker(antwortQueue, speicher)
    configurations_datei_Homematic = './Modbus-Homematic-Mapping.json'
    homematicHandler = ModbusHomematicHandler(configurations_datei_Homematic)
    answerWorker.addHandler(homematicHandler)


    antwortQueue.put({ Constants.NAME: 'Inverter Model',
                       Constants.UNIQUE_ID: 'foxess_inv1_model',
                       Constants.SCAN_INTERVAL: 600,
                       Constants.SLAVE: 247,
                       Constants.ADDRESS: 30000,
                       Constants.COUNT: 16,
                       Constants.STATE_CLASS: 'measurement',
                       Constants.DATA_TYPE: 'string',
                       Constants.INPUT_TYPE: 'holding',
                       Constants.VALUE: 'Foxess H3',
                       Constants.DEVICE_CLASS: '',
                       Constants.TIMESTAMP: datetime.now()
                     })
    antwortQueue.put({ Constants.NAME: 'PV1-Power',
                       Constants.UNIQUE_ID: 'foxess_inv1_pv1_power',
                       Constants.SCAN_INTERVAL: 30,
                       Constants.SLAVE: 247,
                       Constants.ADDRESS: 31002,
                       Constants.STATE_CLASS: 'measurement',
                       Constants.UNIT_OF_MEASUREMENT: 'W',
                       Constants.DATA_TYPE: 'int16',
                       Constants.SCALE: 1,
                       Constants.PRECISION: 0,
                       Constants.INPUT_TYPE: 'holding',
                       Constants.DEVICE_CLASS: 'power',
                       Constants.VALUE: 30,
                       Constants.TIMESTAMP: datetime.now()
                     })
    antwortQueue.put({ Constants.NAME: 'Firmware Battery Slave 1',
                       Constants.UNIQUE_ID: 'foxess_bat_slave_1',
                       Constants.SCAN_INTERVAL: 30,
                       Constants.SLAVE: 247,
                       Constants.ADDRESS: 30020,
                       Constants.STATE_CLASS: 'measurement',
                       Constants.DATA_TYPE: 'uint16',
                       Constants.INPUT_TYPE: 'holding',
                       Constants.DEVICE_CLASS: 'power',
                       Constants.VALUE: 4117,
                       Constants.DEVICE_CLASS: 'battery_version',
                       Constants.TIMESTAMP: datetime.now()
                     })
    import time
    time.sleep(2)
    antwortQueue.put({ Constants.NAME: 'PV1-Power',
                       Constants.UNIQUE_ID: 'foxess_inv1_pv1_power',
                       Constants.SCAN_INTERVAL: 30,
                       Constants.SLAVE: 247,
                       Constants.ADDRESS: 31002,
                       Constants.STATE_CLASS: 'measurement',
                       Constants.UNIT_OF_MEASUREMENT: 'W',
                       Constants.DATA_TYPE: 'int16',
                       Constants.SCALE: 1,
                       Constants.PRECISION: 0,
                       Constants.INPUT_TYPE: 'holding',
                       Constants.DEVICE_CLASS: 'power',
                       Constants.VALUE: 35,
                       Constants.TIMESTAMP: datetime.now()
                     })
    antwortQueue.put(Constants.STOP)

    answerWorker.run()

    print ('Im Speicher ist')
    for item in speicher.values():
        print(item)

    print('------------------')
    liste = []
    for item in speicher.values():
        print('---', item)
        entry = dict()
        for k, v in item.items():
            if k in [Constants.NAME, Constants.VALUE, Constants.UNIT_OF_MEASUREMENT, Constants.TIMESTAMP]:
                entry[k] = v
        liste.append(entry)
    print('------------------')
    print(liste)
    def json_serializer(obj):
        if isinstance(obj, (datetime)):
            return obj.strftime("%m.%d.%Y %H:%M:%S")


    print(json.dumps(liste, default=json_serializer))
    print('------------------')
    #print(speicher.values())
    print(json.dumps(list(speicher.values()), default=json_serializer))
