APP_NAME="tetris_cz19_multiplayer"

import sys
# We would like to import modules that are added to his folder.
sys.path.append("/apps/" + APP_NAME)

import menu
import tetris

role=""

tetrismenu = menu.TetrisMenu()

mode=tetrismenu.main()
if mode=="multiplayer":
  role=tetrismenu.multiplayer()

print(mode,role)
tetrisgame = tetris.Tetris(mode,role)
tetrisgame.start()

