import time
import uinterface

class TetrisMenu():

  def __init__(self):
    print("init")
    self.menu = self._menu_main

  def main(self):
    self.menu = self._menu_main
    return self.menu()

  def multiplayer(self):
    self.menu = self._menu_multiplayer
    return self.menu()

  def hostsettings(self):
    self.menu = self._menu_hostsettings
    return self.menu()

  def _menu_main(self):
    items = ["Single player","Multiplayer"]
    choices = ["singleplayer","multiplayer"]
    choice = uinterface.menu(items)
    return choices[choice]

  def _menu_multiplayer(self):
    items = ["Host","Client"]
    choices = ["host","client"]
    choice = uinterface.menu(items)
    return choices[choice]

  def _menu_hostsettings(self):
    items = ["Survivor","Random lines"]
    choices = ["survivor","randomlines"]
    choice = uinterface.menu(items)
    return choices[choice]
