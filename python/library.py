# -*-python-*-

import os

from ctypes import *

try:
  if os.name == 'posix':
    library = CDLL("./libclient.so")
  elif os.name == 'nt':
    library = CDLL("./client.dll")
  else:
    raise Exception("Unrecognized OS: "+os.name)
except OSError:
  raise Exception("It looks like you didn't build libclient. Run 'make' and try again.")

# commands

library.createConnection.restype = c_void_p
library.createConnection.argtypes = []

library.serverLogin.restype = c_int
library.serverLogin.argtypes = [c_void_p, c_char_p, c_char_p]

library.createGame.restype = c_int
library.createGame.argtypes = [c_void_p]

library.joinGame.restype = c_int
library.joinGame.argtypes = [c_void_p, c_int, c_char_p]

library.endTurn.restype = None
library.endTurn.argtypes = [c_void_p]

library.getStatus.restype = None
library.getStatus.argtypes = [c_void_p]

library.networkLoop.restype = c_int
library.networkLoop.argtypes = [c_void_p]

#Functions
library.pieceMove.restype = c_int
library.pieceMove.argtypes = [c_void_p, c_int, c_int, c_int]

# accessors

#Globals 
library.getTurnNumber.restype = c_int
library.getTurnNumber.argtypes = [c_void_p]

library.getPlayerID.restype = c_int
library.getPlayerID.argtypes = [c_void_p]

library.getGameNumber.restype = c_int
library.getGameNumber.argtypes = [c_void_p]

library.getTurnsToStalemate.restype = c_int
library.getTurnsToStalemate.argtypes = [c_void_p]

library.getMove.restype = c_void_p
library.getMove.argtypes = [c_void_p, c_int]

library.getMoveCount.restype = c_int
library.getMoveCount.argtypes = [c_void_p]

library.getPiece.restype = c_void_p
library.getPiece.argtypes = [c_void_p, c_int]

library.getPieceCount.restype = c_int
library.getPieceCount.argtypes = [c_void_p]

library.getPlayer.restype = c_void_p
library.getPlayer.argtypes = [c_void_p, c_int]

library.getPlayerCount.restype = c_int
library.getPlayerCount.argtypes = [c_void_p]

# getters

#Data
library.moveGetId.restype = c_int
library.moveGetId.argtypes = [c_void_p]

library.moveGetFromFile.restype = c_int
library.moveGetFromFile.argtypes = [c_void_p]

library.moveGetFromRank.restype = c_int
library.moveGetFromRank.argtypes = [c_void_p]

library.moveGetToFile.restype = c_int
library.moveGetToFile.argtypes = [c_void_p]

library.moveGetToRank.restype = c_int
library.moveGetToRank.argtypes = [c_void_p]

library.moveGetPromoteType.restype = c_int
library.moveGetPromoteType.argtypes = [c_void_p]

library.pieceGetId.restype = c_int
library.pieceGetId.argtypes = [c_void_p]

library.pieceGetOwner.restype = c_int
library.pieceGetOwner.argtypes = [c_void_p]

library.pieceGetFile.restype = c_int
library.pieceGetFile.argtypes = [c_void_p]

library.pieceGetRank.restype = c_int
library.pieceGetRank.argtypes = [c_void_p]

library.pieceGetHasMoved.restype = c_int
library.pieceGetHasMoved.argtypes = [c_void_p]

library.pieceGetType.restype = c_int
library.pieceGetType.argtypes = [c_void_p]

library.playerGetId.restype = c_int
library.playerGetId.argtypes = [c_void_p]

library.playerGetPlayerName.restype = c_char_p
library.playerGetPlayerName.argtypes = [c_void_p]

library.playerGetTime.restype = c_float
library.playerGetTime.argtypes = [c_void_p]


#Properties
