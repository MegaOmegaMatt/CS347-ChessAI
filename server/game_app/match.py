from base import *
from matchUtils import *
from objects import *
import networking.config.config
from collections import defaultdict
from networking.sexpr.sexpr import *
import os
import itertools
import scribe
from copy import deepcopy
import string

Scribe = scribe.Scribe

def loadClassDefaults(cfgFile = "config/defaults.cfg"):
  cfg = networking.config.config.readConfig(cfgFile)
  for className in cfg.keys():
    for attr in cfg[className]:
      setattr(eval(className), attr, cfg[className][attr])

class Match(DefaultGameWorld):
  def __init__(self, id, controller):
    self.id = int(id)
    self.controller = controller
    DefaultGameWorld.__init__(self)
    self.scribe = Scribe(self.logPath())
    self.addPlayer(self.scribe, "spectator")

    #TODO: INITIALIZE THESE!
    self.moves = 0
    self.turnNumber = 0
    self.playerID = 0
    self.gameNumber = id
    self.TurnsToStalemate = 100

  def addPlayer(self, connection, type="player"):
    connection.type = type
    if len(self.players) >= 2 and type == "player":
      return "Game is full"
    if type == "player":
      self.players.append(connection)
      try:
        self.addObject(Player, [connection.screenName, self.startTime])
      except TypeError:
        raise TypeError("Someone forgot to add the extra attributes to the Player object initialization")
    elif type == "spectator":
      self.spectators.append(connection)
      #If the game has already started, send them the ident message
      #TODO Figure out if this is actually supposed to be here
      #if (self.turn is not None):
      #  self.sendIdent([connection])
    return True

  def removePlayer(self, connection):
    if connection in self.players:
      if self.turn is not None:
        winner = self.players[1 - self.getPlayerIndex(connection)]
        self.declareWinner(winner, 'Opponent Disconnected')
      self.players.remove(connection)
    else:
      self.spectators.remove(connection)

  def start(self):
    if len(self.players) < 2:
      return "Game is not full"
    if self.winner is not None or self.turn is not None:
      return "Game has already begun"
    
    #TODO: START STUFF
    self.turn = self.players[-1]
    self.turnNumber = 0
    with open("config/initBoardState.txt",'r') as f:
      board = f.read().split()
    for rank, row in enumerate(board):
      for file, piece in enumerate(row):
        if piece != '.':
          self.addObject(Piece, [int(str.istitle(piece)), file+1, 8-rank, 0, ord(string.upper(piece))])

    self.nextTurn()
    return True


  def nextTurn(self):
    self.turnNumber += 1
    if self.turn == self.players[0]:
      self.turn = self.players[1]
      self.playerID = 1
    elif self.turn == self.players[1]:
      self.turn = self.players[0]
      self.playerID = 0

    else:
      return "Game is over."

    for obj in self.objects.values():
      obj.nextTurn()

    self.checkWinner()
    self.moves = 1
    if self.winner is None:
      self.sendStatus([self.turn] +  self.spectators)
    else:
      self.sendStatus(self.spectators)
    self.animations = ["animations"]
    return True

  def checkWinner(self):
    #TODO: Make this check if a player won, and call declareWinner with a player if they did
    #if they didn't make a move, they lose
    if self.moves != 0:
      message = ""
      if self.playerID == 0:
        message += "Black "
      else:
        message += "White "
      message += "failed to make a move!"
      self.declareWinner(self.players[self.playerID],message)
      return
    if self.TurnsToStalemate == 0:
      self.declareDraw("100 moves without a capture or pawn advancement, Stalemate!")
      return
    if len(self.objects.pieces) == 2:
      self.declareDraw("Only Kings Left, Stalemate!")
      return
    if len(self.objects.pieces) == 3:
      for p in self.objects.pieces:
        if p.type == ord('B'):
          self.declareDraw("With a King Vs a King and a Bishop it is impossible to checkmate, Stalemate!")
          return
        if p.type == ord('N'):
          self.declareDraw("With a King Vs a King and a Knight it is impossible to checkmate, Stalemate!")
          return
    if len(self.objects.pieces) == 4:
      bishops = filter(lambda piece: piece.type == ord('B'), self.objects.pieces)
      if len(bishops) == 2: #Exactly 2 bishops and 2 kings
        if bishops[0].owner != bishops[1].owner:# Opposite team
          if (bishops[0].file + bishops[0].rank) % 2 == (bishops[1].file + bishops[1].rank) % 2: # Same color
            self.declareDraw("With a King Bishop Vs King Bishop, with bishops on the same color, it is impossible to checkmate, Stalemate!")
            return

    stalemate = True
    bColor = -1
    for i in self.objects.pieces:
      if i.type != ord('K') and i.type != ord('B'):
        stalemate = False
        break
      if i.type is ord('B'):
        if bColor == -1:
          bColor = (i.rank+i.file)%2
        else:
          if (i.rank+i.file)%2 != bColor:
            stalemate = False
            break
    if stalemate is True:
      self.declareDraw("With only Kings and Bishops, with all of the Bishops on the same color, Checkmate is impossible, Stalemate!")
      return
    moveList = sorted(self.objects.moves, key=lambda X: X.id) #all moves, earlier in the array means later in the game
    moveList = [i.toList()[1:5] for i in reversed(moveList)] #we only care about the start and end positions
    if len(moveList) >= 8 and self.TurnsToStalemate <= 92:
      #print "Debugging info: " + `len(moveList[0])`+ ", " + `self.TurnsToStalemate` + `moveList[0:8]`
      if moveList[0:4] == moveList[4:8]:
        self.declareDraw("Board state repeated three times in a row, Stalemate Declared!")
        return

  def declareDraw(self, reason=''):
    self.winner = 'No one.'
    
    msg = ["game-winner", self.id, 'No one.', 2, reason]
    
    self.scribe.writeSExpr(msg)
    self.scribe.finalize()
    self.removePlayer(self.scribe)

    for p in self.players + self.spectators:
      p.writeSExpr(msg)

    self.sendStatus([self.turn])
    self.playerID ^= 1
    self.sendStatus([self.players[self.playerID]])
    self.playerID ^= 1
    self.turn = None

  def declareWinner(self, winner, reason=''):
    self.winner = winner
    self.sendStatus(self.spectators)
    msg = ["game-winner", self.id, self.winner.user, self.getPlayerIndex(self.winner), reason]
    self.scribe.writeSExpr(msg)
    self.scribe.finalize()
    self.removePlayer(self.scribe)

    for p in self.players + self.spectators:
      p.writeSExpr(msg)

    self.sendStatus([self.turn])
    self.playerID ^= 1
    self.sendStatus([self.players[self.playerID]])
    self.playerID ^= 1
    self.turn = None
    
  def logPath(self):
    return "logs/" + str(self.id) + ".glog"

  @derefArgs(Piece, None, None, None)
  def move(self, object, file, rank, type):
    return object.move(file, rank, type, )


  def sendIdent(self, players):
    if len(self.players) < 2:
      return False
    list = []
    for i in itertools.chain(self.players, self.spectators):
      list += [[self.getPlayerIndex(i), i.user, i.screenName, i.type]]
    for i in players:
      i.writeSExpr(['ident', list, self.id, self.getPlayerIndex(i)])

  def getPlayerIndex(self, player):
    try:
      playerIndex = self.players.index(player)
    except ValueError:
      playerIndex = -1
    return playerIndex

  def sendStatus(self, players):
    for i in players:
      i.writeSExpr(self.status())
      i.writeSExpr(self.animations)
    return True


  def status(self):
    msg = ["status"]

    msg.append(["game", self.turnNumber, self.playerID, self.gameNumber, self.TurnsToStalemate])

    typeLists = []
    typeLists.append(["Move"] + sorted([i.toList() for i in self.objects.values() if i.__class__ is Move], reverse = True))
    typeLists.append(["Piece"] + [i.toList() for i in self.objects.values() if i.__class__ is Piece])
    typeLists.append(["Player"] + [i.toList() for i in self.objects.values() if i.__class__ is Player])

    msg.extend(typeLists)

    return msg

  #checks if a  player is in check
  def inCheck(self,owner):
    temp = self.playerID
    temp2 = self.moves
    self.playerID = owner^1
    self.moves = 1
    king = [ i for i in self.objects.pieces if i.type == ord('K') and i.owner == owner][0]
    #print "Checking for Check!, King at Rank " + `king.rank` + " File " + `king.file`
    for i in self.objects.values():
      if isinstance(i,Piece) and i.owner is not owner:
        vMoveReturn = i.verifyMove(king.file,king.rank,ord('Q')) 
        # Kenneth Perry : if the file and rank are bad, why are you checking?
        if vMoveReturn == True and i.file != -1 and i.rank != -1:
          #print "Check! " + "Rank " + `i.rank` + " File " + `i.file`
          self.playerID = temp
          self.moves = temp2
          return True
        #else:
          #print vMoveReturn + " (" + chr(i.type) + " at " + `i.file`+ ","+ `i.rank`
    self.playerID = temp
    self.moves = temp2
    return False

  def noLegalMoves(self,owner):
    newGameState = deepcopy(self)
    newGameState.playerID = owner
    #print "Checking for a lack of legal moves!"
    for p in newGameState.objects.values():
      #print "There exist things in newGameState.objects"
      if isinstance(p,Piece) and p.owner == owner:
        for i in range(1,9):
          for j in range(1,9):
           # print "Checking  Rank " + `p.rank` + " to " + `i` + " File " + `p.file` + " to " + `j`
    
            if p.makeMove(j,i,ord('Q')) == True:
              #print "Get Out Of Check solution found!" + chr(p.type) + " at Rank " + `p.rank` + " to " + `i` + " File " + `p.file` + " to " + `j`
              return False
    #if no possible move gets out of check, then they are in checkmate
    return True


loadClassDefaults()

