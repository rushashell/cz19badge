import sys, time, gc, wifi_extended

ON_BADGE = "wifi" in sys.modules 

try:
  import thread
except ImportError:
  import _thread as thread

try:
  import socket
except ImportError:
  import _socket as socket

try:
  import random
except ImportError:
  import urandom as random

if ON_BADGE:
  import wifi, consts, network, uinterface

if (not hasattr("time", "ticks_ms")):
  try:
    time.ticks_ms = lambda: int(round(time.time() * 1000))
  except:
    pass

PORT = 55667        # Port to listen on (non-privileged ports are > 1023)
EOF = '\x04abcd'

GAME_HOST_NETWORK_TYPE_NORMAL = 0
GAME_HOST_NETWORK_TYPE_HOTSPOT = 1
GAME_CLIENT_NETWORK_TYPE_NORMAL = 10
GAME_CLIENT_NETWORK_TYPE_HOTSPOT = 11

GAME_NETWORK_TYPE_HOTSPOT_SSID = "AbC_MPCZ19"
GAME_NETWORK_TYPE_HOTSPOT_PASSWD = "Ajk39128asdaD"
GAME_NETWORK_TYPE_HOTSPOT_CHANNEL = 11 
GAME_NETWORK_TYPE_HOTSPOT_HIDDEN = False
GAME_NETWORK_TYPE_HOTSPOT_AUTHMODE = 2
GAME_NETWORK_TYPE_HOTSPOT_SERVERIP = "192.168.4.1"

BUFFER_SIZE = 64

class NetworkSwitcher:
  def switch(self, type):
    if not ON_BADGE:
      return True

    if type == GAME_HOST_NETWORK_TYPE_NORMAL or type == GAME_CLIENT_NETWORK_TYPE_NORMAL:
      if not wifi.status():
        print("Connecting to Wi-Fi...")
        return uinterface.connect_wifi()
    elif type == GAME_HOST_NETWORK_TYPE_HOTSPOT:
      return wifi_extended.hotspot_setup(GAME_NETWORK_TYPE_HOTSPOT_SSID, GAME_NETWORK_TYPE_HOTSPOT_CHANNEL, GAME_NETWORK_TYPE_HOTSPOT_HIDDEN, GAME_NETWORK_TYPE_HOTSPOT_PASSWD, GAME_NETWORK_TYPE_HOTSPOT_AUTHMODE)
    elif type == GAME_CLIENT_NETWORK_TYPE_HOTSPOT:
      return wifi_extended.hotspot_connect(GAME_NETWORK_TYPE_HOTSPOT_SSID, GAME_NETWORK_TYPE_HOTSPOT_PASSWD)

    pass

class GameHost:
  """Simple Game TCP listener with 3 events"""
  def __init__(self):
    self.port = PORT
    self.sock = None
    self.listen_thread = None
    self.is_running = False
    self.is_connected = False
    self.network_switcher = NetworkSwitcher()
    self.network_type = GAME_HOST_NETWORK_TYPE_NORMAL
    self.buffer_size = BUFFER_SIZE

    # Callbacks 
    self.CALLBACK_ON_CONNECT = None 
    self.CALLBACK_ON_DISCONNECT = None 
    self.CALLBACK_ON_DATA = None 

    random.seed(time.ticks_ms())
    self.client = None
    pass

  def start(self):
    gc.enable()

    switched = self.network_switcher.switch(self.network_type)
    if not switched:
      return False 

    addr = socket.getaddrinfo("0.0.0.0", self.port)[0][-1]
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    self.sock.bind(addr)
    
    self.sock.listen(1) # Only allow one single connection at a time
    #self.sock.settimeout(None)
    
    if ON_BADGE:
      self.listen_thread = thread.start_new_thread("listen_thread", self._listen, ())
    else:
      self.listen_thread = thread.start_new_thread(self._listen, ())
    self.is_running = True 

  def stop(self):
    self.is_connected = False
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

  def send_data(self, data):
    if (self.is_running and self.client != None and self.is_connected == True):
      try:
        to_send = None
        if type(data) == str:
          to_send = data.encode("ascii")
        else:
          to_send = data

        print("sending data to client: " + to_send.decode("ascii"))
        self.client.send(to_send)
        gc.collect()
        return True
      except Exception as err:
        print("exception when sending data to client:")
        print(type(err))
        print(err)
        self.is_connected = False

      return False 

  def _listen(self):
    global EOF
    
    try:
      while self.is_running:
        # we wait for a connection, so show a waiting icon...
        wifi_extended.animate_wifi()
        self.client, remote_addr = self.sock.accept()
        wifi_extended.animate_end()
        self.client.settimeout(.1)
        self.is_connected = True

        if self.CALLBACK_ON_CONNECT != None or not callable(self.CALLBACK_ON_CONNECT):
          self.CALLBACK_ON_CONNECT(remote_addr[0])

        lastping = time.ticks_ms()
        while self.is_running and self.client != None and self.is_connected == True:
          try:
            data = None
            if ON_BADGE:
              data = client.read().decode("ascii")
            else:
              data = self.client.recv(self.buffer_size).decode("ascii")

            if (not data or len(data) == 0) and self.client.fileno() == -1: break

            if data and len(data) > 0:
              if self.CALLBACK_ON_DATA == None or not callable(self.CALLBACK_ON_DATA):
                continue
              
              if data.endswith(EOF):
                data = data.replace(EOF, "", 1)

              self.CALLBACK_ON_DATA(data)
          
          except OSError as err: # timeout 
            pass
          except Exception as err:
            print("exception when receiving data from client:")
            print(err)
            self.is_connected = False
            break
        
          time.sleep(.1)
          gc.collect()

          cur_ticks = time.ticks_ms()
          diff_ticks = cur_ticks - lastping
          if diff_ticks > 30000: # Every 30 seconds we ping / pong 
            try:
              self.send_data("ping")
            except Exception as err:
              if not self.is_connected:
                break
            lastping = cur_ticks

        gc.collect()

        if self.CALLBACK_ON_DISCONNECT != None and callable(self.CALLBACK_ON_DISCONNECT):
          self.CALLBACK_ON_DISCONNECT(remote_addr[0])

        self.client.close()
        self.client = None
        self.is_connected = False
      pass
    except Exception as err:
      print("FATAL ERROR: ")
      print(err)
      pass 



