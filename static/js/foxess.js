function getAllDataFromServer() {
    fetch('allSensors')
        .then((sensor_json) => sensor_json.json())
        .then((sensors) => {
            document.getElementById("all_sensors").innerHTML=""
            for (let sensor of sensors) {
                measurement=''
                if (sensor.hasOwnProperty('unit_of_measurement')) {
                    measurement = sensor.unit_of_measurement
                }
                document.getElementById("all_sensors").innerHTML += `<tr id="${sensor.unique_id}"><td>${sensor.name}</td><td>${sensor.value}</td><td>${measurement}</td></tr>
`;
            }
        });
    }

function leseWertVomServer(unique_id) {
    fetch('sensor/' + unique_id)
        .then((sensor_json) => sensor_json.json())
        .then((sensor) => {
            document.getElementById(unique_id).innerHTML=""
            measurement=''
            wert=sensor.value
            if (sensor.data_type != "string") {
                if (sensor.hasOwnProperty('unit_of_measurement')) {
                    measurement = sensor.unit_of_measurement
                }
                if (sensor.hasOwnProperty('precision')) {
                    precision=sensor.precision-1
                    wert=sensor.value.toFixed(precision)
                } else {
                    wert=sensor.value
                }
            }
            document.getElementById(unique_id).innerHTML = `${wert} ${measurement}`;
        });
}

function leseHmipWertVomServer(unique_id) {
    fetch('homematic/' + unique_id)
        .then((hmip_json) => hmip_json.json())
        .then((hmip) => {
            document.getElementById(unique_id).innerHTML=""
            measurement=''
            wert=hmip.value
            if (hmip.hasOwnProperty('unit_of_measurement')) {
                measurement = hmip.unit_of_measurement
            }
            if (hmip.hasOwnProperty('precision')) {
                precision=hmip.precision-1
                wert=hmip.value.toFixed(precision)
            } else {
                wert=hmip.value
            }
            document.getElementById(unique_id).innerHTML = `${wert} ${measurement}`;
        });
}

function getDataFromServer() {
    var allElements = document.querySelectorAll('*[id]');
    for (let elem of allElements) {
        leseWertVomServer(elem.id);
    }
}

function getHmipDataFromServer() {
    var allElements = document.querySelectorAll('*[id]');
    for (let elem of allElements) {
        leseHmipWertVomServer(elem.id);
    }
}
