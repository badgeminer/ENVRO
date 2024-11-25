var panes = {}
panes.alerts = document.getElementById("alerts");
panes.data = document.getElementById("data");
//panes.forcast = document.getElementById("forcast");
panes.map = document.getElementById("map");
function swtch(name) {
    for (const p in panes) {
            const element = panes[p];
            element.hidden = true
    }
    panes[name].hidden = false
}