import eel,env_canada,asyncio,threading
radar_coords = env_canada.ECRadar(coordinates=(50, -100))
eel.init('web')                     # Give folder containing web files
actives = []

ec_en = env_canada.ECWeather(station_id='AB/s0000047', language='english')
types = [
    "warnings",
    "watches",
    "advisories",
    "statements",
    "endings"
]

def update():
    global temp,wtemp,wind,humid, a,wact,Wact
    try:
        asyncio.run(ec_en.update())
    except:
        pass
    if ec_en.conditions["wind_chill"]["value"]:
        wc = ec_en.conditions["wind_chill"]["value"]
    else:
        wc = ec_en.conditions["temperature"]["value"]
    eel.temps(str(ec_en.conditions["temperature"]["value"]),str(wc))
    eel.winds(str(ec_en.conditions["wind_speed"]["value"]),str(ec_en.conditions["wind_bearing"]["value"]))
    #wind = font.render(+" km/h at "++"°",True,(255,255,255))
    #humid = font.render(str(ec_en.conditions["humidity"]["value"])+'%',True,(255,255,255))
    a = []
    w = False
    W = False
    used = set()
    
    for c in types:
        if ec_en.alerts[c]["value"]:
            for i in ec_en.alerts[c]["value"]:
                if f"{c}_{i['title']}" in actives:
                    used.add(f"{c}_{i['title']}")
                else:
                    used.add(f"{c}_{i['title']}")
                    actives.append(f"{c}_{i['title']}")
                    eel.alerts_warn(c,
                                    f"{c}_{str(i['title']).replace(' ','_')}",
                                    i["title"])
                    
    for i in actives:
        if not i in used:
            actives.remove(i)
    

@eel.expose                         # Expose this function to Javascript
def handleinput(x):
    print('%s' % x)

def alrts():
    eel.sleep(2)
    #eel.prompt_alerts("test")
    update()
    while True:
        eel.sleep(30)
        update()


eel.say_hello_js('connected!')   # Call a Javascript function
eel.spawn(alrts)
eel.start('main.html',port=8008)    # Start
print("E")