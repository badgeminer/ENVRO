from flask import Flask, jsonify, json, request, render_template
from flask_cors import CORS,cross_origin
import sched, time,asyncio
from cachetools import cached,TTLCache
from env_canada import ECWeather
import threading


app = Flask(__name__)
CORS(app,resources=r'/api/*')
ec_en = ECWeather(station_id='AB/s0000047', language='english')
types = [
    "warnings",
    "watches",
    "advisories",
    "statements",
    "endings"
]
weather = {
    "alerts" :[]
}
mapings = {
    "Tornado Warning":             "warns.TORNADO",
    "Tornado Watch":               "watch.TORNADO",
    "SEVERE THUNDERSTORM WARNING": "warns.TSTORM",
    "SEVERE THUNDERSTORM WATCH":   "watch.TSTORM",
    "Snowfall Warning": "warns.SNOW"
}

@cached(cache=TTLCache(maxsize=1024, ttl=60))
def update():
    weather = {
        "alerts" :[
        ]
    }
    try:
        print("up")
        asyncio.run(ec_en.update())
    except:
        pass
    for c in types:
        if ec_en.alerts[c]["value"]:
            for i in ec_en.alerts[c]["value"]:
                weather["alerts"].append({
                    "mapped":mapings.get(i['title'],"NONE"),
                    "title":i['title'],
                    "class":c
                })
    return weather

route = [[51.1435, -114.257], [51.1441, -114.2583], [51.1451, -114.2606],[51.1463, -114.2639]]
chsr = [51,-114]
@app.route("/api/chsr",methods=['POST'])
def my_route():
    route.append(request.json)
    chsr = request.json
    return json.dumps(
        {
            "route":route,
            "chsr":chsr
        })
    
@app.route("/api/route")
def routes():
    return json.dumps(
        {
            "route":route,
            "chsr":chsr
        })
@app.route("/api/alerts")
def alerts():
    global weather
    weather = update()
    return json.dumps(
        weather)
@app.route("/api/alerts/top")
def top_alert():
    if len(weather["alerts"]):
        return json.dumps(weather["alerts"][0])
    return json.dumps( {
            "mapped":"NONE",
            "title":"test",
            "class":"warnings"
        })
    
app.route("/api/tso")
def tso():
    pass

@app.route('/')
def render_main():
    return render_template('alerts.html',alrt =True,data=False,forc=False,map=False,abs=False)
@app.route('/data')
def render_data():
    return render_template('data.html',alrt =False,data=True,forc=False,map=False,abs=True)

@app.route('/forcast')
def render_forcast():
    return render_template('forcast.html',alrt =False,data=False,forc=True,map=False,abs=True)
@app.route('/map')
def maps():
    return render_template('map.html',alrt =False,data=False,forc=False,map=True,abs=False)

if __name__ == '__main__':
  app.run(host="0.0.0.0")