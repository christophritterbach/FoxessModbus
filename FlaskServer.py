from flask import Flask                                                         
from flask import render_template
from datetime import datetime
from HomematicBasis import HomematicBasis
import json
import threading

app = Flask('Foxess H3 Server')
werteSpeicher = dict()
homematicMapper = None

##  Seiten
@app.route("/")
def main():
    return render_template('alle_register.html')

@app.route("/PV")
def pv_ansicht():
    return render_template('pv_ansicht.html')

@app.route("/BAT")
def batterie_ansicht():
    return render_template('batterie.html')

@app.route("/TAG")
def tag_ansicht():
    return render_template('tageswerte.html')

@app.route("/HMIP")
def hmip_ansicht():
    return render_template('homematic.html')

### REST-Aufrufe
def json_serializer(obj):
    if isinstance(obj, (datetime)):
        return obj.strftime("%m.%d.%Y %H:%M:%S")

@app.route("/allSensors")
def allSensors():
    return json.dumps(list(werteSpeicher.values()), default=json_serializer)
    
@app.route("/sensor/<sensor_id>")
def sensorById(sensor_id):
    if sensor_id in werteSpeicher.keys():
        return json.dumps(werteSpeicher[sensor_id], default=json_serializer)
    else:
        return ''

@app.route("/homematic/<object_id>")
def sendHomematic(object_id):
    temp = homematicMapper.doReadHomematic(object_id)
    return json.dumps(temp, default=json_serializer)

# Für Testaufrufe    
def fuelle_wertespeicher():
    wertespeicher['foxess_inv1_model'] = { Constants.NAME: 'Inverter Model',
                       Constants.UNIQUE_ID: 'foxess_inv1_model',
                       Constants.SCAN_INTERVAL: 600,
                       Constants.SLAVE: 247,
                       Constants.ADDRESS: 30000,
                       Constants.COUNT: 16,
                       Constants.STATE_CLASS: 'measurement',
                       Constants.DATA_TYPE: 'string',
                       Constants.INPUT_TYPE: 'holding',
                       Constants.VALUE: 'Foxess H3',
                       Constants.TIMESTAMP: datetime.now()
                     }
    wertespeicher['foxess_inv1_pv1_power'] = { Constants.NAME: 'PV1-Power',
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
                     }
if __name__ == "__main__":
    host_name = '0.0.0.0'
    port = 8180
    global homematicBasis
    homematicBasis = HomematicBasis ('localhost', 8181, 'user', 'password')
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()
