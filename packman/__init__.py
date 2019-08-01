BASE_MODULE = "packman"

import sys, time
# We would like to import modules that are added to his folder.
sys.path.append("/apps/" + BASE_MODULE)

#import packman
import gameservices
import tetrisgameservices

def host_on_connect(addr):
  print("(host) connected:" + addr)

def host_on_disconnect(addr):
  print("(host) disconnected:" + addr)

def host_on_row():
  print("(host) row added")
  
def client_on_row():
  print("(client) row added")
  
def client_on_gameover():
  print("(client) gameover")

server = tetrisgameservices.TetrisGameHost()

server.register_on_connect(host_on_connect)
server.register_on_disconnect(host_on_disconnect)
server.register_on_row(host_on_row)
server.start()

client = tetrisgameservices.TetrisGameClient()
client.register_on_row(client_on_row)
client.register_on_gameover(client_on_gameover)

counter = 0
while True:
  time.sleep(2)
  client.start("127.0.0.1")
  time.sleep(3)
  client.send_row_added()
  time.sleep(3)
  server.send_row_added()
  time.sleep(3)
  server.send_gameover()
  time.sleep(3)
  client.stop()


#game = packman.Pacman()
#game.start()
