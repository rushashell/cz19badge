import sys

ON_BADGE = "wifi" in sys.modules 

if ON_BADGE:
  import wifi, network, rgb, uinterface

def animate_wifi():
  if not ON_BADGE:
    return False 

  from default_icons import animation_connecting_wifi
    
  rgb.clear()
  data, size, frames = animation_connecting_wifi
  rgb.framerate(3)
  rgb.gif(data, (12, 0), size, frames)

def animate_no_wifi():
  if not ON_BADGE:
    return False 
  
  from default_icons import icon_no_wifi
  
  rgb.clear()
  data, frames = icon_no_wifi
  rgb.framerate(3)
  rgb.gif(data, (12, 0), (8, 8), frames)
  time.sleep(3)

def animate_end():
  if not ON_BADGE:
    rgb.clear()
    rgb.framerate(20)

def hotspot_setup(ssid, channel, hidden, password, authmode):
  if not ON_BADGE:
    return False

  sta_if = network.WLAN(network.STA_IF)
  ap_if = network.WLAN(network.AP_IF)

  if sta_if.active():
    sta_if.active(False)
  
  ap_if.active(True)
  print("Creating HOTSPOT " + ssid + "...")
  animate_wifi()
  ap_if.config(essid=ssid, channel=channel, hidden=hidden, password=password, authmode=authmode)
  animate_end()
  return True 

def hotspot_connect(ssid, password):
  if not ON_BADGE:
    return False

  sta_if = network.WLAN(network.STA_IF)
  ap_if = network.WLAN(network.AP_IF)

  if ap_if.active():
    ap_if.active(False)
        
  sta_if.active(True)

  if not sta_if.isconnected():
    print("Connecting to HOTSPOT network " + ssid + "...")
    animate_wifi()
    sta_if.connect(ssid, password)
    wifi.wait()

    if not wifi.status():
      animate_no_wifi()

    animate_end()

  return wifi.status()   