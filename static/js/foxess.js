function getAllDataFromServer() {
    fetch('allFoxess')
        .then((sensor_json) => sensor_json.json())
        .then((sensors) => {
            document.getElementById("all_sensors").innerHTML=""
            for (let sensor of sensors) {
                measurement=''
                if (sensor.hasOwnProperty('unit_of_measurement')) {
                    measurement = sensor.unit_of_measurement
                }
                document.getElementById("all_sensors").innerHTML += `<tr class="foxess" id="${sensor.unique_id}"><td style="text-align:left" title="${sensor.unique_id}">${sensor.name}</td><td class="value" style="text-align:right">${sensor.value}</td><td style="text-align:left">${measurement}</td></tr>
`;
            }
        });
    }

function leseWertVomServer(unique_id, quelle) {
    fetch(quelle + '/' + unique_id)
        .then((sensor_json) => sensor_json.json())
        .then((sensor) => {
            console.log(sensor)
            elem=document.getElementById(unique_id)
            wert=sensor.value
            if (sensor.hasOwnProperty('precision') && (sensor.precision > 0)) {
                    precision=sensor.precision-1
                    wert=sensor.value.toFixed(precision)
            }
            if (elem.tagName=="TD") {
                elem.innerHTML=""
                measurement=''
                if (sensor.hasOwnProperty('unit_of_measurement')) {
                    measurement = sensor.unit_of_measurement
                }
                elem.innerHTML = `${wert} ${measurement}`;
            } else if (elem.tagName=="TR") {
                elemTd=elem.getElementsByClassName("value")[0].innerHTML = `${wert}`;
            }
        });
}

function getDataFromServer() {
    var allElements = document.querySelectorAll('*[id]');
    for (let elem of allElements) {
        if (elem.classList.contains('foxess')) {
            leseWertVomServer(elem.id, 'foxess');
        }
        else if (elem.classList.contains('homematic')) {
            leseWertVomServer(elem.id, 'homematic');
        }
    }
}

function getDailyDataFromServer() {
    fetch('allFoxessDaily')
        .then((daily_sensor_json) => daily_sensor_json.json())
        .then((daily_sensors) => {
            document.getElementById("all_daily_sensors").innerHTML=""
            innerHtml=""
            for (let datum of Object.keys(daily_sensors)) {
                anzeige_datum=datum.substr(6,2) + "." + datum.substr(4,2) + "." + datum.substr(0,4)
                anzahlWerte=Object.keys(daily_sensors[datum]).length;
                datumHtml=`<tr><td rowspan="${anzahlWerte}" style="text-align:left">${anzeige_datum}</td>`
                weitere=false
                for (let unique_id of Object.keys(daily_sensors[datum])) {
                    name=daily_sensors[datum][unique_id].name
                    wert=daily_sensors[datum][unique_id].value
                    unit_of_measurement=daily_sensors[datum][unique_id].unit_of_measurement
                    if (weitere) {
                        datumHtml+="<tr>"
                    }
                    weitere=true
                    datumHtml+=`<td id="${unique_id}">${name}</td><td>${wert}</td><td>${unit_of_measurement}</td></tr>`
                }
                innerHtml+=datumHtml
                innerHtml+="</tr>"
            }
            document.getElementById("all_daily_sensors").innerHTML=innerHtml
        });
}