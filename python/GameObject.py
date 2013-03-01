# -*- python -*-

from library import library

from ExistentialError import ExistentialError

class GameObject(object):
  def __init__(self, ptr):
    from BaseAI import BaseAI
    self.ptr = ptr
    self.iteration = BaseAI.iteration


##A chess move
class Move(GameObject):
  def __init__(self, ptr):
    from BaseAI import BaseAI
    self.ptr = ptr
    self.iteration = BaseAI.iteration
    
    self.id = library.moveGetId(ptr)

  def validify(self):
    from BaseAI import BaseAI
    #if this class is pointing to an object from before the current turn it's probably
    #somewhere else in memory now
    if self.iteration == BaseAI.iteration:
      return True
    for i in BaseAI.moves:
      if i.id == self.id:
        self.ptr = i.ptr
        self.iteration = BaseAI.iteration
        return True
    raise ExistentialError()
  ##Unique Identifier
  def getId(self):
    self.validify()
    return library.moveGetId(self.ptr)

  ##The initial file location
  def getFromFile(self):
    self.validify()
    return library.moveGetFromFile(self.ptr)

  ##The initial rank location
  def getFromRank(self):
    self.validify()
    return library.moveGetFromRank(self.ptr)

  ##The final file location
  def getToFile(self):
    self.validify()
    return library.moveGetToFile(self.ptr)

  ##The final rank location
  def getToRank(self):
    self.validify()
    return library.moveGetToRank(self.ptr)

  ##The type of the piece for pawn promotion. Q=Queen, B=Bishop, N=Knight, R=Rook
  def getPromoteType(self):
    self.validify()
    return library.moveGetPromoteType(self.ptr)


  def __str__(self):
    self.validify()
    ret = ""
    ret += "id: %s\n" % self.getId()
    ret += "fromFile: %s\n" % self.getFromFile()
    ret += "fromRank: %s\n" % self.getFromRank()
    ret += "toFile: %s\n" % self.getToFile()
    ret += "toRank: %s\n" % self.getToRank()
    ret += "promoteType: %s\n" % self.getPromoteType()
    return ret

##A chess piece
class Piece(GameObject):
  def __init__(self, ptr):
    from BaseAI import BaseAI
    self.ptr = ptr
    self.iteration = BaseAI.iteration
    
    self.id = library.pieceGetId(ptr)

  def validify(self):
    from BaseAI import BaseAI
    #if this class is pointing to an object from before the current turn it's probably
    #somewhere else in memory now
    if self.iteration == BaseAI.iteration:
      return True
    for i in BaseAI.pieces:
      if i.id == self.id:
        self.ptr = i.ptr
        self.iteration = BaseAI.iteration
        return True
    raise ExistentialError()
  ##
  def move(self, file, rank, type):
    self.validify()
    return library.pieceMove(self.ptr, file, rank, type)

  ##Unique Identifier
  def getId(self):
    self.validify()
    return library.pieceGetId(self.ptr)

  ##The owner of the piece
  def getOwner(self):
    self.validify()
    return library.pieceGetOwner(self.ptr)

  ##The letter this piece is at (1-8)
  def getFile(self):
    self.validify()
    return library.pieceGetFile(self.ptr)

  ##The number this piece is at (1-8)
  def getRank(self):
    self.validify()
    return library.pieceGetRank(self.ptr)

  ##1=has moved, 0=has not moved
  def getHasMoved(self):
    self.validify()
    return library.pieceGetHasMoved(self.ptr)

  ##The letter that describes this piece's type. K=King, Q=Queen, B=Bishop, N=Knight, R=Rook, P=Pawn
  def getType(self):
    self.validify()
    return library.pieceGetType(self.ptr)


  def __str__(self):
    self.validify()
    ret = ""
    ret += "id: %s\n" % self.getId()
    ret += "owner: %s\n" % self.getOwner()
    ret += "file: %s\n" % self.getFile()
    ret += "rank: %s\n" % self.getRank()
    ret += "hasMoved: %s\n" % self.getHasMoved()
    ret += "type: %s\n" % self.getType()
    return ret

##
class Player(GameObject):
  def __init__(self, ptr):
    from BaseAI import BaseAI
    self.ptr = ptr
    self.iteration = BaseAI.iteration
    
    self.id = library.playerGetId(ptr)

  def validify(self):
    from BaseAI import BaseAI
    #if this class is pointing to an object from before the current turn it's probably
    #somewhere else in memory now
    if self.iteration == BaseAI.iteration:
      return True
    for i in BaseAI.players:
      if i.id == self.id:
        self.ptr = i.ptr
        self.iteration = BaseAI.iteration
        return True
    raise ExistentialError()
  ##Unique Identifier
  def getId(self):
    self.validify()
    return library.playerGetId(self.ptr)

  ##Player's Name
  def getPlayerName(self):
    self.validify()
    return library.playerGetPlayerName(self.ptr)

  ##Time remaining, updated at start of turn
  def getTime(self):
    self.validify()
    return library.playerGetTime(self.ptr)


  def __str__(self):
    self.validify()
    ret = ""
    ret += "id: %s\n" % self.getId()
    ret += "playerName: %s\n" % self.getPlayerName()
    ret += "time: %s\n" % self.getTime()
    return ret
