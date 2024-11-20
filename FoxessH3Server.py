import os
import sys
import logging
import getopt
import json
import time
import queue
from configparser import ConfigParser
import logging.handlers as Handlers
from threading import Thread
import env_substitution
import FlaskServer
#from FlaskServer import app
#from FlaskServer import werteSpeicher
from ModbusWorker import ModbusWorker
from AnswerWorker import AnswerWorker
from InquiryWorker import InquiryWorker
from HomematicMapper import HomematicMapper
from ModbusHomematicHandler import ModbusHomematicHandler
import Constants

def readConfigFileH3(configFile):
    with open(configFile, 'r', encoding='utf-8') as file:
        foxess_json_data = json.load(file)
    port = env_substitution.substitute_env_variables(foxess_json_data[Constants.PORT])
    baudrate = env_substitution.substitute_env_variables(foxess_json_data[Constants.BAUDRATE])
    bytesize = env_substitution.substitute_env_variables(foxess_json_data[Constants.BYTESIZE])
    stopbits = env_substitution.substitute_env_variables(foxess_json_data[Constants.STOPBITS])
    parity = env_substitution.substitute_env_variables(foxess_json_data[Constants.PARITY])
    if port and baudrate and bytesize and stopbits and parity:
        ## Iterate ofer all sensors
        sensors = dict()
        for sensor in foxess_json_data[Constants.SENSORS]:
            key = sensor[Constants.UNIQUE_ID]
            werte = dict()
            werte[Constants.SCALE] = 1
            werte[Constants.PRECISION] = 1
            werte[Constants.UNIT_OF_MEASUREMENT] = ''
            werte[Constants.DEVICE_CLASS] = ''
            werte[Constants.COUNT] = 1
            for s_key in [Constants.NAME, Constants.UNIQUE_ID, Constants.ADDRESS, Constants.SLAVE, Constants.COUNT, Constants.UNIT_OF_MEASUREMENT, Constants.DATA_TYPE, Constants.SCALE, Constants.PRECISION, Constants.SCAN_INTERVAL, Constants.SCAN_OFFSET, Constants.STATE_CLASS, Constants.INPUT_TYPE, Constants.DEVICE_CLASS, Constants.ERROR_BITS, Constants.VALUES]:
                if s_key in sensor.keys():
                    werte[s_key] = sensor[s_key]
                else:
                    #print(s_key, 'wurde nicht gefunden für', key)
                    None
            if werte[Constants.DEVICE_CLASS] == Constants.DEVICE_CLASS_ERROR:
                errorbits = dict()
                if Constants.ERROR_BITS in sensor.keys():
                    for bit in sensor[Constants.ERROR_BITS]:
                        bit_number = bit[Constants.BIT]
                        error = dict()
                        error[Constants.BIT] = bit_number
                        for e_key in [Constants.SEVERITY, Constants.FAULT_MESSAGE]:
                            if e_key in bit.keys():
                                error[e_key] = bit[e_key]
                            else:
                                error[e_key] = Constants.NO_ERROR
                        errorbits[bit_number] = error
                    werte[Constants.ERROR_BITS] = errorbits
                else:
                    print('Für {0} sind keine Errorbits definiert'.format(key))
                werte[Constants.ERROR_BITS] = errorbits
            elif werte[Constants.DEVICE_CLASS] == Constants.DEVICE_CLASS_GIVEN:
                given_values = dict()
                if Constants.VALUES in sensor.keys():
                    for values in sensor[Constants.VALUES]:
                        given_values[values[Constants.VALUE]] = values[Constants.MEANING]
                werte[Constants.VALUES] = given_values
            sensors[key] = werte  
        return port, baudrate, bytesize, stopbits, parity, sensors

    else:
        print('Config does not have all values for the installation')

def help():
    print('FoxessH3Server.py -c <configFile>')
    print('Option -c: Name der Konfigurationsdatei')
    sys.exit()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        help()
    opts, args = getopt.getopt(sys.argv[1:], 'h, c:', ['config='])
    configDatei = None
    for opt, arg in opts:
        if opt == '-h':
            help()
        elif opt in ('-c', '--config'):
            configDatei = arg
    config = ConfigParser()
    config.optionxform=str
    config.read(configDatei)
    ## Get logging-Parameter
    logLevel={'NOTSET': logging.NOTSET, 'DEBUG' : logging.DEBUG, 'INFO' : logging.INFO, 'WARNING' : logging.WARNING, 'ERROR' : logging.ERROR, 'CRITICAL' : logging.CRITICAL}[config.get('Logging', 'Loglevel', fallback='INFO')]
    logMaxFileSize=config.getint('Logging', 'MaxFileSize', fallback=1024)
    # Get CCU-Info
    os.environ['CCU_Address'] = config.get('CCU', 'CCU_Address')
    os.environ['CCU_Port'] = config.get('CCU', 'CCU_Port')
    os.environ['CCU_User'] = config.get('CCU', 'CCU_User')
    os.environ['CCU_Password'] = config.get('CCU', 'CCU_Password')
    # Get Foxess-Info
    os.environ['Port'] = config.get('Foxess', 'Port')
    os.environ['Baudrate'] = config.get('Foxess', 'Baudrate')
    os.environ['Bytesize'] = config.get('Foxess', 'Bytesize')
    os.environ['Stopbits'] = config.get('Foxess', 'Stopbits')
    os.environ['Parity'] = config.get('Foxess', 'Parity')
    
    ## Queues anlegen
    auftrags_queue = queue.Queue()
    antwort_queue = queue.Queue()
    # Modbus Parameter lesen
    port, baudrate, bytesize, stopbits, parity, sensors = readConfigFileH3(config.get('Foxess', 'Configuration'))
    ## modbus Worker einrichten und starten
    modbusWorker = ModbusWorker(port, baudrate, bytesize, stopbits, parity, auftrags_queue, antwort_queue, logLevel, logMaxFileSize)
    modbusWorker.start()
    
    ## Answer Worker einrichten und starten
    answerWorker = AnswerWorker(antwort_queue, FlaskServer.werteSpeicher, logLevel, logMaxFileSize)
    homematicHandler = ModbusHomematicHandler(config.get('Homematic', 'Mapping'))
    answerWorker.addHandler(homematicHandler)
    answerWorker.start()

    # InquiriyWorker
    inquiryWorker = InquiryWorker(auftrags_queue, int(config.getint('Run', 'ScanInterval')), sensors, config.get('Run', 'StopFile'), logLevel, logMaxFileSize)
    inquiryWorker.start()

    # Homematic Mapper
    FlaskServer.homematicMapper = HomematicMapper(config.get('Homematic', 'Status'))

    # Webserver starten
    flaskThread = Thread(target=lambda: FlaskServer.app.run(host=config.get('Webserver', 'Address'), port=config.getint('Webserver', 'Port'), debug=True, use_reloader=False))
    flaskThread.setDaemon(True)
    flaskThread.start()
    
    # Warte auf Ende
    inquiryWorker.join()
    modbusWorker.join()
    answerWorker.join()
