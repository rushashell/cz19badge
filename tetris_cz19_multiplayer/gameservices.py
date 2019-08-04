import sys, time, gc, wifi_extended, badgehelper

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

if badgehelper.on_badge():
  import wifi, consts, network, uinterface

PORT = 55667        # Port to listen on (non-privileged ports are > 1023)

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
    if not badgehelper.on_badge():
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
    self.use_listener = False

    # Callbacks 
    self.CALLBACK_ON_CONNECT = None 
    self.CALLBACK_ON_DISCONNECT = None 
    self.CALLBACK_ON_DATA = None 
    
    random.seed(time.ticks_ms())
    self.client = None
    pass

  def start(self):
    switched = self.network_switcher.switch(self.network_type)
    if not switched:
      return False 

    addr = socket.getaddrinfo("0.0.0.0", self.port)[0][-1]
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    self.sock.bind(addr)
    
    self.sock.listen(1) # Only allow one single connection at a time
    self.sock.settimeout(None)
    
    if self.use_listener:
      if badgehelper.on_badge():
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
  
  def wait_for_connection(self):
    # we wait for a connection, so show a waiting icon...
    wifi_extended.animate_wifi()
    self.client, remote_addr = self.sock.accept()
    self.client.settimeout(0.01)
    wifi_extended.animate_end()
    self.is_connected = True

  def disconnect(self):
    if self.client:
      self.client.close()
      self.client = None
      self.is_connected = False

  def read_data(self):
    data = []

    if not self.is_connected or not self.is_running:
      return data

    if badgehelper.on_badge() or 1 == 0:
      try:
        data = self.client.read()
      except OSError as err: # timeout 
        pass
      except Exception as err:
        print("exception when receiving data from client:")
        print(err)
        self.disconnect()
    else:
      try:
        data = self.client.recv(self.buffer_size)
      except OSError as err: # timeout
        pass
      except Exception as err:
          print("exception when receiving data from client:")
          print(err)
          self.disconnect()
     
    if self.client.fileno() == -1: 
      self.is_connected = False 

    if type(data) == bytes:
      return data.decode("ascii")
    else:
      return data
    
  def send_data(self, data):
    if (not self.is_running or self.client == None or not self.is_connected):
      return False 

    to_send = None
    if type(data) == str:
      to_send = data.encode("ascii")
    else:
      to_send = data

    #print("sending data to client: " + to_send.decode("ascii"))
    
    try:
      if badgehelper.on_badge():
        self.client.write(to_send)
      else:
        self.client.send(to_send)
      return True 
    except OSError as err: # Timeout
      print("Timeout exception when sending data to client:")
      print(type(err))
      print(err)
      self.is_connected = False
      return False 
    except Exception as err:
      print("exception when sending data to client:")
      print(type(err))
      print(err)
      self.is_connected = False
      return False 


  def _listen(self):
    self.wait_for_connection()    

    if self.CALLBACK_ON_CONNECT != None and callable(self.CALLBACK_ON_CONNECT):
      self.CALLBACK_ON_CONNECT(remote_addr[0])

    while self.is_running and self.is_connected:
      time.sleep(.1)
      gc.collect()
     
      data = self.read_data()

      if not data:
        continue      

      if len(data) > 0 and not self.CALLBACK_ON_DATA == None and callable(self.CALLBACK_ON_DATA):
        #print("got data from client: " + data.decode("ascii"))
        self.CALLBACK_ON_DATA(data.decode("ascii"))

    if self.CALLBACK_ON_DISCONNECT != None and callable(self.CALLBACK_ON_DISCONNECT):
      self.CALLBACK_ON_DISCONNECT(remote_addr[0])

    self.disconnect()

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
    self.use_listener = False

    # Callbacks 
    self.CALLBACK_ON_CONNECT = None 
    self.CALLBACK_ON_DISCONNECT = None 
    self.CALLBACK_ON_DATA = None 

    random.seed(time.ticks_ms())
    self.client = None
    pass

  def start(self, ip_address):
    if (ip_address is None or ip_address == "" or len(ip_address) < 7):
      return False 

    switched = self.network_switcher.switch(self.network_type)
    if not switched:
      return False

    self.ip_address = ip_address
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.settimeout(.3)
    self.is_running = True 
    
    if self.use_listener:
      if badgehelper.on_badge():
        self.connect_thread = thread.start_new_thread("client_connect_thread", self._client_handler, ())
      else:
        self.connect_thread = thread.start_new_thread(self._client_handler, ())

  def stop(self):
    self.is_running = False
    pass
    
  def disconnect(self):
    if self.sock:
      self.sock.close()
      self.sock = None
      self.is_connected = False

  def wait_for_connection(self):
    # we wait for a connection, so show a waiting icon...
    if self.is_connected:
      return True 

    while not self.is_connected:
      time.sleep(.1)
      try:
        wifi_extended.animate_wifi()
        self.sock.connect((self.ip_address, self.port))
        wifi_extended.animate_end()
        self.is_connected = True
        return True 
      except:
        pass
        
      if not self.is_connected:
        # we should wait 10 seconds before going further 
        connect_ticks = time.ticks_ms()
        print("Could not connect. Waiting...")
        while True:
          time.sleep(.1)
          diff_ticks = time.ticks_ms() - connect_ticks
          if diff_ticks > 10000: # Every 10 seconds we try again
            continue

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
    if (not self.is_running or not self.is_connected):
      return False 

    to_send = None
    if type(data) == str:
      to_send = data.encode("ascii")
    else:
      to_send = data 

    #print("sending data to server: " + to_send.decode("ascii"))
    try:
      self.sock.send(to_send)
      return True
    except OSError as err: # also a timeout
      return False 
    except Exception as err:
      return False 


  def read_data(self):
    data = []

    if not self.is_connected or not self.is_running:
      return data

    if badgehelper.on_badge() and 1 == 0:
      try:
        data = self.sock.read()
      except OSError as err: # timeout 
        pass
      except Exception as err:
        print("exception when receiving data from host:")
        print(err)
        self.disconnect()
    else:
      try:
        data = self.sock.recv(self.buffer_size)
      except OSError as err: # timeout
        pass
      except Exception as err:
          print("exception when receiving data from host:")
          print(err)
          self.disconnect()
    
    if self.sock.fileno() == -1: 
      self.is_connected = False 

    if type(data) == bytes:
      return data.decode("ascii")
    else:
      return data

  def _client_handler(self):
    while self.is_running and not self.is_connected:
      self.wait_for_connection()
      
      if self.CALLBACK_ON_CONNECT != None and callable(self.CALLBACK_ON_CONNECT):
        self.CALLBACK_ON_CONNECT(remote_addr[0])
    
    print("Connected to host: " + self.ip_address)
    while self.is_running and self.is_connected == True:
      data = self.read_data()
     
      if data and len(data) > 0 and not self.CALLBACK_ON_DATA == None and callable(self.CALLBACK_ON_DATA):
        self.CALLBACK_ON_DATA(data.decode("ascii"))

    self.is_running = False 
    self.is_connected = False 
    if self.CALLBACK_ON_DISCONNECT != None and callable(self.CALLBACK_ON_DISCONNECT):
      self.CALLBACK_ON_DISCONNECT(self.ip_address)
