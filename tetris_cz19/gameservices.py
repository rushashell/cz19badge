import sys, time, gc, wifi_extended

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
  import consts
except ImportError:
  pass

try:
  import network
except:
  pass

try:
  import uinterface
except ImportError:
  pass

try:
  import random
except ImportError:
  import urandom as random

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

GAME_NETWORK_TYPE_HOTSPOT_SSID = "TetrisCZ19"
GAME_NETWORK_TYPE_HOTSPOT_PASSWD = "Ajk39128asdaD"
GAME_NETWORK_TYPE_HOTSPOT_CHANNEL = 11 
GAME_NETWORK_TYPE_HOTSPOT_HIDDEN = False
GAME_NETWORK_TYPE_HOTSPOT_AUTHMODE = 2
GAME_NETWORK_TYPE_HOTSPOT_SERVERIP = "192.168.4.1"

class NetworkSwitcher:
  def switch(self, type):
    if not "wifi" in sys.modules or not "uinterface" in sys.modules:
      return True

    if type == GAME_HOST_NETWORK_TYPE_NORMAL or type == GAME_CLIENT_NETWORK_TYPE_NORMAL:
      if not wifi.status():
        print("Connecting to Wi-Fi...")
        return uinterface.connect_wifi()
    elif type == GAME_HOST_NETWORK_TYPE_HOTSPOT:
      return wifi_extended.hotspot_setup(GAME_NETWORK_TYPE_HOTSPOT_SSID, GAME_NETWORK_TYPE_HOTSPOT_CHANNEL, GAME_NETWORK_TYPE_HOTSPOT_HIDDEN, GAME_NETWORK_TYPE_HOTSPOT_PASSWD, GAME_NETWORK_TYPE_HOTSPOT_AUTHMODE)
    elif type == GAME_CLIENT_NETWORK_TYPE_HOTSPOT:
      return wifi_extended.hotspot_connect(GAME_NETWORK_TYPE_HOTSPOT_SSID, GAME_NETWORK_TYPE_HOTSPOT_PASSWD)

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
    #self.sock.settimeout(None)

    if "wifi" in sys.modules:
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
        if type(data) == str :
          if len(data) > 0 and data[len(data)-1] != EOF:
            data = data + EOF
          self.client.sendall(data.encode("ascii"))
          pass
        else:
          if len(data) > 0 and data[len(data)-1] != EOF:
            data.append(EOF)
          self.client.sendall(data)
      except Exception as err:
        if type(err) == ConnectionAbortedError:
          self.is_connected = False 
        if type(err) == ConnectionResetError:
          self.is_connected = False
        pass

  def _listen(self):
    while self.is_running:
      # Wait for connection
      self.client, remote_addr = self.sock.accept()
      self.client.settimeout(.1)
      self.is_connected = True
      if (self.CALLBACK_ON_CONNECT != None):
        self.CALLBACK_ON_CONNECT(remote_addr[0])

      lastping = time.ticks_ms()
      while self.is_running and self.client != None and self.is_connected == True:
        try:
          data = self.client.recv(64).decode("ascii")
          if (not data or len(data) == 0) and self.client.fileno() == -1: break

          if data and len(data) > 0:
            if (self.CALLBACK_ON_DATA == None):
              continue
              
            if data.endswith(EOF):
              data = data.replace(EOF, "")

            print(data)
            self.CALLBACK_ON_DATA(data)

          gc.collect()
        except OSError as err:
          pass
        except Exception as err:
          if type(err) == ConnectionAbortedError:
            self.is_connected = False 
            break
          pass
        
        time.sleep(.01)

        cur_ticks = time.ticks_ms()
        diff_ticks = cur_ticks - lastping
        if diff_ticks > 10000: # Every 10 seconds we ping / pong 
          try:
            self.send_data("ping")
          except Exception as err:
            if not self.is_connected:
              break
          lastping = cur_ticks

      if (self.CALLBACK_ON_DISCONNECT != None):
        self.CALLBACK_ON_DISCONNECT(remote_addr[0])

      self.client.close()
      self.client = None
      self.is_connected = False
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
    self.sock.settimeout(0.1)
    
    if "wifi" in sys.modules:
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
    if (self.is_running and self.is_connected == True):
      try:
        to_send = None
        if type(data) == str:
          if len(data) > 0 and data[len(data)-1] != EOF:
            data = data + EOF
          to_send = data.encode("ascii")
        else:
          if len(data) > 0 and data[len(data)-1] != EOF:
            data.append(EOF)
          to_send = data

        self.sock.send(to_send)
      except OSError as err:
        pass
      except:
        pass

  def _client_handler(self):
    while self.is_running:
      
      # Setup connection, if needed
      try:
        if not self.is_connected == True:
          self.sock.connect((self.ip_address, self.port))
          self.is_connected = True
          if (self.CALLBACK_ON_CONNECT != None):
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
          data = self.sock.recv(64).decode("ascii")
          if not data:
            break

          if (not data or len(data) == 0) and self.sock.fileno() == -1: break

          if data and len(data) > 0:
            if (self.CALLBACK_ON_DATA == None):
              continue
              
            if data.endswith(EOF):
              data = data.replace(EOF, "")

            self.CALLBACK_ON_DATA(data)
            pass

          gc.collect()
        except OSError as err:
          pass
        except:
          break
        
        time.sleep(.01)

        cur_ticks = time.ticks_ms()
        diff_ticks = cur_ticks - lastping
        if diff_ticks > 10000: # Every 10 seconds we ping / pong 
          try:
            self.send_data("ping")
          except Exception as err:
            break
          lastping = cur_ticks

      self.is_running = False 
      self.is_connected = False 
      if (self.CALLBACK_ON_DISCONNECT != None):
        self.CALLBACK_ON_DISCONNECT(self.ip_address)

    try:
      self.sock.shutdown(socket.SHUT_RDWR)
      self.sock.close()
    except:
      pass

    pass