APP_NAME="tetris_cz19_multiplayer"

import sys
# We would like to import modules that are added to his folder.
sys.path.append("/apps/" + APP_NAME)

import menu
import tetris

role=""
hostsettings="survivor"

tetrismenu = menu.TetrisMenu()

mode=tetrismenu.main()
if mode=="multiplayer":
  role=tetrismenu.multiplayer()
  if role=="host":
    hostsettings=tetrismenu.hostsettings()

print(mode,role)
tetrisgame = tetris.Tetris(mode,role,hostsettings)
tetrisgame.start()

