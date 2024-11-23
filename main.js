//document.getElementById("button-name").addEventListener("click", ()=>{eel.get_random_name()}, false);
//document.getElementById("button-number").addEventListener("click", ()=>{eel.get_random_number()}, false);
//document.getElementById("button-date").addEventListener("click", ()=>{eel.get_date()}, false);
//document.getElementById("button-ip").addEventListener("click", ()=>{eel.get_ip()}, false);
let sc = document.getElementById("temps");
let wc = document.getElementById("temps_wind");
let wnd = document.getElementById("wind");
let warns = document.getElementById("warns");
eel.expose(prompt_alerts);
function prompt_alerts(description) {
  alert(description);
}

eel.expose(alerts_warn);
function alerts_warn(type,id,title) {
  let a = document.createElement("div")
  a.classList.add(type)
  a.id = id
  a.innerHTML = `<h3>${title}</h3>`
  document.getElementById(`${type}`).appendChild(a)
}

eel.expose(temps);
function temps(static,wind) {
  sc.innerText = `${static}°C`;
  wc.innerText = `${wind}°C`;
}
eel.expose(winds);
function winds(speed,hddn) {
  wnd.innerText = `${speed} km/h @ ${hddn}°`;
}
eel.expose(refr);
function refr(description) {
  document.getElementById("cntr").innerHTML = "<img "
}

var timeDisplay = document.getElementById("time");
var Display = document.getElementById("time");


function refreshTime() {
  var dateString = new Date().toLocaleString("en-US", {timeZone: "America/Sao_Paulo"});
  var formattedString = dateString.replace(", ", " - ");
  timeDisplay.innerHTML = formattedString;
}

setInterval(refreshTime, 1000);