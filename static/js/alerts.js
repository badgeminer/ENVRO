var active = new Set();
var types = [
    "warnings",
    "watches",
    "advisories",
    "statements",
    "endings"
]
function alerts_warn(type,id,title) {
    let a = document.createElement("div")
    a.classList.add(type)
    a.id = id
    a.innerHTML = `<h3>${alerts[id]["symbols"]} ${title}</h3>`
    document.getElementById(`${type}`).appendChild(a)
  }

setInterval(() => {
    fetch("/api/alerts")
  .then((response) => response.json())
  .then((json) => {
    for (const type of types) {
        document.getElementById(`${type}`).innerHTML = ""
    }
    if (json.alerts.length > 0) {
        for (const element of json.alerts) {
            alerts_warn(element.class,element.mapped,element.title)
        }
    }
    
  });
},15000)