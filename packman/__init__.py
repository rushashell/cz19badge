BASE_MODULE = "packman"

import sys, time
# We would like to import modules that are added to his folder.
sys.path.append("/apps/" + BASE_MODULE)

import packman
game = packman.Pacman()
game.start()
