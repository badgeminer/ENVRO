import asyncio
import sched,struct
import threading
import time,merge

from cachetools import TTLCache, cached
from env_canada import ECWeather
from flask import Flask, json, jsonify, render_template, request,Response,send_from_directory,redirect,send_file,url_for
from flask_cors import CORS, cross_origin

import dataPack,pcap

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
conditionTypes = [
    "temperature",
    "dewpoint",
    "wind_speed",
    "wind_chill",
    "wind_bearing"
]

windLevels = [
    {"max":1},
    {"max":5},
    {"max":11},
    {"max":19},
    {"max":28},
    {"max":38},
    {"max":49},
    {"max":61},
    {"max":74},
    {"max":88},
    {"max":102},
    {"max":117},
    {"max":133},
]

weather = {
    "alerts" :[],
    "cond":{}
}
mapings = {
    "Tornado Warning":             "warns.TORNADO",
    "Tornado Watch":               "watch.TORNADO",
    "SEVERE THUNDERSTORM WARNING": "warns.TSTORM",
    "SEVERE THUNDERSTORM WATCH":   "watch.TSTORM",
    "Snowfall Warning": "warns.SNOW"
}
alertsMap = {}

async def alertMap():
    global alertsMap
    alertsMap = pcap.fetch()
    
@cached(cache=TTLCache(maxsize=1024, ttl=60*5))
def getMap():
    asyncio.run(alertMap())
    return alertsMap

@cached(cache=TTLCache(maxsize=1024, ttl=60))
def update():
    weather = {
        "alerts" :[
        ],
        "cond":{}
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
    for c in conditionTypes:
        weather["cond"][c] = ec_en.conditions[c]["value"]
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
    
@app.route("/api/geojson/<name>")
def geo(name):
    return json.dumps(getMap()[name])

@app.route("/api/geojson")
def geokeys():
    return json.dumps(tuple(getMap()))

@app.route("/api/geojson/merged")
def geomerged():
    return jsonify(pcap.merge(getMap()))

@app.route("/api/conditions")
def conditions():
    return jsonify(weather["cond"])


def utf8_integer_to_unicode(n):
    #s= hex(n)
    #if len(s) % 2:
    #    s= '0'+s
    #return s.decode('hex').decode('utf-8')
    return struct.pack(">H",n)

@app.route("/api/conditions/bft")
def conditionsbft():
    print(b'')
    for i,b in enumerate(windLevels):
        if b["max"] >weather["cond"]["wind_speed"]+0.1:
            return jsonify({"scale":i,"icon":chr(0xe3af+i)})

@app.route("/api/tso")
def tso():
    pass

@app.route('/')
def render_main():
    return render_template('alerts.html',alrt =True,data=False,forc=False,map=False,abs=False)
@app.route('/data')
def render_data():
    return render_template('data.html',alrt =False,data=True,forc=False,map=False,abs=False)

@app.route('/forcast')
def render_forcast():
    return render_template('forcast.html',alrt =False,data=False,forc=True,map=False,abs=False)
@app.route('/map')
def maps():
    return render_template('map.html',alrt =False,data=False,forc=False,map=True,abs=False)
@app.route('/bar')
def bar():
    return render_template('bar.html')

@app.route('/main')
def main():
    return send_from_directory("static/my-app/dist/","index.html")

@app.route('/assets/<path:key>')
def assets(key):
    return send_from_directory("static/my-app/dist/assets/",key)


if __name__ == '__main__':
  app.run(host="0.0.0.0")