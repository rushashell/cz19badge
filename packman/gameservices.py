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
EOF = '\x04abcd'

class GameHost:
  """Simple Game TCP listener with 3 events"""
  def __init__(self):
    self.port = PORT
    self.sock = None
    self.listen_thread = None
    self.is_running = False
    self.is_connected = False
    
    # Callbacks 
    self.CALLBACK_ON_CONNECT = None 
    self.CALLBACK_ON_DISCONNECT = None 
    self.CALLBACK_ON_DATA = None 

    random.seed(time.ticks_ms())
    self.client = None
    pass

  def start(self):
    if "wifi" in sys.modules:
      wifi.connect()
      _  = wifi.wait()

    addr = socket.getaddrinfo("0.0.0.0", self.port)[0][-1]
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    self.sock.bind(addr)
    
    self.sock.listen(1) # Only allow one single connection at a time
    #self.sock.settimeout(None)

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
      self.client.settimeout(.0001)
      self.is_connected = True
      if (self.CALLBACK_ON_CONNECT != None):
        self.CALLBACK_ON_CONNECT(remote_addr[0])

      lastping = time.ticks_ms()
      while self.is_running and self.client != None and self.is_connected == True:
        try:
          if (not hasattr("client", "read")):
            data = self.client.recv(1024).decode("ascii")
          else:
            data = self.client.read().decode("ascii")

          if data and len(data) > 0:
            if (self.CALLBACK_ON_DATA == None):
              continue

            if data.endswith(EOF):
              data = data.replace(EOF, "")
            
            self.CALLBACK_ON_DATA(data)
            pass
          elif not data and self.client.fileno() == -1: break
          gc.collect()
        except Exception as err:
          if type(err) == ConnectionAbortedError:
            self.is_connected = False 
            break
          if type(err) == socket.timeout:
            #self.is_connected = False 
            #break
            pass
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

      self.client.close()
      self.client = None
      self.is_connected = False
      if (self.CALLBACK_ON_DISCONNECT != None):
        self.CALLBACK_ON_DISCONNECT(remote_addr[0])
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

    if "wifi" in sys.modules:
      wifi.connect()
      _  = wifi.wait()    
      
    self.ip_address = ip_address
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.settimeout(0.0001)

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
        if type(data) == str:
          if len(data) > 0 and data[len(data)-1] != EOF:
            data = data + EOF
          self.sock.sendall(data.encode("ascii"))
        else:
          if len(data) > 0 and data[len(data)-1] != EOF:
            data.append(EOF)
          self.sock.send(data)
      except Exception as err:
        if type(err) == socket.timeout:
          self.is_connected = False
          return False
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
          data = self.sock.recv(1024).decode("ascii")

          if data and len(data) > 0:
            if (self.CALLBACK_ON_DATA == None):
              continue

            if data.endswith(EOF):
              data = data.replace(EOF, "")

            self.CALLBACK_ON_DATA(data)
            pass
          elif not data and self.sock.fileno() == -1: break
          gc.collect()
        except socket.timeout:
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
