from flask import Flask
from flask import render_template
from datetime import datetime
from HomematicBasis import HomematicBasis
from AnswerWorker import AnswerWorker
from ModbusDailyHandler import ModbusDailyHandler
import json
import threading

app = Flask('Foxess H3 Server')
homematicMapper = None
dailyHandler = None
answerWorker = None

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

@app.route("/VERLAUF")
def mehrere_tage_ansicht():
    return render_template('verlaufswerte.html')

@app.route("/HMIP")
def hmip_ansicht():
    return render_template('homematic.html')

### REST-Aufrufe
def json_serializer(obj):
    if isinstance(obj, (datetime)):
        return obj.strftime("%m.%d.%Y %H:%M:%S")

@app.route("/allFoxess")
def allFoxessSensors():
    daten = answerWorker.readDatenspeicher()
    if daten:
        return json.dumps(list(daten.values()), default=json_serializer)
    else:
        return ''

@app.route("/allFoxessDaily")
def allFoxessDaily():
    daten = dailyHandler.readListe()
    if daten:
        return json.dumps(daten)
    else:
        return ''

@app.route("/foxess/<sensor_id>")
def sensorById(sensor_id):
    daten = answerWorker.readDatenspeicher(sensor_id)
    if daten:
        return json.dumps(daten, default=json_serializer)
    else:
        return ''

@app.route("/homematic/<object_id>")
def sendHomematic(object_id):
    temp = homematicMapper.doReadHomematic(object_id)
    return json.dumps(temp, default=json_serializer)

if __name__ == "__main__":
    host_name = '0.0.0.0'
    port = 8180
    global homematicBasis
    homematicBasis = HomematicBasis ('localhost', 8181, 'user', 'password')
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()
