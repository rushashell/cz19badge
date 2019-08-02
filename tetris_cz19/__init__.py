APP_NAME="EWS99-Dev"

import sys
# We would like to import modules that are added to his folder.
sys.path.append("/apps/" + APP_NAME)
sys.path.append("/apps/tetris_cz19")

import menu
import tetris

role=""

tetrismenu = menu.TetrisMenu()

mode=tetrismenu.main()
if mode=="multiplayer":
  role=tetrismenu.multiplayer()

print(mode,role)
tetris = tetris.Tetris(mode,role)

