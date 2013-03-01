##################################
# Utils.py By Matthew Terneus
# Updated 3/6/12
# Contains classes and utility functions to analyze a chess board
# This code is meant to interface with the 2012 SIG Game chess framework
##################################
from EvalHeuristics import *

#---------------------------------------------------------------------------------------------------------------

# Utility functions #

def isValidPos(tup):
    """Determines if a position is a valid place on the board
    Args:
    tup- a tuple containing rank,file coordinates
    Returns: bool- if position on board with 0-7 coords"""
    r,f = tup
    return r >= 0 and r < 8 and f >= 0 and f < 8

def toCoords(piece):
    """Creates coordinates of a chess peice
    Args:
    piece- a Piece or BetterPiece object
    Returns: tuple- containing rank,file coordinates from 0-7"""
    return(piece.getRank()-1,piece.getFile()-1)

def toAction(move,state):
    """Converts a Move object to an Action object
    Args:
    move- a Move object
    state- State that is converting the move to action
    Returns: Action object"""
    dest = (move.getToRank()-1,move.getToFile()-1)
    piece = state.getAtPos(dest)
    return Action(piece,dest)
    

#---------------------------------------------------------------------------------------------------------------

class Action:
    """Describes a potential chess move"""
    
    def __init__(self,piece,dest):
        """Constructs Action object
        Args:
        piece- a Piece or BetterPiece object
        dest- tuple of 0-7 rank,file coords"""
        self.piece = piece
        self.dest = dest

    def equals(self,other):
        """Check equivalence of two actions
        Args:
        other- an Action object
        Returns: boolean -true if equal"""
        #can't cause repetition on castling so if one action is castling then the other is not
        if self.piece == None or other.piece == None:
            return False
        return self.piece.getId() == other.piece.getId() and self.dest == other.dest

    def toStr(self):
        """Creates string representation of the action
        Returns: str"""
        if self.piece == None:
            (king,kpos),(rook,rpos) = self.dest
            r,f = kpos
            return "Castle K to " + chr(ord('A')+f) + str(r+1)
        r,f = self.dest
        return chr(self.piece.getType())+" "+ chr(ord('A')+self.piece.getFile()-1) +str(self.piece.getRank()) +" to "+ chr(ord('A')+f) + str(r+1)

    def execute(self,promote = 'Q'):
        """Preforms this action on the chess board
        This should be last method called before returning in the run method
        Args:
        promote- chr of pawn promotion(defaults to Queen)"""
        if self.piece == None:
            #recursive if handling a castle
            (king,kpos),(rook,rpos) = self.dest
            Action(king,kpos).execute()
        else:
            #issues move command on piece
            r,f = self.dest
            self.piece.move(f+1,r+1,ord(promote))
            

#--------------------------------------------------------------------------------------------------------------

class BetterPiece:
    """A master of disguise. Pretends to be the Piece class but contains additional functionality and can simulate potential moves"""
    
    def __init__(self,oldpiece):
        """Constructs BetterPiece object
        Args:
        oldpiece- the Piece that this piece is emulating or a BetterPiece to copy"""
        self.rank = oldpiece.getRank()
        self.file = oldpiece.getFile()
        self.owner = oldpiece.getOwner()
        self.moved = oldpiece.getHasMoved()
        self.ID = oldpiece.getId()
        self.type = oldpiece.getType()
        if isinstance(oldpiece,BetterPiece):
            self.original = oldpiece.original
        else:
            self.original = oldpiece

    def getOwner(self):
        """Gets Owner Id
        Returns: int- 0,1"""
        return self.owner

    def getFile(self):
        """Locates board file
        Returns: int- 1-8"""
        return self.file

    def getRank(self):
        """Locates board rank
        Returns: int- 1-8"""
        return self.rank

    def getHasMoved(self):
        """Gets if it has moved yet
        Returns: int- 0(No),1(Yes)"""
        return self.moved

    def getId(self):
        """Gets peice Id
        Returns: int"""
        return self.ID

    def getType(self):
        """Gets kind of piece
        Returns: int 0-255(use chr)"""
        return self.type

    def move(self,_file,rank,promote):
        """Tells server that this piece should be moved
        Args:
        _file -int 1-8 of destination file
        rank -int 1-8 of destination rank
        promote- int 0-255 of pawn promotion(use ord)"""
        self.original.move(_file,rank,promote)

    def setPos(self,tup):
        """simulates a potential move
        Args:
        tup - tuple rank,file coords 0-7"""
        r,f = tup
        self.rank = r+1
        self.file = f+1
        self.moved = 1
        

