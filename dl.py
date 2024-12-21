import datetime,requests
from bs4 import BeautifulSoup

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

for i in range(24,0,-1):
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
            with open(f"cap/{name}","w") as f:
                f.write(R.text)