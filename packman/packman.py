# pc 
# 8x8 pc man links
# #000000 | #000000 | #57002d | #ca0c79 | #ca0c79 | #57002d | #000000 | #000000
# #000000 | #7a264c | #ca247b | #ce007a | #ce007a | #ca247b | #7a264c | #000000

import time
import rgb, defines, buttons

class Pacman:
  # buttons 
  UP, DOWN, LEFT, RIGHT = defines.BTN_UP, defines.BTN_DOWN, defines.BTN_LEFT, defines.BTN_RIGHT
  A, B = defines.BTN_A, defines.BTN_B
  
  ## GLOBALS 
  current_x = 0
  current_direction = RIGHT
  current_speed = 0.5

  START_X = 0
  START_Y = 0
  MAX_X = 37
  MAX_Y = 0
  PAC_WIDTH = 8
  PAC_HEIGHT = 8
  
  PINK_GHOST_8x8_LEFT = [
    0x000000FF, 0x000000FF, 0x57002DFF, 0xCA0C79FF, 0xCA0C79FF, 0x57002DFF, 0x000000FF, 0x000000FF,
    0x000000FF, 0x7A264CFF, 0xCA247BFF, 0xCE007AFF, 0xCE007AFF, 0xCA247BFF, 0x7A264CFF, 0x000000FF,
    0x3D2731FF, 0xDECDD6FF, 0xEBD3DDFF, 0xD02780FF, 0xDECDD6FF, 0xEBD3DDFF, 0x7A0045FF, 0x000000FF,
    0x8F2567FF, 0x7291BDFF, 0xEDECF1FF, 0xCD488AFF, 0x748EBDFF, 0xECECF1FF, 0xD04787FF, 0xA1005CFF,
    0xCF0076FF, 0xD483A7FF, 0xDA8DACFF, 0xCE0076FF, 0xD481A6FF, 0xDA8EADFF, 0xCF007AFF, 0xCF007AFF,
    0xCE107CFF, 0xCE107CFF, 0xCE107CFF, 0xCE107CFF, 0xCE107CFF, 0xCE107CFF, 0xCE107CFF, 0xCE107CFF,
    0xD00A7DFF, 0xB60A6DFF, 0xD00A7DFF, 0xB60A6DFF, 0xB60A6DFF, 0xD00A7DFF, 0xB60A6DFF, 0xD00A7DFF,
    0xD00A7DFF, 0x000000FF, 0xD00A7DFF, 0xB60A6DFF, 0xB60A6DFF, 0xD00A7DFF, 0x000000FF, 0xD00A7DFF
  ]

  PINK_GHOST_8x8_RIGHT = [
    0x000000FF, 0x000000FF, 0x57002DFF, 0xCA0C79FF, 0xCA0C79FF, 0x57002DFF, 0x000000FF, 0x000000FF,
    0x000000FF, 0x7A264CFF, 0xCA247BFF, 0xCE007AFF, 0xCE007AFF, 0xCA247BFF, 0x7A264CFF, 0x000000FF,
    0x000000FF, 0x7A0045FF, 0xEBD3DDFF, 0xDECDD6FF, 0xD02780FF, 0xEBD3DDFF, 0xDECDD6FF, 0x3D2731FF,
    0xA1005CFF, 0xD04787FF, 0xECECF1FF, 0x748EBDFF, 0xCD488AFF, 0xEDECF1FF, 0x7291BDFF, 0x8F2567FF,
    0xCF007AFF, 0xCF007AFF, 0xDA8EADFF, 0xD481A6FF, 0xCE0076FF, 0xDA8DACFF, 0xD483A7FF, 0xCF0076FF,
    0xCE107CFF, 0xCE107CFF, 0xCE107CFF, 0xCE107CFF, 0xCE107CFF, 0xCE107CFF, 0xCE107CFF, 0xCE107CFF,
    0xD00A7DFF, 0xB60A6DFF, 0xD00A7DFF, 0xB60A6DFF, 0xB60A6DFF, 0xD00A7DFF, 0xB60A6DFF, 0xD00A7DFF,
    0xD00A7DFF, 0x000000FF, 0xD00A7DFF, 0xB60A6DFF, 0xB60A6DFF, 0xD00A7DFF, 0x000000FF, 0xD00A7DFF
  ]

  def __init__(self):
    self.current_x = 0
    self.init_buttons()
    pass
  
  @property
  def currentDirection(self):
    return self.current_direction

  @property
  def backgroundColor(self):
    return (0,0,0)

  def start(self):
    # reset background color
    rgb.background(self.backgroundColor)
    
    while True:
      time.sleep(.01)
      self.draw_ghost()
      sleep(self.current_speed)
  
      # set new position 
      if self.current_direction == self.LEFT and self.current_x > (self.START_X-self.PAC_WIDTH):
        self.current_x -= 1
        continue 
      elif self.current_direction == self.LEFT and self.current_x <= (self.START_X-self.PAC_WIDTH): 
        self.current_x = self.MAX_X
        continue
      elif self.current_direction == self.RIGHT and self.current_x >= self.MAX_X:
        self.current_x = self.START_X - (self.PAC_WIDTH)
        continue
      else:
        self.current_x += 1

  def init_buttons(self):
    # init button callbacks
    buttons.register(self.UP, self.input_up)
    buttons.register(self.DOWN, self.input_down)
    buttons.register(self.LEFT, self.input_left)
    buttons.register(self.RIGHT, self.input_right)
    buttons.register(self.A, self.input_a)
    #buttons.register(self.B, self.input_b)

  def input_left(self, pressed):
    if pressed:
      self.current_direction = self.LEFT
      pass

  def input_right(self, pressed):
    if pressed:
      self.current_direction = self.RIGHT
      pass

  def input_up(self, pressed):
    if pressed:
      if self.current_speed > 0.2:
        self.current_speed -= 0.05
        pass 

  def input_down(self, pressed):
    if pressed:
      if self.current_speed < 2:
        self.current_speed += 0.1
        pass

  def input_a(self, pressed):
    if pressed:
      pass
  
  def draw_ghost(self):
    rgb.clear()
    if self.current_direction == self.LEFT:
      rgb.image(self.PINK_GHOST_8x8_LEFT, (self.current_x,self.START_Y), (self.PAC_WIDTH,self.PAC_HEIGHT))
    else:
      rgb.image(self.PINK_GHOST_8x8_RIGHT, (self.current_x,self.START_Y), (self.PAC_WIDTH,self.PAC_HEIGHT))
