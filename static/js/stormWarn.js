let sc = document.getElementById("temps");
let wc = document.getElementById("temps_wind");
let wnd = document.getElementById("wind");
var warns = {
    "TSTORM":" ",
    "TORNADO":" 󰼸",
    "HEAT":" ",
    "SNOW":"󰼩"
}
var watch = {
    "TSTORM":"󰼯 ",
    "TORNADO":"󰼯 󰼸",
}
var prioritys = [
    "warns.TORNADO",
    "watch.TORNADO",
    "warns.SNOW",
    "warns.TSTORM",
    "watch.TSTORM",
    "warns.HEAT",
    "test"
]
var alerts= {
    "NONE": {
        "bg":"#333",
    },
    "test":{
        "bg":"#119911",
        "symbols": ' ',
        "text":"TEST",
        "class":"test",
    }
}
for (const key in warns) {
    const element = warns[key];
    
    alerts[`warns.${key}`]={
        "class":"warnings",
        "bg":"red",
        "symbols": element,
        "text":key
    }
}
for (const key in watch) {
    const element = watch[key];
    
    alerts[`watch.${key}`]={
        "class":"watches",
        "bg":"yellow",
        "symbols": element,
        "text":key
    }
}

var top_alert = document.getElementById("topWarn");
var alertIcon = document.getElementById("warn");
var alertType = document.getElementById("warnType");
var curAlert = "NONE"
var prev = alerts[curAlert]
var alertData = alerts[curAlert]
function setAlertLayout() {
    var intr = 0;
    intr = setInterval(() => {
        top_alert.style.setProperty("--prev",alertData.bg)
        top_alert.style.setProperty("--side","left")
        clearInterval(intr)
    },501)
}

function setAlert(alert) {
    prev = alerts[curAlert]
    alertData = alerts[alert]
    top_alert.style.setProperty("--side","right")
    if (alert == "NONE") {
        
        top_alert.setAttribute("type","NONE")
        top_alert.style.setProperty("--prev",prev.bg)
        top_alert.style.setProperty("--cur",alertData.bg)
        alertIcon.innerText = ""
        alertType.innerText = ""
    } else {
        
        //top_alert.style.background = "linear-gradient(to left, yellow 50%, red 50%) right"
        
        
        top_alert.setAttribute("type",alertData.class)
        top_alert.style.setProperty("--prev",prev.bg)
        top_alert.style.setProperty("--cur",alertData.bg)

        //top_alert.class = `${alertData.class} twoLineData`
        //top_alert.classList[0] = alertData.class
        alertIcon.innerText = alertData.symbols
        alertType.innerText = alertData.text
        
    }
    setAlertLayout();

    curAlert = alert
}
var irtrv = () => {
    fetch("/api/alerts/top")
        .then((response) => response.json())
        .then((json) => {
            setAlert(json.mapped)
        });
        fetch("/api/conditions")
        .then((response) => response.json())
        .then((json) => {
            sc.innerText = `${json["temperature"]}°C`;
            wc.innerText = `${json["wind_chill"]}°C`;
            fetch("/api/conditions/bft")
                .then((rs) => rs.json())
                .then((bft) => {
                    wnd.innerText = `[ ${bft["icon"]} ] ${json["wind_speed"]} km/h at ${json["wind_bearing"]}°`
                })
        });
}
setInterval(irtrv,15000)
irtrv()