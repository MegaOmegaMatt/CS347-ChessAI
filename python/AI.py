############################################
# AI.py by SIG Game modified by Matthew Terneus
# Updated 3/9/12
# Controls the actions of a chess playing entity
############################################
from BaseAI import BaseAI
from GameObject import *
from Utils import *
from Minimax import *
from OrderHeuristics import HistoryTable
import time, math


import random

class AI(BaseAI):
  """The class implementing gameplay logic."""
  @staticmethod
  def username():
    return "Aperture Science"

  @staticmethod
  def password():
    return "GLaDOS"

  def init(self):
    self.table = HistoryTable()
    pass

  def end(self):
    pass

  def run(self):
    """Selects and moves a piece or pieces"""
    #capture time a start of turn
    truestarttime = time.clock()
    
    # Print out the current board state
    state = "+---+---+---+---+---+---+---+---+\n"
    for rank in range(8, 0, -1):
      state += "|"
      for file in range(1, 9):
        found = False
        for piece in self.pieces:
          # determines if that piece is at the current rank and file
          if piece.getRank() == rank and piece.getFile() == file:
            found = True
            # Checks if the piece is black
            if piece.getOwner() == 1:
              state += '*'
            else:
              state += ' '
            # prints the piece's type
            state += chr(piece.getType())+" "
        if not found:
          state += "   "
        state += "|"
      state += "\n+---+---+---+---+---+---+---+---+\n"
    print state
    
    # Looks through information about the players
    for player in self.players:
      # if playerID is 0, you're white, if its 1, you're black
      if player.getId() == self.playerID():
        mytime = player.getTime()

    turntime = mytime / math.floor(1+60.0*math.exp(-len(self.moves)/50.0)) #turn left est is 50e^(-t/50)
    
    print "Time total: ", mytime
    print "Time given: ",turntime
    print "Est moves to termination: ", math.floor(1+60.0*math.exp(-len(self.moves)/50.0))
    
    #create a state based off the game data from the server
    state = State()
    state.generateFromGameData(self.pieces,self.moves,self.playerID(),self.TurnsToStalemate())

    # est. branching factor
    turnmoves = len(state.getMoves(self.playerID()))
    print "Branching: ",turnmoves
    
    #capture time at start of iterative search
    starttime = time.clock()
    
    #finding solution at depth 1 since no matter what we need a solution to act on
    #a,b are -1,2 since eval returns number between 0 and 1
    value,action = abMinimax(state,self.playerID(),1,-1,2)
    i = 2

    #estimating that next iteration of minimax will take turnmoves times the sum of all previous minimax
    #(assuming a full tree with branching factor turnmoves)
    while (0.66*turnmoves*(time.clock()-starttime))+(starttime-truestarttime) < turntime:
      value,action = abQuiOrderMinimax(state,self.playerID(),i,math.floor(math.sqrt(i)),state.evaluate(self.playerID())-.15,2,self.table)
      i += 1
      
    print action.toStr()
    print "Estimate: ",value
    print "Depth: ", (i-1)
    print "Take taken: ", (time.clock()-truestarttime)
    action.execute()
    return 1

  def __init__(self, conn):
      BaseAI.__init__(self, conn)
