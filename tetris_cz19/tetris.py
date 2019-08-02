import time
import urandom 
import rgb
import gameservices
import tetrisgameservices


# Basic implementation of tetris, adapted to CZ19 badge

class Tetris:

    def __init__(self,mode="singleplayer",role="host"):
        defs = Defs()
        rgb.clear()
        self.mode=mode
        self.role=role
        self.font = "fixed_10x20"
        self.board_height = 8
        self.board_width = 32
        self.board_rotated = True
        self.board_color_background = defs.gray
        self.game_default_step_time = 500
        self.game_step_time = self.game_default_step_time
        self.game_step_speed_increase = 10
        self.game_width = 8 
        self.game_height = self.board_width - 5 
        self.game_blockedlines = 0
        # self.game_height = 10
        # self.game_color_piece = defs.white
        self.game_color_filledline = defs.blue
        self.game_color_addedline = defs.red
        self.game_color_blockedlines = defs.orange
        self.game_color_background = defs.black
        self.game_color_piece = [
           defs.white,
           defs.blue,
           defs.red,
           defs.yellow,
           defs.green,
           defs.purple,
           defs.cyan
        ]
        # self.game_linecolor = defs.white
        self.frame = []
        for i in range(256):
            self.frame+=[0]

        # nr of unique rotations per piece
        self.piece_rotations = [1, 2, 2, 2, 4, 4, 4]

        # Piece data: [piece_nr * 32 + rot_nr * 8 + brick_nr * 2 + j]
        # with rot_nr between 0 and 4
        # with the brick number between 0 and 4
        # and j == 0 for X coord, j == 1 for Y coord
        self.piece_data = [
            # pixel block
            0, 0, -1, 0, -1, -1, 0, -1, 
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,

            # line block
            0, 0, -2, 0, -1, 0, 1, 0,
            0, 0, 0, 1, 0, -1, 0, -2,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,

            # S-block
            0, 0, -1, -1, 0, -1, 1, 0, 
            0, 0, 0, 1, 1, 0, 1, -1, 
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,

            # Z-block
            0, 0, -1, 0, 0, -1, 1, -1, 
            0, 0, 1, 1, 1, 0, 0, -1, 
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,

            # L-block
            0, 0, -1, 0, -1, -1, 1, 0, 
            0, 0, 0, 1, 0, -1, 1, -1, 
            0, 0, -1, 0, 1, 0, 1, 1, 
            0, 0, -1, 1, 0, 1, 0, -1, 

            # J-block
            0, 0, -1, 0, 1, 0, 1, -1, 
            0, 0, 0, 1, 0, -1, 1, 1, 
            0, 0, -1, 1, -1, 0, 1, 0, 
            0, 0, 0, 1, 0, -1, -1, -1, 

            # T-block
            0, 0, -1, 0, 0, -1, 1, 0,  
            0, 0, 0, 1, 0, -1, 1, 0, 
            0, 0, -1, 0, 0, 1, 1, 0, 
            0, 0, -1, 0, 0, 1, 0, -1
        ]

        import buttons, defines
        # Controls are rotated to the left
        # UP button = left 
        # DOWN button = right 
        # RIGHT button = down 
        # LEFT button = up 

        def btn_a(button_is_down):
          if button_is_down:
              # self.rotate_piece()
              self.add_line()
              pass

        def btn_up(button_is_down):
          if button_is_down:
            if self.board_rotated:
              self.move_left()
            else:
              self.move_right()
            pass

        def btn_down(button_is_down):
          if button_is_down:
            if self.board_rotated:
              self.move_right()
            else:
              self.move_left()
            pass

        def btn_right(button_is_down):
          if button_is_down:
            if self.board_rotated:
              self.rotate_piece()
            else:
              self.lower_piece()
            pass

        def btn_left(button_is_down):
          if button_is_down:
            if self.board_rotated:
              self.lower_piece()
            else:
              self.rotate_piece()
            pass

        buttons.register(defines.BTN_A, btn_a)
        buttons.register(defines.BTN_UP, btn_up)
        buttons.register(defines.BTN_DOWN, btn_down)
        buttons.register(defines.BTN_LEFT, btn_left)
        buttons.register(defines.BTN_RIGHT, btn_right)

        self.client=None
        self.host=None
        self.connected=False
        if self.mode=="multiplayer":
          self.network_init()

        self.game_init()

        while True:
            time.sleep(.01)
            self.game_update()
            # self.draw()

    def multiplayer_on_connect(self,addr):
      self.connected = True
      print("(host) connected:" + addr)

    def multiplayer_on_disconnect(self,addr):
      self.connected = False
      print("(host) disconnected:" + addr)

    def multiplayer_on_row(self):
      print("(host) row added")
      self.add_line()
      # on row

    def multiplayer_on_gameover(self):
      print("(host) gameover")
      # on gameover

    def multiplayer_send_line(self):
      if self.role=="host":
        self.host.send_row_added()
      else:
        self.client.send_row_added()

    def network_init(self):
      if self.role=="host":
        self.host=tetrisgameservices.TetrisGameHost()
        self.host.register_on_connect(self.multiplayer_on_connect)
        self.host.register_on_disconnect(self.multiplayer_on_disconnect)
        self.host.register_on_row(self.multiplayer_on_row)
        self.host.register_on_gameover(self.multiplayer_on_gameover)
        self.host.network_type = gameservices.GAME_HOST_NETWORK_TYPE_HOTSPOT
        self.host.start()
      else:
        self.client = tetrisgameservices.TetrisGameClient()
        self.client.register_on_connect(self.multiplayer_on_connect)
        self.client.register_on_disconnect(self.multiplayer_on_disconnect)
        self.client.register_on_row(self.multiplayer_on_row)
        self.client.register_on_gameover(self.multiplayer_on_gameover)
        self.client.network_type = gameservices.GAME_CLIENT_NETWORK_TYPE_HOTSPOT
        self.client.start(gameservices.GAME_NETWORK_TYPE_HOTSPOT_SERVERIP)
      while not(self.connected):
        time.sleep(0.1)

    def game_init(self):
        # Init game state
        self.game_step_time = self.game_default_step_time
        urandom.seed(time.ticks_ms())
        self.piece_next = urandom.getrandbits(8) % 7

        rgb.clear
        rgb.disablecomp()
        for i in range(256):
            self.frame[i]=0
        self.spawn_new_piece()
        self.field = [[0 for i in range(self.game_width)] for j in range(self.game_height)]
        self.last_update = time.ticks_ms()
        self.score = 0
        self.game_blockedlines = 0


    def spawn_new_piece(self):
        self.piece_current = self.piece_next
        urandom.seed(time.ticks_ms())
        self.piece_next = urandom.getrandbits(8) % 7
        # self.piece_current = 1
        self.piece_x = 4
        self.piece_y = 0
        self.piece_rot = 0
        # print("Piece:",self.piece_current)

    def game_update(self):
        cur_ticks = time.ticks_ms()
        if cur_ticks - self.last_update > self.game_step_time:
            # Move piece down
            self.lower_piece()
            self.last_update = cur_ticks

    def rotate_piece(self):
        self.piece_rot += 1
        if self.piece_rot >= self.piece_rotations[self.piece_current]:
            self.piece_rot = 0
        if self.is_right_collision():
          self.piece_x -= 1
        if self.is_left_collision():
          self.piece_x += 1
          # line piece needs additional step to the right:
          if (self.piece_current == 1) and (self.piece_x == 1):
            self.piece_x += 1
        self.draw()

    def is_side_collision(self):
        for pixel in range(4):
            x_off = self.piece_data[self.piece_current * 32 + self.piece_rot * 8 + pixel * 2 + 0]
            y_off = self.piece_data[self.piece_current * 32 + self.piece_rot * 8 + pixel * 2 + 1]

            abs_x = self.piece_x + x_off
            abs_y = self.piece_y + y_off

            # collision with walls
            if abs_x < 0 or abs_x > self.game_width-1:
                return True

            # collision with field blocks
            if self.field[abs_y][abs_x]:
                return True

        return False

    def is_left_collision(self):
        for pixel in range(4):
            x_off = self.piece_data[self.piece_current * 32 + self.piece_rot * 8 + pixel * 2 + 0]
            y_off = self.piece_data[self.piece_current * 32 + self.piece_rot * 8 + pixel * 2 + 1]

            abs_x = self.piece_x + x_off
            abs_y = self.piece_y + y_off

            # collision with walls
            if abs_x < 0:
                return True

            # collision with field blocks
            if self.field[abs_y][abs_x]:
                return True

        return False

    def is_right_collision(self):
        for pixel in range(4):
            x_off = self.piece_data[self.piece_current * 32 + self.piece_rot * 8 + pixel * 2 + 0]
            y_off = self.piece_data[self.piece_current * 32 + self.piece_rot * 8 + pixel * 2 + 1]

            abs_x = self.piece_x + x_off
            abs_y = self.piece_y + y_off

            # collision with walls
            if abs_x > self.game_width-1:
                return True

            # collision with field blocks
            if self.field[abs_y][abs_x]:
                return True

        return False


    def move_left(self):
        self.piece_x -= 1

        # check collision with walls
        if self.is_side_collision():
            self.piece_x += 1
        self.draw()

    def move_right(self):
        self.piece_x += 1

        # check collision with walls
        if self.is_side_collision():
            self.piece_x -= 1
        self.draw()


    def lower_piece(self):
        self.piece_y += 1

        # check for collisions
        collision = False
        for pixel in range(4):
            x_off = self.piece_data[self.piece_current * 32 + self.piece_rot * 8 + pixel * 2 + 0]
            y_off = self.piece_data[self.piece_current * 32 + self.piece_rot * 8 + pixel * 2 + 1]

            abs_x = self.piece_x + x_off
            abs_y = self.piece_y + y_off

            if abs_y > self.game_height-1 or self.field[abs_y][abs_x]:
                collision = True
                break

        if collision:
            # if at the top, game over
            if self.piece_y == 1:
                self.do_game_over()
                time.sleep(10)
                self.game_init()
                return

            # add to field
            self.piece_y -= 1
            for pixel in range(4):
                x_off = self.piece_data[self.piece_current * 32 + self.piece_rot * 8 + pixel * 2 + 0]
                y_off = self.piece_data[self.piece_current * 32 + self.piece_rot * 8 + pixel * 2 + 1]

                abs_x = self.piece_x + x_off
                abs_y = self.piece_y + y_off

                self.field[abs_y][abs_x] = True

            # check for line clears
            self.check_for_filled_lines()

            # Spawn new piece
            self.spawn_new_piece()
        self.draw()


    def check_for_filled_lines(self):
        for row in range(self.game_height-self.game_blockedlines):
            fill_count = 0
            for column in range(self.game_width):
                fill_count += self.field[row][column]
            if fill_count == self.game_width:
                # self.score += 10
                self.do_line()
                # Remove line
                self.remove_line(row)

    def remove_line(self,row):
        for col in range(self.game_width):
            self.draw_pixel(row,col,self.game_color_filledline)
        rgb.frame(self.frame)
        time.sleep(.5)
        for col in range(self.game_width):
            self.draw_pixel(row,col,self.game_color_background)
        rgb.frame(self.frame)
        time.sleep(.25)
         
        for row2 in range(row, 0, -1):
            for col in range(self.game_width):
                self.field[row2][col] = self.field[row2-1][col]
        if self.game_step_time > 50:
            self.game_step_time = self.game_step_time - self.game_step_speed_increase

    def add_line(self):
        for row in range(self.game_height-1):
            for col in range(self.game_width):
                self.field[row][col] = self.field[row+1][col]
        self.draw()
        for col in range(self.game_width):
            self.draw_pixel(self.game_height-1,col,self.game_color_addedline)
        rgb.frame(self.frame)
        time.sleep(.5)
        self.game_blockedlines+=1
        for col in range(self.game_width):
            self.field[self.game_height-1][col] = True
        
    def draw(self):
        self.draw_field()
        self.draw_piece_current()
        self.draw_piece_next()
        rgb.frame(self.frame)

    def draw_field(self):
        for row in range(self.game_height-self.game_blockedlines):
            for column in range(self.game_width):
                color = self.game_color_piece[0] if self.field[row][column] else self.game_color_background
                self.draw_pixel(row, column, color)
        for row in range(self.game_height-self.game_blockedlines,self.game_height):
            for column in range(self.game_width):
                color = self.game_color_blockedlines
                self.draw_pixel(row, column, color)
        for row in range(self.game_height,self.board_width):
            for column in range(self.game_width):
                color = self.board_color_background
                self.draw_pixel(row, column, color)

    def draw_piece_current(self):
        for pixel in range(4):
            # [piece_nr * 32 + rot_nr * 8 + brick_nr * 2 + j]
            x_off = self.piece_data[self.piece_current * 32 + self.piece_rot * 8 + pixel * 2 + 0]
            y_off = self.piece_data[self.piece_current * 32 + self.piece_rot * 8 + pixel * 2 + 1]

            abs_x = self.piece_x + x_off
            abs_y = self.piece_y + y_off

            self.draw_pixel(abs_y, abs_x, self.game_color_piece[self.piece_current])

    def draw_piece_next(self):
        for pixel in range(4):
            # [piece_nr * 32 + rot_nr * 8 + brick_nr * 2 + j]
            # skipping rotation, because is always 0 on next piece
            x_off = self.piece_data[self.piece_next * 32 + pixel * 2 + 0]
            y_off = self.piece_data[self.piece_next * 32 + pixel * 2 + 1]

            abs_x = 1 + x_off
            abs_y = 1 + y_off
            # line piece is special...
            if self.piece_next==1:
              abs_x += 1
              abs_y -= 1

            self.draw_pixel(abs_y, abs_x, self.game_color_piece[self.piece_next])


    def draw_pixel(self, row, column, color):
        if row < 0 or column < 0 or row > self.board_width-1 or column > self.board_height-1:
            return
        raw_x = (self.board_height-1 - column)
        raw_y = row
        if self.board_rotated:
          raw_x = self.board_height - 1 - raw_x
          raw_y = self.board_width - 1 - raw_y
        self.frame[raw_x * self.board_width + raw_y] = color

    def do_line(self):
        if self.mode=="multiplayer":
          print("Send line")
          self.multiplayer_send_line()

    def do_game_over(self):
        if self.mode=="multiplayer":
          print("Send gameover")
        rgb.enablecomp()
        rgb.clear()
        rgb.scrolltext("game over")

class Defs:
  def __init__(self):
    self.red    = 0xFF000000
    self.green  = 0x00FF0000
    self.blue   = 0x0000FF00
    self.purple = 0xFF00FF00
    self.yellow = 0xFFFF0000
    self.cyan   = 0x00FFFF00
    self.white  = 0xFFFFFF00
    self.black  = 0x00000000
    self.gray   = 0x30303000
    self.orange = 0xFFA50000

