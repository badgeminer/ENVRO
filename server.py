import asyncio,ansi2html
import sched,struct
import ansi2html.style
import threading,pika
import time,merge,logging,collections

from cachetools import TTLCache, cached
from env_canada import ECWeather
from flask import Flask, json, jsonify, render_template, request,Response,send_from_directory,redirect,send_file,url_for
from flask_cors import CORS, cross_origin

import pcap
logging.basicConfig(level=logging.DEBUG)

ansi2html.style.SCHEME["ansi2html"] = (
        "#555555",
        "#aa0000",
        "#00aa00",
        "#aa5500",
        "#0000aa",
        "#E850A8",
        "#00aaaa",
        "#F5F1DE",
        "#7f7f7f",
        "#ff0000",
        "#00ff00",
        "#ffff00",
        "#5c5cff",
        "#ff00ff",
        "#00ffff",
        "#ffffff",
    )
logSync = threading.Lock()
class ListHandler(logging.Handler):
    def __init__(self, log_list):
        super().__init__()
        self.log_list = log_list

    def emit(self, record):
        log_entry = self.format(record)
        logSync.acquire()
        self.log_list.append(log_entry)
        logSync.release()


log_messages = collections.deque(maxlen= 1000)
net_log_messages = collections.deque(maxlen= 1000)
list_handler = ListHandler(log_messages)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
list_handler.setFormatter(formatter)

logging.getLogger().addHandler(list_handler)
pcap.setup()

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
    "Snowfall Warning": "warns.SNOW",
    "Extreme Cold Warning" : "warns.COLD"
}
iconBindings = {
    "01":"clear",
    "02":"partcloud",
    "03":"partcloud",
    "04":"cloudy",
    "05":"partcloud",
    "06":"clear",
    "07":"raining",
    "08":"snowrain",
    "09":"snowing",
    "10":"thunderstorm",
    "11":"cloudy",
    "12":"raining",
    "13":"raining",
    "14":"hail",
    "15":"snowing",
    "16":"snowing",
    "17":"snowing",
    "18":"snowing",
    "26":"partcloud",
    "27":"partcloud",
    "28":"cloudy",
    "31":"raining",
    "32":"snowrain",
    "33":"snowing",
    "34":"thunderstorm",
    "35":"snowwind",
    "36":"windy"
}
alertsMap = {}

RABBITMQ_HOST = pika.URLParameters("amqp://enviro-server:enviro@10.0.0.41")

messages = []  # Store received messages in a list for demonstration
merged = {}

def callback_log(ch, method, properties, body):
    """Handle incoming RabbitMQ messages."""
    message = body.decode()
    logSync.acquire()
    list_handler.log_list.append(message)  # Store the message
    net_log_messages.append(message)
    logSync.release()
    
def callback_merged(ch, method, properties, body):
    global merged
    """Handle incoming RabbitMQ messages."""
    message = body.decode()
    merged = json.loads(message)
    

def consume_messages():
    """Start consuming messages from RabbitMQ."""
    connection = pika.BlockingConnection(RABBITMQ_HOST)
    channel = connection.channel()

    channel.basic_consume(queue="log", on_message_callback=callback_log, auto_ack=True)
    channel.basic_consume(queue="merged", on_message_callback=callback_merged, auto_ack=True)

    print("Waiting for messages...")
    channel.start_consuming()  # Blocking call

async def alertMap():
    global alertsMap
    alertsMap = pcap.fetch()
    

@cached(cache=TTLCache(maxsize=1024, ttl=60))
def update():
    weather = {
        "alerts" :[
        ],
        "cond":{},
        "icon_code":None
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
    weather["cond"]["ECicon_code"] = ec_en.conditions["icon_code"]["value"]
    weather["cond"]["icon_code"] = iconBindings.get(weather["cond"]["ECicon_code"],"err")
    return weather

@app.route("/api/alerts")
def alerts():
    global weather
    weather = update()
    return jsonify(weather["alerts"])
@app.route("/api/alerts/top")
def top_alert():
    if len(weather["alerts"]):
        return json.dumps(weather["alerts"][0])
    return json.dumps( {
            "mapped":"NONE",
            "title":"test",
            "class":"warnings"
        })
    

@app.route("/api/geojson/merged")
def geomerged():
    return jsonify(merged)

@app.route("/api/conditions")
def conditions():
    return jsonify(weather["cond"])

@app.route("/log")
def outLog():
    def streamLog():
        conv = ansi2html.Ansi2HTMLConverter()
        m = ""
        logSync.acquire()
        for i in log_messages:
            m += f"{conv.convert(i)}"
        logSync.release()
        return m
        
    return streamLog()

@app.route("/log/net")
def outNetLog():
    def streamLog():
        conv = ansi2html.Ansi2HTMLConverter()
        m = ""
        logSync.acquire()
        for i in net_log_messages:
            m += f"{conv.convert(i)}"
        logSync.release()
        return m
        
    return streamLog()

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
        if b["max"] > weather["cond"].get("wind_speed",0)+0.1:
            return jsonify({"scale":i,"icon":chr(0xe3af+i)})

@app.route("/api/tso")
def tso():
    pass


@app.route('/bar')
def bar():
    return render_template('bar.html')

@app.route('/')
def main():
    return send_from_directory("static/my-app/dist/","index.html")

@app.route('/assets/<path:key>')
def assets(key):
    return send_from_directory("static/my-app/dist/assets/",key)


if __name__ == '__main__':
  threading.Thread(target=consume_messages, daemon=True).start()
  app.run(host="0.0.0.0")