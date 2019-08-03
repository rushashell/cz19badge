BASE_MODULE = "clienttest"

import sys, time
# We would like to import modules that are added to his folder.
sys.path.append("/apps/" + BASE_MODULE)
sys.path.append("/apps/tetris_cz19")
sys.path.append("H:\\CZ2019\\badge\\tetris_cz19")

import badgehelper

DEBUG = False
connected = False 
received_rows = 0

if badgehelper.on_badge():
  import rgb

import gameservices
import tetrisgameservices

def show_scrolltext(text):
  if badgehelper.on_badge():
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
  global received_rows
  received_rows += 1
  print("(client) received row")
  show_scrolltext("(client) received row " + str(received_rows)) 

def client_on_gameover():
  print("(client) received gameover")
  show_scrolltext("(client) received gameover") 

def on_left(pressed):
  global connected
  if pressed and connected:
    print ("pressed")
    client.send_data("row")

def on_right(pressed):
  global connected
  if pressed and connected:
    print ("pressed")
    client.send_data("gameover")

client = gameservices.GameClient()
#client.register_on_connect(client_on_connect)
#client.register_on_disconnect(client_on_disconnect)
#client.register_on_row(client_on_row)
#client.register_on_gameover(client_on_gameover)
 
# TEMPORARY
if DEBUG == True or not badgehelper.on_badge():
  client.network_type = gameservices.GAME_CLIENT_NETWORK_TYPE_NORMAL
  
  if badgehelper.on_badge():
    # Running on badge, so connect to PDW
    print("Connecting with 204.2.68.199...")
    client.start("204.2.68.199")
  else:
    # Running in debug mode on PDW, connect to badge
    client.start("100.64.13.227")
else:
  client.network_type = gameservices.GAME_CLIENT_NETWORK_TYPE_HOTSPOT 
  client.start(gameservices.GAME_NETWORK_TYPE_HOTSPOT_SERVERIP)

# Wait for connection
print("Waiting for connection...")
connected = client.wait_for_connection()

if connected:
  print("connected")
else:
  print("not connected")

if badgehelper.on_badge():
  rgb.clear()
  rgb.background((0,0,0))
  rgb.scrolltext("Running...", (255,255,255))

  import buttons, defines
  buttons.register(defines.BTN_LEFT, on_left)
  buttons.register(defines.BTN_RIGHT, on_right)
else:
  print("Running...")

while True:
  time.sleep(0.1)
  data = client.read_data()

  if not data:
    continue

  if data == "row" or data == "row\r\n" or data == "'row'" or data == "'row\\r\\n'":
    client_on_row()
  elif data == "gameover":
    client_on_gameover()