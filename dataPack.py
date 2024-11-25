import calendar
import datetime
import re
import xml.sax.handler

import dateutil.parser as duparser
import requests
from bs4 import BeautifulSoup

R1 = re.compile(r"^\s{2,}", re.MULTILINE)

def clean_text(field_name, raw_text):
    if field_name in ['description','instruction']:
        return R1.sub(" ", raw_text.strip()).replace('\n',' ')
    return raw_text

def convert_timestamp(t):
    #e.g., 2012-03-15T22:18:00-04:00
    dt = duparser.parse(t)
    return calendar.timegm(dt.utctimetuple())



def get_url_paths(url, ext='', params={}):
    response = requests.get(url, params=params)
    if response.ok:
        response_text = response.text
    else:
        return []
    soup = BeautifulSoup(response_text, 'html.parser')
    parent = [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
    return parent


url = 'https://dd.weather.gc.ca/alerts/cap/20241122/CWNT/15/'
ext = 'cap'

alerts = []
prov =("AB","SK","MB")
issu = ("CWNT","CWWG","CWVR")

types = {
    "snowfall":1,
    "blizzard":2,
    "tornado":4
}


def xml2obj(src):
    """
    A simple function to converts XML data into native Python object.
    """

    non_id_char = re.compile('[^_0-9a-zA-Z]')
    def _name_mangle(name):
        return non_id_char.sub('_', name)

    class DataNode(object):
        def __init__(self):
            self._attrs = {}    # XML attributes and child elements
            self.data = None    # child text data
        def __len__(self):
            # treat single element as a list of 1
            return 1
        def __getitem__(self, key):
            if isinstance(key, str|bytes):
                return self._attrs.get(key,None)
            else:
                return [self][key]
        def __contains__(self, name):
            return name in self._attrs
        def __nonzero__(self):
            return bool(self._attrs or self.data)
        def __getattr__(self, name):
            if name.startswith('__'):
                # need to do this for Python special methods???
                raise AttributeError(name)
            return self._attrs.get(name,None)
        def _add_xml_attr(self, name, value):
            if name in self._attrs:
                # multiple attribute of the same name are represented by a list
                children = self._attrs[name]
                if not isinstance(children, list):
                    children = [children]
                    self._attrs[name] = children
                children.append(value)
            else:
                self._attrs[name] = value
        def __str__(self):
            return self.data or ''
        def __repr__(self):
            items = sorted(self._attrs.items())
            if self.data:
                items.append(('data', self.data))
            return u'{%s}' % ', '.join([u"'%s':%s" % (k,repr(v)) for k,v in items])

    class TreeBuilder(xml.sax.handler.ContentHandler):
        def __init__(self):
            self.stack = []
            self.root = DataNode()
            self.current = self.root
            self.text_parts = []
        def startElement(self, name, attrs):
            self.stack.append((self.current, self.text_parts))
            self.current = DataNode()
            self.text_parts = []
            # xml attributes --> python attributes
            for k, v in attrs.items():
                self.current._add_xml_attr(_name_mangle(k), v)
        def endElement(self, name):
            text = ''.join(self.text_parts).strip()
            if text:
                self.current.data = clean_text(name,text)
            if self.current._attrs:
                obj = self.current
            else:
                # a text only node is simply represented by the string
                obj = clean_text(name,text) or ''
            self.current, self.text_parts = self.stack.pop()
            self.current._add_xml_attr(_name_mangle(name), obj)
            try:
                if str(obj).strip() != '':
                    obj_epoch = convert_timestamp(obj)
                    self.current._add_xml_attr(_name_mangle("%s_epoch"%name), obj_epoch)
            except:
                pass
        def characters(self, content):
            self.text_parts.append(content)


    builder = TreeBuilder()
    if isinstance(src,str|bytes):
        xml.sax.parseString(src, builder)
    else:
        xml.sax.parse(src, builder)
    return builder.root._attrs

def extract():
    t = datetime.datetime.now(datetime.timezone.utc)
    alerts = {}
    zones = {}
    for i in range(24,0,-1):
        T = datetime.timedelta(hours=i)
        d = t-T
        #print(f"{d.day} -> {d.hour}")
        
        for iss in issu:
            url = f'https://dd.weather.gc.ca/alerts/cap/{d.year}{d.month}{d.day}/{iss}/{d.hour}/'
            result: list[str] = get_url_paths(url, ext)
            #for p in prov:
            #    print(f"{d.year}{d.month}{d.day}/CWNT/{d.hour}/T_{p}CN")
            for r in result:
                
                #print(r.removeprefix(url))
                #d = feedparser.parse(r)
                #pprint.pprint(d)
                R = requests.get(r)
                #f = io.BytesIO(R.content)
                tr = xml2obj(R.content)
                #pprint.pprint(tr['alert']['info'])
                #print(tr["alert"]['info'][0]['event'])
                alert ={"type": "FeatureCollection","features":[]}
                if tr["alert"]['info'][0]["responseType"] != "AllClear":
                    for i in tr["alert"]['info'][0]["area"]:
                        coords_pair = str(i["polygon"]).split(" ")
                        coords = []
                        for pir in coords_pair:
                            coord = []
                            for C in pir.split(","):
                                coord.insert(0,float(C))
                            coords.append(coord)
                        coords = tuple(coords)
                        coordsS= str(coords)
                        typ = types[tr["alert"]['info'][0]['event']]
                        if zones.get(coordsS,0) &  typ == 0:
                            zones[coordsS] = zones.get(coordsS,0) | typ
                            alert["features"].append({
                                "type": "Feature",
                                "geometry":{
                                    "type": "Polygon",
                                    "coordinates": [coords]
                                },
                                "properties": {
                                    "warn": tr["alert"]['info'][0]['event']
                                }
                            })
                    for r in tr["alert"]["references"].split("\n"):
                        try:
                            Rd = r.split(",")
                            R = Rd[1]
                            if alerts.get(R,None):
                                del alerts[R]
                            print(f"ended {R}")
                        except:
                            print("E",r)
                    alerts[tr["alert"]["identifier"]] = alert
                    print(f"set {tr['alert']['identifier']}")
                else:
                    
                    for r in tr["alert"]["references"].split("\n"):
                        try:
                            Rd = r.split(",")
                            R = Rd[1]
                            if alerts.get(R,None):
                                del alerts[R]
                            print(f"ended {R}")
                        except:
                            print("E",r)
    return alerts
def merge(alerts):
    alert ={"type": "FeatureCollection","features":[]}
    for k,v in alerts.items():
        for i in v["features"]:
            alert["features"].append(i)
    return alert
    
if __name__ == "__main__":                 
    extract()