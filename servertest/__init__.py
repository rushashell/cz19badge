BASE_MODULE = "servertest"

import sys, time
# We would like to import modules that are added to his folder.
sys.path.append("/apps/" + BASE_MODULE)
sys.path.append("/apps/tetris_cz19")
sys.path.append("H:\\CZ2019\\badge\\tetris_cz19")

import badgehelper
import gameservices, tetrisgameservices

if badgehelper.on_badge():
  import rgb

DEBUG = False
connected = False
received_rows = 0

def host_on_connect(addr):
  global connected
  connected = True
  print("(host) connected:" + addr)
  if badgehelper.on_badge():
    rgb.clear()
    rgb.scrolltext("(host) client connected: " + addr, (255,255,255)) 

def host_on_disconnect(addr):
  global connected
  connected = False
  print("(host) disconnected:" + addr)
  if badgehelper.on_badge():
    rgb.clear()
    rgb.scrolltext("(host) client disconnected: " + addr, (255,255,255)) 

def host_on_row():
  global received_rows
  print("(host) row added")
  received_rows += received_rows
  if badgehelper.on_badge():
    rgb.clear()
    rgb.scrolltext("(host) received row " + str(received_rows), (255,255,255)) 

def host_on_gameover():
  print("(host) gameover")
  if badgehelper.on_badge():
    rgb.clear()
    rgb.scrolltext("(host) received gameover", (255,255,255)) 

def on_left(pressed):
  global connected, server
  if pressed and connected:
    print ("pressed")
    server.send_data("row")

def on_right(pressed):
  global connected
  if pressed and connected:
    print ("pressed")
    server.send_data("gameover")

server = gameservices.GameHost()
#server.register_on_connect(host_on_connect)
#server.register_on_disconnect(host_on_disconnect)
#server.register_on_row(host_on_row)
#server.register_on_gameover(host_on_gameover)

if DEBUG == True or not badgehelper.on_badge():
  server.network_type = gameservices.GAME_HOST_NETWORK_TYPE_NORMAL
else:
  print("on the badge")
  server.network_type = gameservices.GAME_HOST_NETWORK_TYPE_HOTSPOT

server.start()

print("Waiting for connection...")
server.wait_for_connection()
connected = True
print("Done.")

if badgehelper.on_badge():
  rgb.clear()
  rgb.background((0,0,0))
  rgb.scrolltext("(host) running...", (255,255,255))

  import buttons, defines
  buttons.register(defines.BTN_LEFT, on_left)
  buttons.register(defines.BTN_RIGHT, on_right)

print("(host) running...")

row_send = 0
lastping = time.ticks_ms()

while True:
  time.sleep(0.1)

  data = server.read_data()

  if data:
    if data == "row" or data == "row\r\n" or data == "'row'" or data == "'row\\r\\n'":
      host_on_row()

    if data == "gameover":
      host_on_gameover()

  if connected and not badgehelper.on_badge():
    cur_ticks = time.ticks_ms()
    diff_ticks = cur_ticks - lastping
    if diff_ticks > 10000:
      lastping = cur_ticks
      if row_send >=0 and row_send < 8:
        print("sending row...")
        server.send_data("row")
        row_send += 1
