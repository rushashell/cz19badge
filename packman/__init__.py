BASE_MODULE = "test"

import sys
# We would like to import modules that are added to his folder.
sys.path.append("/apps/" + BASE_MODULE)

#import packman
import gameservice 

def on_connect(addr):
  print("connected:" + addr)

def on_disconnect(addr):
  print("disconnected:" + addr)

def on_data(data):
  print("data: " + data)
  
server = gameservice.GameHost()

server.register_on_connect(on_connect)
server.register_on_disconnect(on_disconnect)
server.register_on_data(on_data)
server.start()

while True:
  import time
  time.sleep(0.1)

#game = packman.Pacman()
#game.start()
