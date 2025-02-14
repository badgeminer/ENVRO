import env_canada,asyncio,requests,datetime,pika,sqlite3,logging,connLog,json,time
from bs4 import BeautifulSoup
lookback = 24

logger = logging.Logger("DL")
testSrv = pika.URLParameters("amqp://enviro:enviro@10.0.0.41")

connection = pika.BlockingConnection(testSrv)
channel = connection.channel()
chnd = connLog.ConnHandler(channel)
formatter = logging.Formatter('DL - %(asctime)s - %(levelname)s - %(message)s')
chnd.setFormatter(formatter)
logger.addHandler(chnd)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

issu = ("CWNT","CWWG","CWVR")

def setup():
    c = sqlite3.connect("alert.db")
    c.execute("CREATE TABLE if not exists  `Alerts` (`key` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, `id` TEXT UNIQUE, `data` TEXT)")
    c.execute("CREATE TABLE if not exists  `formattedAlert` (`id` TEXT PRIMARY KEY UNIQUE, `begins` TEXT, `ends` TEXT, `areas` TEXT, `urgency` TEXT, `references` TEXT, `msgType` TEXT, `type` TEXT)")
    c.close()
    logger.info("PCAP setup")

def get_url_paths(url, ext='', params={}):
    response = requests.get(url, params=params)
    if response.ok:
        response_text = response.text
    else:
        return []
    soup = BeautifulSoup(response_text, 'html.parser')
    parent = [(url + node.get('href'),node.get('href')) for node in soup.find_all('a') if node.get('href').endswith(ext)]
    return parent

def cache(sql:sqlite3.Cursor,url):
    sql.execute("SELECT EXISTS(SELECT 1 FROM Alerts WHERE id=?)",(url,))
    fth =  sql.fetchone()
    if not fth[0]:
        logger.info(url)
        R = requests.get(url)
        sql.execute("INSERT or replace INTO Alerts (id,data) VALUES (?,?)",(url,R.text))
        return R.text
    else:
        sql.execute("SELECT data FROM Alerts WHERE id=?",(url,))
        fth =  sql.fetchone()
        return fth[0]

def fetch():
    global lookback
    t = datetime.datetime.now(datetime.timezone.utc)
    dat = []
    for i in range(lookback,0,-1):
        T = datetime.timedelta(hours=i)
        d = t-T
        #print(f"{d.day} -> {d.hour}")
        
        for iss in issu:
            conn = sqlite3.connect("alert.db")
            cur = conn.cursor()
            url = f'https://dd.weather.gc.ca/{d.year}{d.month:>02}{d.day:>02}/WXO-DD/alerts/cap/{d.year}{d.month:>02}{d.day:>02}/{iss}/{d.hour:>02}/'
            result: list[str] = get_url_paths(url, "cap")
            #for p in prov:
            #    print(f"{d.year}{d.month}{d.day}/CWNT/{d.hour}/T_{p}CN")
            for r,name in result:
                R = cache(cur,r)
                dat.append(R)
                channel.basic_publish("","alert_cap",json.dumps({
                    "typ":"dat",
                    "data":R
                }),pika.BasicProperties(content_type='text/json',
                                           delivery_mode=pika.DeliveryMode.Transient))
            conn.commit()
            conn.close()
    lookback = 1
    channel.basic_publish("","alert_cap",json.dumps({
                    "typ":"merge",
                    "data":"..."
                }),pika.BasicProperties(content_type='text/json',
                                           delivery_mode=pika.DeliveryMode.Transient))
def downloader():
    try:
        while True:
            logger.info("downloading")
            fetch()
            time.sleep(60*5)
    except:
        logger.warning("DL offline")
        connection.close()