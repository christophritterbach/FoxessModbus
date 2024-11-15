import abc
import base64
import requests
import json
from datetime import datetime
import xml.etree.ElementTree as ET
import Constants

from ModbusHandlerInterface import ModbusHandlerInterface

class ModbusHomematicHandler(ModbusHandlerInterface):
    def __init__(self, configFile):
        with open(configFile, 'r', encoding='utf-8') as file:
            configuration = json.load(file)
            self._address = configuration[Constants.CCU_ADDRESS]
            self._port = configuration[Constants.CCU_PORT]
            user = configuration[Constants.CCU_USER]
            password = configuration[Constants.CCU_PASSWORD]
            self._authorization_header = 'Basic ' + base64.b64encode('{0}:{1}'.format(user, password).encode('ascii')).decode('ascii')
            self._mapping = configuration[Constants.CCU_MAPPINGS]

    def doHandleItem(self, item):
        uniqueId = item[Constants.UNIQUE_ID]
        if uniqueId in self._mapping and Constants.VALUE in item.keys():
            value = item[Constants.VALUE]
            if Constants.ERROR_BITS in item.keys() and value > 0:
                print (item[Constants.ERROR_BITS])
                fehlercodes = ''
                for k, v in item[Constants.ERROR_BITS].items():
                    if value & (1 << k):
                        if len(fehlercodes) > 0:
                            fehlercodes += ', '
                        meldung = v[Constants.FAULT_MESSAGE]
                        if v[Constants.FAULT_MESSAGE] == Constants.NO_ERROR:
                            fehlercodes += 'Bit {0} ohne Definition'. format(k, v[Constants.SEVERITY])
                        else:
                            fehlercodes += '{0} ({1})'.format(meldung, v[Constants.SEVERITY])
                value = fehlercodes
            ccu_variable = self._mapping[uniqueId]
            anfrage='http://{0}:{1}/HM.exe?Status=dom.GetObject("{2}").State("{3}")'.format(self._address, self._port, ccu_variable, value)
            response=requests.get(anfrage, headers ={'Authorization': self._authorization_header})
            return response.ok
        else:
            return False

if __name__ == '__main__':
    dateiname = './Modbus-Homematic-Mapping.json'
    homematicHandler = ModbusHomematicHandler(dateiname)
    
    # Modell name
    print(homematicHandler.doHandleItem({ Constants.NAME: 'Inverter Model',
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
    ## MPPT1 
    print(homematicHandler.doHandleItem({ Constants.NAME: 'PV1-Power',
                                          Constants.UNIQUE_ID: 'foxess_inv1_pv1_power',
                                          'scan_interval': 30,
                                          'slave': 247,
                                          'address': 31002,
                                          'state_class': 'measurement',
                                          'unit_of_measurement': 'W',
                                          'data_type': 'int16',
                                          'scale': 1,
                                          'precision': 0,
                                          'input_type': 'holding',
                                          'device_class': 'power',
                                          Constants.VALUE: 22,
                                          'timestamp': datetime.now()
                                        }))
    print(homematicHandler.doHandleItem({ Constants.NAME: 'PV2-Power',
                                          Constants.UNIQUE_ID: 'foxess_inv1_pv2_power',
                                          'scan_interval': 30,
                                          'slave': 247,
                                          'address': 31002,
                                          'state_class': 'measurement',
                                          'unit_of_measurement': 'W',
                                          'data_type': 'int16',
                                          'scale': 1,
                                          'precision': 0,
                                          'input_type': 'holding',
                                          'device_class': 'power',
                                          Constants.VALUE: 21,
                                          'timestamp': datetime.now()
                                        }))
    print(homematicHandler.doHandleItem({ Constants.NAME: 'Today Meter Feed-in Energy',
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
