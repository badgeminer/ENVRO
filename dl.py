import datetime,requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

issu = ("CWNT","CWWG","CWVR")

def get_url_paths(url, ext='', params={}):
    response = requests.get(url, params=params)
    if response.ok:
        response_text = response.text
    else:
        return []
    soup = BeautifulSoup(response_text, 'html.parser')
    parent = [(url + node.get('href'),node.get('href')) for node in soup.find_all('a') if node.get('href').endswith(ext)]
    return parent

t = datetime.datetime.now(datetime.timezone.utc)

for i in range(48,0,-1):
    T = datetime.timedelta(hours=i)
    d = t-T
    #print(f"{d.day} -> {d.hour}")
    
    for iss in issu:
        url = f'https://dd.weather.gc.ca/alerts/cap/{d.year}{d.month}{d.day}/{iss}/{d.hour}/'
        result: list[str] = get_url_paths(url, "cap")
        #for p in prov:
        #    print(f"{d.year}{d.month}{d.day}/CWNT/{d.hour}/T_{p}CN")
        for r,name in result:
            R = requests.get(r)
            root = ET.fromstring(R.text)
        
            # CAP namespace handling
            ns = {'cap': 'urn:oasis:names:tc:emergency:cap:1.2'}
            
            # Extract relevant fields
            status = root.find('cap:status', ns).text  # Example: "Actual"
            response_type = root.find('cap:info/cap:responseType', ns)
            event = root.find('cap:info/cap:event', ns).text
            if event == "freezing rain":
                with open(f"cap/{name}","w") as f:
                    f.write(R.text)