import abc
import os
import json
import logging
import logging.handlers
from datetime import datetime
from datetime import timedelta
import xml.etree.ElementTree as ET
import env_substitution
import Constants

from ModbusHandlerInterface import ModbusHandlerInterface

class ModbusDailyHandler(ModbusHandlerInterface):
    ## Ablageformat
    # {
    #   'YYYYMMDD' : {
    #                  'unique_id' : {
    #                                  'value' : 'wert',
    #                                  'unit_of_measurement' : 'uom'
    #                }
    # }
    _log = logging.getLogger(__name__)
    def __init__(self, configFile, loglevel=logging.INFO, log_maxbytesize=4*1024):
        self._log.setLevel(loglevel)
        log_handler = logging.handlers.RotatingFileHandler('logging/modbusDailyHandler.log', maxBytes=log_maxbytesize)
        log_formatter = logging.Formatter("%(asctime)s %(levelname)-5s %(module)s:%(lineno)s %(message)s")
        log_handler.setFormatter(log_formatter)
        self._log.addHandler(log_handler)
        self._stored_data = dict()
        self.readConfig(configFile)
        self.read_stored_data()

    def readConfig(self, configFile):
        self._log.info(f'readConfig({configFile})')
        with open(configFile, 'r', encoding='utf-8') as file:
            configuration = json.load(file)
            self._dateiname = configuration[Constants.DAILY_LIST_FILE]
            self._liste = configuration[Constants.DAILY_LIST_ITEMS]

    def read_stored_data(self):
        self._log.info(f'read_stored_data({self._dateiname})')
        if os.path.isfile(self._dateiname):
            with open(self._dateiname, 'r', encoding='utf-8') as file:
                self._stored_data = json.load(file)

    def write_stored_data(self):
        with open(self._dateiname, 'w', encoding='utf-8') as file:
            json.dump(self._stored_data, file, indent=3)

    def doHandleItem(self, item):
        uniqueId = item[Constants.UNIQUE_ID]
        if uniqueId in self._liste and Constants.VALUE in item.keys():
            datum = item[Constants.TIMESTAMP].strftime('%Y%m%d')
            werte_zum_datum = dict()
            if datum in self._stored_data.keys():
                werte_zum_datum = self._stored_data[datum]
            werte_zur_unique_id = dict()
            if uniqueId in werte_zum_datum.keys():
                werte_zur_unique_id = werte_zum_datum[uniqueId]
            else:
                werte_zur_unique_id[Constants.NAME] = item[Constants.NAME]
                if Constants.UNIT_OF_MEASUREMENT in item.keys():
                    werte_zur_unique_id[Constants.UNIT_OF_MEASUREMENT] = item[Constants.UNIT_OF_MEASUREMENT]
                else:
                    werte_zur_unique_id[Constants.UNIT_OF_MEASUREMENT] = ''
            werte_zur_unique_id[Constants.VALUE] = item[Constants.VALUE]
            werte_zum_datum[uniqueId] = werte_zur_unique_id
            self._stored_data[datum] = werte_zum_datum
            self.write_stored_data()
            return True
        else:
            return False

    def readListe(self, datum=None, uniqueId=None):
        self._log.info('readListe()')
        if datum:
            if datum in self._stored_data.keys():
                werte_zum_datum = self._stored_data[datum]
                if uniqueId:
                    if uniqueId in werte_zum_datum.keys():
                        return werte_zum_datum[uniqueId]
                    else:
                        return None
                else:
                    return werte_zum_datum
            else:
                return None
        else:
            return self._stored_data

if __name__ == '__main__':
    dateiname = './Modbus-Daily.json'
    dailyHandler = ModbusDailyHandler(dateiname)

    # Modell name
    print(dailyHandler.doHandleItem({ Constants.NAME: 'Inverter Model',
                                          Constants.UNIQUE_ID: 'foxess_inv1_model',
                                          'scan_interval': 600,
                                          'slave': 247,
                                          'address': 30000,
                                          'count': 16,
                                          'state_class': 'measurement',
                                          'data_type': 'string',
                                          'input_type': 'holding',
                                          Constants.VALUE: 'Foxess H3',
                                          'timestamp': datetime.now()
                                        }))
    print(dailyHandler.doHandleItem({ Constants.NAME: 'Today Meter Feed-in Energy',
                                          Constants.UNIQUE_ID: 'foxess_sm1_daily_feedin_energy',
                                          'scan_interval': 60,
                                          'slave': 247,
                                          'address': 32011,
                                          'state_class': 'total_increasing',
                                          'unit_of_measurement': 'kWh',
                                          'scale': 0.1,
                                          'precision': 1,
                                          'data_type': 'int16',
                                          'input_type': 'holding',
                                          'device_class': 'energy',
                                          Constants.VALUE: 4567.8,
                                          'timestamp': datetime.now() - timedelta(days=1)
                                        }))
    print(dailyHandler.doHandleItem({ Constants.NAME: 'Today Meter Feed-in Energy',
                                          Constants.UNIQUE_ID: 'foxess_sm1_daily_feedin_energy',
                                          'scan_interval': 60,
                                          'slave': 247,
                                          'address': 32011,
                                          'state_class': 'total_increasing',
                                          'unit_of_measurement': 'kWh',
                                          'scale': 0.1,
                                          'precision': 1,
                                          'data_type': 'int16',
                                          'input_type': 'holding',
                                          'device_class': 'energy',
                                          Constants.VALUE: 3456.7,
                                          'timestamp': datetime.now()
                                        }))
    print(dailyHandler.doHandleItem({ Constants.NAME: 'Today Inv Load Energy',
                                          Constants.UNIQUE_ID: 'foxess_inv1_daily_load_energy',
                                          'scan_interval': 60,
                                          'slave': 247,
                                          'address': 32023,
                                          'state_class': 'total_increasing',
                                          'unit_of_measurement': 'kWh',
                                          'scale': 0.1,
                                          'precision': 1,
                                          'data_type': 'int16',
                                          'input_type': 'holding',
                                          'device_class': 'energy',
                                          Constants.VALUE: 64357,
                                          'timestamp': datetime.now()
                                        }))
    print(dailyHandler.readListe())
    print(dailyHandler.readListe(datetime.now().strftime('%Y%m%d')))
    print(dailyHandler.readListe(datetime.now().strftime('%Y%m%d'), 'foxess_inv1_daily_load_energy'))
