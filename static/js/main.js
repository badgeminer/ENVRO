//document.getElementById("button-name").addEventListener("click", ()=>{eel.get_random_name()}, false);
//document.getElementById("button-number").addEventListener("click", ()=>{eel.get_random_number()}, false);
//document.getElementById("button-date").addEventListener("click", ()=>{eel.get_date()}, false);
//document.getElementById("button-ip").addEventListener("click", ()=>{eel.get_ip()}, false);
let sc = document.getElementById("temps");
let wc = document.getElementById("temps_wind");
let wnd = document.getElementById("wind");
let warnsls = document.getElementById("warns");
//eel.expose(prompt_alerts);
function prompt_alerts(description) {
  alert(description);
}



//eel.expose(alerts_warn);
function alerts_warn(type,id,title) {
  let a = document.createElement("div")
  a.classList.add(type)
  a.id = id
  a.innerHTML = `<h3>${title}</h3>`
  document.getElementById(`${type}`).appendChild(a)
}

//eel.expose(temps);
function temps(static,wind) {
  sc.innerText = `${static}°C`;
  wc.innerText = `${wind}°C`;
}
//eel.expose(winds);
function winds(speed,hddn) {
  wnd.innerText = `${speed} km/h @ ${hddn}°`;
}
//eel.expose(refr);
function refr(description) {
  document.getElementById("cntr").innerHTML = "<img "
}
var timeDisplay = document.getElementById("time");
var dateDisplay = document.getElementById("date");


function refreshTime() {
  var d= new Date();
  var dateString = new Date().toLocaleString("en-US",);
  var formattedString = dateString.replace(", ", " - ");
  formattedString = `${d.getUTCHours()}:${d.getUTCMinutes()}Z`
  timeDisplay.innerHTML = formattedString;
  dateDisplay.innerHTML = `${d.getUTCFullYear()}-${d.getUTCMonth()}-${d.getUTCDate()}`;
}

setInterval(refreshTime, 1000);

function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open( "GET", theUrl, false ); // false for synchronous request
    xmlHttp.send( null );
    return xmlHttp.responseText;
}

var cntr = document.getElementById("cntr");
function update(url) {
  cntr.innerHTML = httpGet(url)
}