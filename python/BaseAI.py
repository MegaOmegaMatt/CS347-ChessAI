# -*- python -*-

from library import library

class BaseAI:
  """@brief A basic AI interface.

  This class implements most the code an AI would need to interface with the lower-level game code.
  AIs should extend this class to get a lot of builer-plate code out of the way
  The provided AI class does just that.
  """
  initialized = False
  iteration = 0
  runGenerator = None
  connection = None
  moves = []
  pieces = []
  players = []

  def startTurn(self):
    from GameObject import Move
    from GameObject import Piece
    from GameObject import Player

    BaseAI.moves = [Move(library.getMove(self.connection, i)) for i in xrange(library.getMoveCount(self.connection))]
    BaseAI.pieces = [Piece(library.getPiece(self.connection, i)) for i in xrange(library.getPieceCount(self.connection))]
    BaseAI.players = [Player(library.getPlayer(self.connection, i)) for i in xrange(library.getPlayerCount(self.connection))]

    if not self.initialized:
      self.initialized = True
      self.init()
    BaseAI.iteration += 1;
    if self.runGenerator:
      try:
        return self.runGenerator.next()
      except StopIteration:
        self.runGenerator = None
    r = self.run()
    if hasattr(r, '__iter__'):
      self.runGenerator = r
      return r.next()
    return r
  
  def turnNumber(self):
    return library.getTurnNumber(self.connection)

  def playerID(self):
    return library.getPlayerID(self.connection)

  def gameNumber(self):
    return library.getGameNumber(self.connection)

  def TurnsToStalemate(self):
    return library.getTurnsToStalemate(self.connection)

  def __init__(self, connection):
    self.connection = connection
