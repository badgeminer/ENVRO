


var checks = document.getElementById('checks')
function makeBind(name) {
    var elem = document.getElementById(name)
    var data = document.createElement("p");
    var check = document.createElement("input");
    check.type = "checkbox";
    check.checked = !elem.hidden;
    data.innerText = name;
    //data.appendChild(check);
    data.insertAdjacentElement("afterbegin",check)
    checks.appendChild(data)
    

    check.addEventListener('change', (event) => {
        elem.hidden = !event.currentTarget.checked
      })
}
makeBind("shear")
makeBind("MUCAPE")
makeBind("VORT")
makeBind("DEW")
makeBind("MOIST")
makeBind("DIVERG")