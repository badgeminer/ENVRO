import pygame,threading,pika,re,time
import textwrap
import win32api
import win32con
import win32gui

import pyttsx3

testSrv = pika.URLParameters("amqp://alert:alert@10.0.0.41")

engine = pyttsx3.init()
def onEnd():
    engine.endLoop()
engine.connect('finished-utterance', onEnd)
voices = engine.getProperty('voices')       #getting details of current voice
#engine.setProperty('voice', voices[0].id)  #changing index, changes voices. o for male
engine.setProperty('voice', voices[1].id)   #changing index, changes voices. 1 for female

class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 25)

    def tprint(self, screen, text):
        text_bitmap = self.font.render(text, False, (255, 255, 255))
        screen.blit(text_bitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 500
        self.y = 45
        self.line_height = 20

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10

pygame.init()
warnbeep2 = pygame.mixer.Sound("canada-eas-alert.mp3")
infoObject = pygame.display.Info()
scr = pygame.display.set_mode((infoObject.current_w, infoObject.current_h),pygame.NOFRAME|pygame.FULLSCREEN) # For borderless, use pygame.NOFRAME
done = False
fuchsia = (255, 0, 128)  # Transparency color
red = (255, 0, 0)

# Create layered window
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
# Set window transparency color
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)
win32gui.SetWindowPos(pygame.display.get_wm_info()['window'], win32con.HWND_TOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

size = min(infoObject.current_w,infoObject.current_h)
redSquare = pygame.Rect(0,0,size,size)
redSquare.centerx = infoObject.current_w/2
redSquare.centery = infoObject.current_h/2
text = []
def say(s):
    text.extend([line for line in re.findall(r'.{1,100}(?:\s+|$)', s)])
    def trd():
        global text
        warnbeep2.play()
        time.sleep(warnbeep2.get_length())
        
        engine.say(s)
        engine.runAndWait()
        text = []
    t = threading.Thread(None,trd,daemon=True)
    t.start()


tp = TextPrint()
hidden = False

connection = pika.BlockingConnection(testSrv)
channel = connection.channel()

result = channel.queue_declare(queue='', exclusive=True)
channel.queue_bind(exchange='alerting',
                   queue=result.method.queue)

def callback(ch, method, properties, body):
    b = body.decode()
    say(b)


def runAMQP():
    channel.basic_consume(
    queue=result.method.queue, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
threading.Thread(target=runAMQP,daemon=True).start()


say("""ENVIROTRON ALERT
At 14:29, Enviroment Canada issued a extreme cold warning


A prolonged extreme cold event continues over southern Manitoba, with the region experiencing extreme wind chill values of minus 40 or lower at times.

While wind chill values may moderate slightly during the day, they are anticipated to return to extreme levels at night and in the mornings.

Extreme cold warnings are expected to remain in place for many over the next few days. Temperatures will begin to moderate by Thursday with a significant warm-up expected next weekend.

###

Extreme cold puts everyone at risk.

Risks are greater for young children, older adults, people with chronic illnesses, people working or exercising outdoors, and those without proper shelter.

Extreme cold warnings are issued when very cold temperatures or wind chill creates an elevated risk to health such as frost bite and hypothermia.

Please continue to monitor alerts and forecasts issued by Environment Canada. To report severe weather, send an email to MBstorm@ec.gc.ca, call 1-800-239-0484 or post reports on X using #MBStorm.""")
while not done:
    tp.reset()
    if len(text) == 0:
        if not hidden:
            scr = pygame.display.set_mode((800, 600), flags=pygame.HIDDEN)
    elif hidden:
        scr = pygame.display.set_mode((infoObject.current_w, infoObject.current_h),pygame.NOFRAME|pygame.FULLSCREEN)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            done = True
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                done = True
            if e.key == pygame.K_F1:
                pygame.display.iconify()

    scr.fill((0,0,0))  # Transparent background
    pygame.draw.rect(scr, red, redSquare)
    tp.tprint(scr,"This Is Only A Test")
    for t in text:
        tp.tprint(scr,t)
    
    pygame.display.update()