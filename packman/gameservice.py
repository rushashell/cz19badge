import sys, time, gc

try:
  import thread
except ImportError:
  import _thread as thread

try:
  import socket
except ImportError:
  import _socket as socket

try:
  import wifi
except ImportError:
  pass

try:
  import random
except ImportError:
  import urandom as random


if (not hasattr("time", "ticks_ms")):
  time.ticks_ms = lambda: int(round(time.time() * 1000))

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 55667        # Port to listen on (non-privileged ports are > 1023)

class GameHost:
  def __init__(self):
    self.port = PORT
    self.sock = None
    self.listen_thread = None
    self.is_running = True

    # Callbacks 
    self.CALLBACK_ON_CONNECT = None 
    self.CALLBACK_ON_DISCONNECT = None 
    self.CALLBACK_ON_DATA = None 

    random.seed(time.ticks_ms())
    pass

  def start(self):
    if "wifi" in sys.modules:
      wifi.connect()
      _  = wifi.wait()

    addr = socket.getaddrinfo("0.0.0.0", self.port)[0][-1]
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    self.sock.bind(addr)
    
    self.sock.listen(1) # Only allow one single connection at a time
    self.sock.settimeout(None)

    self.listen_thread = thread.start_new_thread(self._listen, ())
    self.is_running = True 

  def stop(self):
    self.is_running = False
    pass

  def register_on_connect(self, action = None):
    self.CALLBACK_ON_CONNECT = action
    return True

  def register_on_disconnect(self, action = None):
    self.CALLBACK_ON_DISCONNECT = action
    return True

  def register_on_data(self, action = None):
    self.CALLBACK_ON_DATA = action
    return True

  def _listen(self):
    while self.is_running:
      # Wait for connection
      client, remote_addr = self.sock.accept()
      client.settimeout(.0001)

      if (self.CALLBACK_ON_CONNECT != None):
        self.CALLBACK_ON_CONNECT(remote_addr[0])

      lastping = time.ticks_ms()
      while self.is_running and client != None:
        try:
          if (not hasattr("client", "read")):
            data = client.recv(1024).decode("ascii")
          else:
            data = client.read().decode("ascii")

          if data and len(data) > 0:
            if (self.CALLBACK_ON_DATA == None):
              continue

            self.CALLBACK_ON_DATA(repr(data))
            pass
          elif not data and client.fileno() == -1: break
          gc.collect()
        except Exception as err:
          pass
        
        time.sleep(.01)

        cur_ticks = time.ticks_ms()
        diff_ticks = cur_ticks - lastping
        if diff_ticks > 10000: # Every 10 seconds we ping / pong 
          try:
            client.send(b"ping")
          except Exception as err:
            break
          lastping = cur_ticks

      client.close()
      client = None
      if (self.CALLBACK_ON_DISCONNECT != None):
        self.CALLBACK_ON_DISCONNECT(remote_addr[0])
    pass

