BASE_MODULE = "clienttest"

import sys, time
# We would like to import modules that are added to his folder.
sys.path.append("/apps/" + BASE_MODULE)
sys.path.append("/apps/Tetris-CZ19")
sys.path.append("H:\\CZ2019\\badge\\Tetris-CZ19")

connected = False 
row_added = False

try:
  import rgb
except ImportError:
  pass

import gameservices
import tetrisgameservices


def show_scrolltext(text):
  if "rgb" in sys.modules:
    rgb.clear()
    rgb.scrolltext(text, (255,255,255))

def client_on_connect(addr):
  global connected
  connected = True
  print("(client) connected:" + addr)
  show_scrolltext("(client) host connected: " + addr)

def client_on_disconnect(addr):
  global connected
  connected = False
  print("(client) disconnected:" + addr)
  show_scrolltext("(client) host disconnected: " + addr) 

def client_on_row():
  print("(client) row added")
  show_scrolltext("(client) host had row") 

def client_on_gameover():
  print("(client) gameover")
  show_scrolltext("(client) host gameover") 

def on_left(pressed):
  global connected
  if pressed and connected:
    print ("pressed")
    client.send_row_added()

def on_right(pressed):
  global connected
  if pressed and connected:
    print ("pressed")
    client.send_gameover()

client = tetrisgameservices.TetrisGameClient()
client.register_on_connect(client_on_connect)
client.register_on_disconnect(client_on_disconnect)
client.register_on_row(client_on_row)
client.register_on_gameover(client_on_gameover)
client.start("204.2.68.199")

if "rgb" in sys.modules:
  rgb.clear()
  rgb.background((0,0,0))
  rgb.scrolltext("Running...", (255,255,255))

if "buttons" in sys.modules:
  import buttons, defines
  buttons.register(defines.BTN_LEFT, on_left)
  buttons.register(defines.BTN_RIGHT, on_right)

while True:
  time.sleep(0.1)