#--------------------------------------------------------------------------------------------------------------

class TransTable:
    def __init__(self):
        self.moves = dict()
        self.eval = dict()
        self.check = dict()

    def compress(self,state):
        string = str(state.turn)
        for i in state.board:
            for j in i:
                if j != None:
                    string += chr(j.getType())
                else:
                    string += " "
        return string

    def getMoves(self,state):
        key = self.compress(state)
        if key in self.moves:
            moves = self.moves[key]
            newmoves = []
            for each in moves:
                pos,dest = each
                newmoves.append(Action(state.getAtPos(pos),dest))
            return newmoves
        else:
            return None

    def setMoves(self,state,moves):
        key = self.compress(state)
        newmoves = []
        for each in moves:
            if each.piece == None:
                return False #Castling is funky so just don't save but regenerate moves in that case
            pos = toCoords(each.piece)
            dest = each.dest
            newmoves.append((pos,dest))
        self.moves[key] = newmoves

    def getCheck(self,state):
        key = self.compress(state)
        if key in self.check:
            return self.check[key]
        else:
            return None

    def setCheck(self,state,check):
        key = self.compress(state)
        self.check[key] = check

    def getEval(self,state):
        key = self.compress(state)
        if key in self.eval:
            return self.eval[key]
        else:
            return None

    def setEval(self,state,_eval):
        key = self.compress(state)
        self.eval[key] = _eval
        

#--------------------------------------------------------------------------------------------------------------