class GameClient:
  """Simple Game TCP client with 3 events"""
  def __init__(self):
    self.port = PORT
    self.sock = None
    self.connect_thread = None
    self.is_running = False
    self.is_connected = False
    self.ip_address = None
    self.network_switcher = NetworkSwitcher()
    self.network_type = GAME_CLIENT_NETWORK_TYPE_NORMAL
    self.buffer_size = BUFFER_SIZE

    # Callbacks 
    self.CALLBACK_ON_CONNECT = None 
    self.CALLBACK_ON_DISCONNECT = None 
    self.CALLBACK_ON_DATA = None 

    random.seed(time.ticks_ms())
    self.client = None
    pass

  def start(self, ip_address):
    gc.enable()

    if (ip_address is None or ip_address == "" or len(ip_address) < 7):
      return False 

    switched = self.network_switcher.switch(self.network_type)
    if not switched:
      return False

    self.ip_address = ip_address
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.settimeout(.1)
    
    if ON_BADGE:
      self.connect_thread = thread.start_new_thread("client_connect_thread", self._client_handler, ())
    else:
      self.connect_thread = thread.start_new_thread(self._client_handler, ())
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

  def send_data(self, data):
    global EOF

    if (self.is_running and self.is_connected == True):
      try:
        to_send = None
        if type(data) == str:
          to_send = data.encode("ascii")
        else:
          to_send = data 

        print("sending data to server: " + to_send.decode("ascii"))
        self.sock.send(to_send)
        gc.collect()
      except OSError as err: # also a timeout
        return False 
      except:
        return False 

  def _client_handler(self):
    try:
      while self.is_running:
      
        # Setup connection, if needed
        try:
          if not self.is_connected == True:
            wifi_extended.animate_wifi()
            self.sock.connect((self.ip_address, self.port))
            wifi_extended.animate_end()
            self.is_connected = True

            if self.CALLBACK_ON_CONNECT != None and callable(self.CALLBACK_ON_CONNECT):
              self.CALLBACK_ON_CONNECT(self.ip_address)

        except Exception as err:
          # we should wait 10 seconds before going further 
          connect_ticks = time.ticks_ms()
          while True:
            diff_ticks = time.ticks_ms() - connect_ticks
            if diff_ticks > 10000: # Every 10 seconds we try again
                continue

        lastping = time.ticks_ms()
        while self.is_running and self.is_connected == True:
          try:
            data = None
            if ON_BADGE:
              data = self.sock.read().decode("ascii")
            else:
              data = self.sock.recv(self.buffer_size).decode("ascii")

            gc.collect()
            if not data:
              break

            if (not data or len(data) == 0) and self.sock.fileno() == -1: break

            if data and len(data) > 0:
              if self.CALLBACK_ON_DATA == None or not callable(self.CALLBACK_ON_DATA):
                continue
              
              if data.endswith(EOF):
                data = data.replace(EOF, "", 1)

              self.CALLBACK_ON_DATA(data)
              pass

          except OSError as err:
            pass
          except:
            break
        
          time.sleep(.1)
          gc.collect()

          cur_ticks = time.ticks_ms()
          diff_ticks = cur_ticks - lastping
          if diff_ticks > 30000: # Every 30 seconds we ping / pong 
            try:
              self.send_data("ping")
            except Exception as err:
              break
            lastping = cur_ticks

        gc.collect()
        self.is_running = False 
        self.is_connected = False 
        if self.CALLBACK_ON_DISCONNECT != None and callable(self.CALLBACK_ON_DISCONNECT):
          self.CALLBACK_ON_DISCONNECT(self.ip_address)

      try:
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        gc.collect()
      except:
        pass

      pass
    except Exception as err:
      print("FATAL ERROR: ")
      print(type(err))
      print(err)
      pass