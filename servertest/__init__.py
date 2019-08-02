BASE_MODULE = "servertest"

import sys, time
# We would like to import modules that are added to his folder.
sys.path.append("/apps/" + BASE_MODULE)
sys.path.append("/apps/modules")
sys.path.append("D:\\Userdocs\\PeterdeWit\\Desktop\\CZ2019\\badge\\modules")

try:
  import rgb
except ImportError:
  pass

import gameservices, tetrisgameservices
connected = False

def host_on_connect(addr):
  global connected
  connected = True
  print("(host) connected:" + addr)
  if "rgb" in sys.modules:
    rgb.scrolltext("(host) client connected: " + addr, (255,255,255)) 

def host_on_disconnect(addr):
  global connected
  connected = False
  print("(host) disconnected:" + addr)
  if "rgb" in sys.modules:
    rgb.scrolltext("(host) client disconnected: " + addr, (255,255,255)) 

def host_on_row():
  print("(host) row added")
  if "rgb" in sys.modules:
    rgb.scrolltext("(host) client had row", (255,255,255)) 

def host_on_gameover():
  print("(host) gameover")
  if "rgb" in sys.modules:
    rgb.scrolltext("(host) client gameover", (255,255,255)) 

server = tetrisgameservices.TetrisGameHost()
server.register_on_connect(host_on_connect)
server.register_on_disconnect(host_on_disconnect)
server.register_on_row(host_on_row)
server.register_on_gameover(host_on_gameover)
server.start()

if "rgb" in sys.modules:
  rgb.clear()
  rgb.background((0,0,0))
  rgb.scrolltext("(host) running...", (255,255,255))

print("(host) running...")

if (not hasattr("time", "ticks_ms")):
  try:
    time.ticks_ms = lambda: int(round(time.time() * 1000))
  except:
    pass

row_send = 0
lastping = time.ticks_ms()

while True:
  time.sleep(0.1)

  if connected:
    cur_ticks = time.ticks_ms()
    diff_ticks = cur_ticks - lastping
    if diff_ticks > 10000:
      lastping = cur_ticks
      if row_send >=0 and row_send < 4:
        print("sending row...")
        server.send_row_added()
        row_send += 1
      if row_send == 5:
        row_send = -3
        server.send_gameover()    