class State:
    """Describes a layout of a chess board"""
    heuristic = composite
    table = TransTable()
    def generateFromGameData(self,pieces,lastmoves,player,staleturns):
        """Creates a State from the list of pieces from the server
        Args:
        pieces- a list of Pieces
        lastmoves- list of 8 last moves
        player- player ID at move
        staleturns- int turns util 100 move stalemate"""
        #create empty board
        self.board = []
        self.black = []
        self.white = []
        self.stale = staleturns
        for i in range(8):
            self.board.append([None,None,None,None,None,None,None,None])
        for p in pieces:
            #replace piece objects with betterpiece objects
            p = BetterPiece(p)
            #sort pieces into lists
            if p.getOwner()== 0:
                self.white.append(p)
            else:
                self.black.append(p)
            #place pieces on the board
            r,f = toCoords(p)
            self.board[r][f] = p

        self.turn = player
        self.quiet = True
        self.lastmoves = []
        self.lastrank = []
        i = 0
        for each in lastmoves:
            self.lastmoves.append(toAction(each,self))
            self.lastrank.append(each.getFromRank()-1)
            i += 1
            if i == 9:
                break

    def getAtPos(self,tup):
        """Finds the pieces at at board position
        Args:
        tup- tuple of rank,file coords 0-7
        Returns: BetterPiece"""
        r,f = tup
        return self.board[r][f]

    def move(self,action):
        """Simulates a potential move
        Args:
        action- Action object of move that should be taken
        Returns: State- board after move have been made"""
        # creates a copy of the board and lists
        newboard = [row[:] for row in self.board]
        newwhite = self.white[:]
        newblack = self.black[:]
        quiet = True
        
        #record of last rank for enpassent
        temprank = -1
        #checks if should update turns to stalemate
        refresh = False
        if action.piece == None:
            (king,kpos),(rook,rpos) = action.dest
            quiet = False
            #king
            #Clear board of piece's last pos
            r,f = toCoords(king)
            newboard[r][f] = None
            temprank = r
            #copy piece and place at new pos
            r,f = kpos
            newking = BetterPiece(king)
            newboard[r][f] = newking
            newking.setPos(kpos)
            #rook
            #Clear board of piece's last pos
            r,f = toCoords(rook)
            newboard[r][f] = None
            #copy piece and place at new pos
            r,f = rpos
            newrook = BetterPiece(rook)
            newboard[r][f] = newrook
            newrook.setPos(rpos)
            #update peice list
            if newking.getOwner()==0:
                newwhite.remove(rook)
                newwhite.remove(king)
                newwhite.append(newrook)
                newwhite.append(newking)
            else:
                newblack.remove(rook)
                newblack.remove(king)
                newblack.append(newrook)
                newblack.append(newking)
            
        else:
            #record potential capture
            capture = self.getAtPos(action.dest)
            #Clear board of peice's last pos
            oldr,oldf = toCoords(action.piece)
            newboard[oldr][oldf] = None
            temprank = oldr
            #copy piece and place at new pos
            r,f = action.dest
            newpiece = BetterPiece(action.piece)
            if chr(action.piece.getType()) == 'P':
                refresh = True
                if (r == 0 or r == 7):
                    # promote
                    newpiece.type = ord('Q')
                    quiet = False
                #enpassent (change file without landing on a piece)
                if capture == None and oldf != f:
                    #captured piece is actually at the old rank and the new file
                    capture = self.getAtPos((oldr,f))
            newboard[r][f] = newpiece
            newpiece.setPos(action.dest)
            # update piece list
            if newpiece.getOwner() == 0:
                newwhite.remove(action.piece)
                newwhite.append(newpiece)
            else:
                newblack.remove(action.piece)
                newblack.append(newpiece)
            #remove capture from list
            if capture != None:
                quiet = False
                refresh = True
                if capture.getOwner()==0:
                    newwhite.remove(capture)
                else:
                    newblack.remove(capture)

        #put data in new state object
        newstate = State()
        newstate.board = newboard
        newstate.white = newwhite
        newstate.black = newblack
        newstate.quiet = quiet

        #update last move data
        newstate.lastmoves = [action] + self.lastmoves
        newstate.lastrank = [temprank] + self.lastrank
        
        # toggle turn
        newstate.turn = 1 - self.turn
        #count down or refresh 100 turns
        if refresh:
            newstate.stale = 100
        else:
            newstate.stale = self.stale -1

        return newstate

    def termTest(self,player):
        """Checks if a state is a stalemate or not a terminal state
        Does not check for no moves stalemate
        Args:
        player- Player to find utility value for
        Returns: float utility value"""
        if self.stale == 0:
            #ran out of moves
            return 0.5
        #check repetition
        if len(self.lastmoves) >= 8:
            repeat = True
            for i in [0,1,2,3]:
                if not self.lastmoves[i].equals(self.lastmoves[i+4]):
                    repeat = False
                    break
            if repeat:
                return 0.5
        rpqcount = 0 #count of rook pawn queen
        ncount = 0 #count of knights
        wbish = [0,0] #count of even/odd bishops
        bbish = [0,0]
        for p in self.white:
            if chr(p.getType()) == "P" or chr(p.getType()) == "R" or chr(p.getType()) == "Q":
                rpqcount += 1
            if chr(p.getType()) == "N":
                ncount += 1
            if chr(p.getType()) == "B":
                r,f = toCoords(p)
                wbish[(r+f)%2] += 1
        for p in self.black:
            if chr(p.getType()) == "P" or chr(p.getType()) == "R" or chr(p.getType()) == "Q":
                rpqcount += 1
            if chr(p.getType()) == "N":
                ncount += 1
            if chr(p.getType()) == "B":
                r,f = toCoords(p)
                bbish[(r+f)%2] += 1
        # cases that are not a stalemate
        if rpqcount > 0 or ncount > 1 or (ncount > 0 and wbish[0]+wbish[1]+bbish[0]+bbish[1] > 0):
            return -1
        if (wbish[0] > 0 and bbish[1] > 0) or (wbish[1] > 0 and bbish[0] > 0):
            return -1
        # stalemate by material
        return 0.5
        
    def evaluate(self,player):
        """Estimates the current Utility value of this state using the heuristic specified in the static varible
        Args:
        player- player to estimate for
        Returns: float -estimated utility value (0.0-1.0)
        """
        history = State.table.getEval(self)
        if history == None:
            new = State.heuristic(self,player)
            State.table.setEval(self,new)
            return new
        else:
            return history

    def isInCheck(self,player):
        """Determines if the player is in check on this board
        Args:
        player- Id 0,1 of the player to find check for
        Returns: bool- True if in check"""
        if player == 0:
            mypieces = self.white
            direction = 1
        else:
            mypieces = self.black
            direction = -1

        r = -1
        f = -1
        # get king position
        for p in mypieces:
            if chr(p.getType()) == 'K':
                r,f =toCoords(p)

        # check queens rooks and bishops
        for i in range(1,9):
            pos = (r+i,f+i)
            if isValidPos(pos):
                if self.getAtPos(pos) != None:
                    if self.getAtPos(pos).getOwner() != player and (chr(self.getAtPos(pos).getType()) == 'B' or chr(self.getAtPos(pos).getType()) == 'Q'):
                        return True
                    else:
                        break
            else:
                break
                
        for i in range(1,9):
            pos = (r-i,f+i)
            if isValidPos(pos):
                if self.getAtPos(pos) != None:
                    if self.getAtPos(pos).getOwner() != player and (chr(self.getAtPos(pos).getType()) == 'B' or chr(self.getAtPos(pos).getType()) == 'Q'):
                        return True
                    else:
                        break
            else:
                break
        for i in range(1,9):
            pos = (r+i,f-i)
            if isValidPos(pos):
                if self.getAtPos(pos) != None:
                    if self.getAtPos(pos).getOwner() != player and (chr(self.getAtPos(pos).getType()) == 'B' or chr(self.getAtPos(pos).getType()) == 'Q'):
                        return True
                    else:
                        break
            else:
                break
        for i in range(1,9):
            pos = (r-i,f-i)
            if isValidPos(pos):
                if self.getAtPos(pos) != None:
                    if self.getAtPos(pos).getOwner() != player and (chr(self.getAtPos(pos).getType()) == 'B' or chr(self.getAtPos(pos).getType()) == 'Q'):
                        return True
                    else:
                        break
            else:
                break
        for i in range(1,9):
            pos = (r+i,f)
            if isValidPos(pos):
                if self.getAtPos(pos) != None:
                    if self.getAtPos(pos).getOwner() != player and (chr(self.getAtPos(pos).getType()) == 'R' or chr(self.getAtPos(pos).getType()) == 'Q'):
                        return True
                    else:
                        break
            else:
                break
        for i in range(1,9):
            pos = (r-i,f)
            if isValidPos(pos):
                if self.getAtPos(pos) != None:
                    if self.getAtPos(pos).getOwner() != player and (chr(self.getAtPos(pos).getType()) == 'R' or chr(self.getAtPos(pos).getType()) == 'Q'):
                        return True
                    else:
                        break
            else:
                break
        for i in range(1,9):
            pos = (r,f+i)
            if isValidPos(pos):
                if self.getAtPos(pos) != None:
                    if self.getAtPos(pos).getOwner() != player and (chr(self.getAtPos(pos).getType()) == 'R' or chr(self.getAtPos(pos).getType()) == 'Q'):
                        return True
                    else:
                        break
            else:
                break
        for i in range(1,9):
            pos = (r,f-i)
            if isValidPos(pos):
                if self.getAtPos(pos) != None:
                    if self.getAtPos(pos).getOwner() != player and (chr(self.getAtPos(pos).getType()) == 'R' or chr(self.getAtPos(pos).getType()) == 'Q'):
                        return True
                    else:
                        break
            else:
                break
        
        #Pawns
        moves = []
        moves.append((r+direction,f-1)) #attack from left
        moves.append((r+direction,f+1)) #attack from right

        for pos in moves:
            if isValidPos(pos) and self.getAtPos(pos) != None and self.getAtPos(pos).getOwner() != player and chr(self.getAtPos(pos).getType()) == 'P':
                return True

        #knights
        moves = []
        moves.append((r+2,f+1))
        moves.append((r+2,f-1))
        moves.append((r+1,f+2))
        moves.append((r+1,f-2))
        moves.append((r-1,f+2))
        moves.append((r-1,f-2))
        moves.append((r-2,f+1))
        moves.append((r-2,f-1))

        for pos in moves:
            if isValidPos(pos) and self.getAtPos(pos) != None and self.getAtPos(pos).getOwner() != player and chr(self.getAtPos(pos).getType()) == 'N':
                return True
            
        # Kings
        moves = []
        moves.append((r+1,f+1))
        moves.append((r+1,f-1))
        moves.append((r-1,f+1))
        moves.append((r-1,f-1))
        moves.append((r+1,f))
        moves.append((r-1,f))
        moves.append((r,f+1))
        moves.append((r,f-1))

        for pos in moves:
            if isValidPos(pos) and self.getAtPos(pos) != None and self.getAtPos(pos).getOwner() != player and chr(self.getAtPos(pos).getType()) == 'K':
                return True

        #if passed all loops then its not in check
        return False

    def getMoves(self,player):
        history = State.table.getMoves(self)
        if history == None:
            new = self.getMovesManual(player)
            State.table.setMoves(self,new)
            return new
        else:
            return history   
         
    def getMovesManual(self,player):
        """Generates a list of all possible moves for a player
        Args:
        player- Id 0,1 of the player that is moving
        lastmove -Move object on the last move made (defined in GameObject.py)
        Returns: list- of all legal actions"""
        if player == 0:
            mypieces = self.white
            direction = 1
        else:
            mypieces = self.black
            direction = -1

        #vars for castling
        king = None
        rook1 = None
        rook2 = None
        #list to keep potential moves
        actions = []
            
        for p in mypieces:
            ID = chr(p.getType())
            r,f = toCoords(p)
            
            #Pawn Movement
            if ID == 'P':
                moves = []
                m1 = (r+direction,f) #move forward 1
                m2 = (r+2*direction,f) #move forward 2
                a1 = (r+direction,f-1) #attack to left
                a2 = (r+direction,f+1) #attack to right
                

                if isValidPos(m1) and self.getAtPos(m1) == None:
                    moves.append(m1)
                if isValidPos(m2) and self.getAtPos(m1) == None and self.getAtPos(m2) == None and p.getHasMoved() == 0:
                    moves.append(m2)
                if isValidPos(a1) and self.getAtPos(a1) != None and self.getAtPos(a1).getOwner() != player:
                    moves.append(a1)
                if isValidPos(a2) and self.getAtPos(a2) != None and self.getAtPos(a2).getOwner() != player:
                    moves.append(a2)
                for pos in moves:
                    actions.append(Action(p,pos))

            #Knight Movement
            if ID == 'N':
                moves = []
                moves.append((r+2,f+1))
                moves.append((r+2,f-1))
                moves.append((r+1,f+2))
                moves.append((r+1,f-2))
                moves.append((r-1,f+2))
                moves.append((r-1,f-2))
                moves.append((r-2,f+1))
                moves.append((r-2,f-1))

                for pos in moves:
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))

            #Rook Movement
            if ID == 'R':
                if rook1 == None:
                    rook1 = p
                else:
                    rook2 = p
                    
                for i in range(1,9):
                    pos = (r+i,f)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break #these breaks stop the current loop since you can't move through pices
                    else:
                        break 
                for i in range(1,9):
                    pos = (r-i,f)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r,f+i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r,f-i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                    
            #Bishop Movement
            if ID == 'B':
                for i in range(1,9):
                    pos = (r+i,f+i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r-i,f+i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r+i,f-i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r-i,f-i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break

            #Queen
            if ID == 'Q':
                for i in range(1,9):
                    pos = (r+i,f+i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r-i,f+i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r+i,f-i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r-i,f-i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r+i,f)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r-i,f)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r,f+i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r,f-i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
            #King
            if ID == 'K':
                king = p
                pos = (r+1,f+1)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                pos = (r-1,f+1)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                pos = (r+1,f-1)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                pos = (r-1,f-1)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                pos = (r+1,f)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                pos = (r-1,f)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                pos = (r,f+1)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                pos = (r,f-1)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                    
        #Passing
        #if there was a previous move, the move wasn't a castle and it was by a pawn
        if len(self.lastmoves) > 0 and self.lastmoves[0].piece != None and chr(self.lastmoves[0].piece.getType()) == 'P':
            r1 = self.lastrank[0]
            r2,f2 = self.lastmoves[0].dest
            if abs(r1-r2) == 2: #last move was two
                a1 = (r2,f2-1) #pass on left
                a2 = (r2,f2+1) #pass on right
                # is there space on left and a pawn in the space that belongs to me
                if isValidPos(a1) and self.getAtPos(a1) != None and self.getAtPos(a1).getOwner == player and chr(self.getAtPos(a1).getType()) == 'P': 
                    actions.append(Action(self.getAtPos(a1),(r2+dir,f2)))
                # is there space on right and a pawn in the space that belongs to me
                if isValidPos(a2) and self.getAtPos(a2) != None and self.getAtPos(a2).getOwner == player and chr(self.getAtPos(a2).getType()) == 'P':
                    actions.append(Action(self.getAtPos(a2),(r2+dir,f2)))

        #Castling
        if king != None and king.getHasMoved() == 0 and not self.isInCheck(player):
            kr,kf = toCoords(king)
            for rook in [rook1,rook2]:
                if rook != None and rook.getHasMoved() == 0:
                    rr,rf = toCoords(rook)
                    # castle right
                    if rf > kf and (not self.move(Action(king,(kr,kf+1))).isInCheck(player)):
                        clear = True
                        # check that no pieces are between the king and rook
                        for f in range(kf+1,rf):
                            if self.board[kr][f] != None:
                                clear = False
                        if clear:
                            kpos = (kr,kf+2)
                            rpos = (kr,kf+1)
                            # Special parameters for castling piece is none and destination holds parameters for two actions
                            actions.append(Action(None,((king,kpos),(rook,rpos))))
                    elif rf < kf and (not self.move(Action(king,(kr,kf-1))).isInCheck(player)):
                        # castle left
                        clear = True
                        # check that no pieces are between the king and rook
                        for f in range(rf+1,kf):
                            if self.board[kr][f] != None or self.move(Action(king,(kr,f))).isInCheck(player):
                                clear = False
                        if clear:
                            kpos = (kr,kf-2)
                            rpos = (kr,kf-1)
                            # Special parameters for castling piece is none and destination holds parameters for two actions
                            actions.append(Action(None,((king,kpos),(rook,rpos))))

        # Clean list of illegal moves
        i = 0
        while i < len(actions):
            if self.move(actions[i]).isInCheck(player):
                del actions[i]
            else:
                i = i+1
        return actions

    def getSimpleMoves(self,player):
        """Generates a rough list of moves, will contain some illegal moves
        For heuritic estimates
        Args:
        player- Id 0,1 of the player that is moving
        lastmove -Move object on the last move made (defined in GameObject.py)
        Returns: list- of all legal actions"""
        if player == 0:
            mypieces = self.white
            direction = 1
        else:
            mypieces = self.black
            direction = -1

        #list to keep potential moves
        actions = []
            
        for p in mypieces:
            ID = chr(p.getType())
            r,f = toCoords(p)
            
            #Pawn Movement
            if ID == 'P':
                moves = []
                m1 = (r+direction,f) #move forward 1
                m2 = (r+2*direction,f) #move forward 2
                a1 = (r+direction,f-1) #attack to left
                a2 = (r+direction,f+1) #attack to right
                

                if isValidPos(m1) and self.getAtPos(m1) == None:
                    moves.append(m1)
                if isValidPos(m2) and self.getAtPos(m1) == None and self.getAtPos(m2) == None and p.getHasMoved() == 0:
                    moves.append(m2)
                if isValidPos(a1) and self.getAtPos(a1) != None and self.getAtPos(a1).getOwner() != player:
                    moves.append(a1)
                if isValidPos(a2) and self.getAtPos(a2) != None and self.getAtPos(a2).getOwner() != player:
                    moves.append(a2)
                for pos in moves:
                    actions.append(Action(p,pos))

            #Knight Movement
            if ID == 'N':
                moves = []
                moves.append((r+2,f+1))
                moves.append((r+2,f-1))
                moves.append((r+1,f+2))
                moves.append((r+1,f-2))
                moves.append((r-1,f+2))
                moves.append((r-1,f-2))
                moves.append((r-2,f+1))
                moves.append((r-2,f-1))

                for pos in moves:
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))

            #Rook Movement                 
                for i in range(1,9):
                    pos = (r+i,f)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break #these breaks stop the current loop since you can't move through pices
                    else:
                        break 
                for i in range(1,9):
                    pos = (r-i,f)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r,f+i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r,f-i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                    
            #Bishop Movement
            if ID == 'B':
                for i in range(1,9):
                    pos = (r+i,f+i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r-i,f+i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r+i,f-i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r-i,f-i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break

            #Queen
            if ID == 'Q':
                for i in range(1,9):
                    pos = (r+i,f+i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r-i,f+i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r+i,f-i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r-i,f-i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r+i,f)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r-i,f)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r,f+i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
                for i in range(1,9):
                    pos = (r,f-i)
                    if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                        actions.append(Action(p,pos))
                        if self.getAtPos(pos) != None:
                            break
                    else:
                        break
            #King
            if ID == 'K':
                pos = (r+1,f+1)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                pos = (r-1,f+1)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                pos = (r+1,f-1)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                pos = (r-1,f-1)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                pos = (r+1,f)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                pos = (r-1,f)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                pos = (r,f+1)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                pos = (r,f-1)
                if isValidPos(pos) and (self.getAtPos(pos) == None or self.getAtPos(pos).getOwner() != player):
                    actions.append(Action(p,pos))
                    
        return actions
