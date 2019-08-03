import time 

INIT = False
RUNNING_ON_BADGE = False

def on_badge():
  global INIT, RUNNING_ON_BADGE
  """Check if code is running on a Badge"""

  if not INIT:
    try:
      import wifi
      RUNNING_ON_BADGE = True
      INIT = True
    except:
      RUNNING_ON_BADGE = False
      INIT = True
      
  return RUNNING_ON_BADGE

# Add missing functionality on PC's python
if (not "ticks_ms" in dir(time)):
  try:
    time.ticks_ms = lambda: int(round(time.time() * 1000))
  except:
    pass