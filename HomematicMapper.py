import abc
import json
import Constants
from HomematicBasis import HomematicBasis

class HomematicMapper:

    def __init__(self, configFile):
        with open(configFile, 'r', encoding='utf-8') as file:
            configuration = json.load(file)
            address = configuration[Constants.CCU_ADDRESS]
            port = configuration[Constants.CCU_PORT]
            user = configuration[Constants.CCU_USER]
            password = configuration[Constants.CCU_PASSWORD]
            self._homematicBasis = HomematicBasis (address, port, user, password)
            self._devices = dict()
            for device in configuration[Constants.CCU_HOMEMATIC_STATUS]:
                key = device[Constants.UNIQUE_ID]
                werte = dict()
                werte[Constants.UNIT_OF_MEASUREMENT] = ''
                for s_key in [Constants.NAME, Constants.UNIQUE_ID, Constants.ADDRESS, Constants.DATA_TYPE, Constants.SCALE, Constants.PRECISION, Constants.UNIT_OF_MEASUREMENT, Constants.DEVICE_CLASS, Constants.VALUES]:
                    if s_key in device.keys():
                        werte[s_key] = device[s_key]
                    else:
                        #print(s_key, 'wurde nicht gefunden für', key)
                        None
                if Constants.VALUES in werte.keys():
                    given_values = dict()
                    for values in werte[Constants.VALUES]:
                        given_values[values[Constants.VALUE]] = values[Constants.MEANING]
                    werte[Constants.VALUES] = given_values
                #print(werte)
                self._devices[key] = werte

    def doReadHomematic(self, uniqueId):
        if uniqueId in self._devices.keys():
            device = self._devices[uniqueId]
            device[Constants.VALUE] = ''
            if Constants.PRECISION in device.keys():
                precision = device[Constants.PRECISION]
            else:
                precision = 1
            if Constants.SCALE in device.keys():
                scale = device[Constants.SCALE]
            else:
                scale = 1
            if device[Constants.DEVICE_CLASS] == Constants.DEVICE_CLASS_DATA_POINT:
                ergebnis = self._homematicBasis.getDPValue(device[Constants.ADDRESS])
                if Constants.DATA_TYPE in device.keys() and device[Constants.DATA_TYPE] == 'float':
                    device[Constants.VALUE] = round(float(ergebnis) * scale, precision)
                elif Constants.VALUES in device.keys():
                    allValues = device[Constants.VALUES]
                    if ergebnis in allValues.keys():
                        device[Constants.VALUE] = allValues[ergebnis]
                else:
                    device[Constants.VALUE] = ergebnis
        else:
            device = None
        return device

if __name__ == '__main__':
    dateiname = 'C:\\Users\\christoph\\Modbus\\Homematic-Mapping.json'
    #dateiname = 'H:\\Entwicklung\\Homematic\\Homematic-Mapping.json'
    homematicMapper = HomematicMapper(dateiname)
    print(homematicMapper.doReadHomematic('rollade_dg_suedfenster_o'))
    print(homematicMapper.doReadHomematic('temp_eg_kueche'))
    print(homematicMapper.doReadHomematic('feuchte_eg_wohnzimmer'))
    print(homematicMapper.doReadHomematic('strom_bezug_total'))
    print(homematicMapper.doReadHomematic('wc_fenster'))
    print(homematicMapper.doReadHomematic('garagentor'))
    print(homematicMapper.doReadHomematic('mess_steckdose'))
    