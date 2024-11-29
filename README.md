# FoxessModbus
Read Modbus Registers from Foxess and write it to Homematic

## Übersicht
Dieses Programm ist in der Lage, per Modbus über RS485 Daten aus einem Foxess Wechselrichter (H3) auszulesen und diese Daten
einerseits in einer Webseite darzustellen als auch an eine Homematic CCU zu übertragen.

### Raspberry
Das Programm läuft aktuell auf einem Raspberry Pi, Version 1.

PRETTY_NAME="Raspbian GNU/Linux 12 (bookworm)"
NAME="Raspbian GNU/Linux"
VERSION_ID="12"
VERSION="12 (bookworm)"
VERSION_CODENAME=bookworm

Hardware        : BCM2835
Revision        : 000f
Model           : Raspberry Pi Model B Rev 2

### RS485
Die Kommunikation übernimmt ein USB-Stick, der RS485 auf USB umsetzt.
[ch340 bei Reichelt](https://www.reichelt.de/raspberry-pi-usb-rs485-schnittstelle-ch340c-rpi-usb-rs485-p242783.html)

Es musste kein Treiber manuell installiert werden.

### Python
Python wird in einer eigenen Umgebung eingesetzt.

`python -m venv solar`
`source solar/bin/activate`

#### Bibliotheken
- PyModbus
- pyserial
- flask
- FlaskServer
- Flask
- requests

## Aufbau

### Konfigurationen

