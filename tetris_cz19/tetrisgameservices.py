import sys, time, gc
import gameservices

ON_BADGE = "wifi" in sys.modules 

try:
  import thread
except ImportError:
  import _thread as thread

try:
  import random
except ImportError:
  import urandom as random
 
class TetrisGameHost:
  """Tetris Game host for interaction with a TetrisGameClient"""

  def __init__(self): 
    self.game_host = gameservices.GameHost()
    self.CALLBACK_ON_CONNECT = None 
    self.CALLBACK_ON_DISCONNECT = None 
    self.CALLBACK_ON_ROW = None
    self.CALLBACK_ON_GAMEOVER = None
    self.game_host.register_on_connect(self._callback_on_connect)
    self.game_host.register_on_disconnect(self._callback_on_disconnect)
    self.game_host.register_on_data(self._callback_on_data)
    self.network_type = gameservices.GAME_HOST_NETWORK_TYPE_NORMAL
    pass

  def start(self):
    self.game_host.network_type = self.network_type
    self.game_host.start()

  def stop(self):
    self.game_host.stop()
    pass

  def register_on_connect(self, action = None):
    self.CALLBACK_ON_CONNECT = action
    return True

  def register_on_disconnect(self, action = None):
    self.CALLBACK_ON_DISCONNECT = action
    return True

  def register_on_row(self, action = None):
    self.CALLBACK_ON_ROW = action
    return True

  def register_on_gameover(self, action = None):
    self.CALLBACK_ON_GAMEOVER = action
    return True

  def send_row_added(self):
    self.game_host.send_data("row")

  def send_gameover(self):
    self.game_host.send_data("gameover")

  def _callback_on_connect(self, addr):
    if (self.CALLBACK_ON_CONNECT != None):
      self.CALLBACK_ON_CONNECT(addr)

  def _callback_on_disconnect(self, addr):
    if (self.CALLBACK_ON_DISCONNECT != None):
      self.CALLBACK_ON_DISCONNECT(addr)

  def _callback_on_data(self, data):
    if (data == "ping"):
      return True
    if ((data == "row" or data == "row\r\n" or data == "'row'" or data == "'row\\r\\n'") and self.CALLBACK_ON_ROW != None):
      self.CALLBACK_ON_ROW()
      return True
    if ((data == "gameover" or data == "gameover\r\n"  or data == "'gameover'" or data == "'gameover\\r\\n'") and self.CALLBACK_ON_ROW != None):
      self.CALLBACK_ON_GAMEOVER()
      return True


class TetrisGameClient:
  """Tetris Game client for interaction with a TetrisGameHost"""

  def __init__(self): 
    self.game_client = gameservices.GameClient()
    self.CALLBACK_ON_CONNECT = None 
    self.CALLBACK_ON_DISCONNECT = None 
    self.CALLBACK_ON_ROW = None
    self.CALLBACK_ON_GAMEOVER = None
    self.game_client.register_on_connect(self._callback_on_connect)
    self.game_client.register_on_disconnect(self._callback_on_disconnect)
    self.game_client.register_on_data(self._callback_on_data)
    self.network_type = gameservices.GAME_CLIENT_NETWORK_TYPE_NORMAL
    pass

  def start(self, ip_address):
    self.game_client.network_type = self.network_type
    self.game_client.start(ip_address)

  def stop(self):
    self.game_client.stop()
    pass

  def register_on_connect(self, action = None):
    self.CALLBACK_ON_CONNECT = action
    return True

  def register_on_disconnect(self, action = None):
    self.CALLBACK_ON_DISCONNECT = action
    return True

  def register_on_row(self, action = None):
    self.CALLBACK_ON_ROW = action
    return True

  def register_on_gameover(self, action = None):
    self.CALLBACK_ON_GAMEOVER = action
    return True

  def send_row_added(self):
    self.game_client.send_data("row")
  
  def send_gameover(self):
    self.game_client.send_data("gameover")

  def _callback_on_connect(self, addr):
    if self.CALLBACK_ON_CONNECT != None and callable(self.CALLBACK_ON_CONNECT):
      self.CALLBACK_ON_CONNECT(addr)

  def _callback_on_disconnect(self, addr):
    if self.CALLBACK_ON_DISCONNECT != None and callable(self.CALLBACK_ON_DISCONNECT):
      self.CALLBACK_ON_DISCONNECT(addr)

  def _callback_on_data(self, data):
    if (data == "ping"):
      return True

    if ((data == "row" or data == "row\r\n" or data == "'row'" or data == "'row\\r\\n'") and self.CALLBACK_ON_ROW != None and callable(self.CALLBACK_ON_ROW)):
      self.CALLBACK_ON_ROW()
      return True

    if ((data == "gameover" or data == "gameover\r\n" or data == "'gameover'" or data == "'gameover\\r\\n'") and self.CALLBACK_ON_GAMEOVER != None and callable(self.CALLBACK_ON_GAMEOVER)):
      self.CALLBACK_ON_GAMEOVER()
      return True