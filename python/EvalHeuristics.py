##################################
# EvalHeuristics.py By Matthew Terneus
# Updated 3/7/12
# Contains methods to evaluate a state at a non terminal position
##################################

import random

def composite(state,player):
    """Takes linear combination of several heuritstics
    Args:
    state -State Object to eval
    player -Side to eval for
    Returns: int -rating (0-1) with 1 as winning"""
    tot = 0
    mat = getMaterial(state)
    pawn = pawnScore(state)
    tot += (0.45)*materialAdvantage(mat,player)
    tot += (0.45)*materialPercentage(mat,player)
    tot += (0.02)*pawnPercentage(pawn,player)
    tot += (0.02)*pawnStructure(pawn,player)
    tot += (0.05)*checkThreat(state,player)
    tot += (0.01)*randomify()
    #tot += (0.02)*coverage(state,player)
    return tot

def getMaterial(state):
    """Gets material scores
    Args:
    state -State Object to eval
    Returns: Tuple(int,int) -Material scores of each player"""
    whitescore = 0.0
    blackscore = 0.0
    for p in state.white:
        if chr(p.getType()) == 'P':
            whitescore += 1.0
        elif chr(p.getType()) == 'N' or chr(p.getType()) == 'B':
            whitescore += 3.0
        elif chr(p.getType()) == 'R':
            whitescore += 5.0
        elif chr(p.getType()) == 'Q':
            whitescore += 9.0
    for p in state.black:
        if chr(p.getType()) == 'P':
            blackscore += 1.0
        elif chr(p.getType()) == 'N' or chr(p.getType()) == 'B':
            blackscore += 3.0
        elif chr(p.getType()) == 'R':
            blackscore += 5.0
        elif chr(p.getType()) == 'Q':
            blackscore += 9.0
    return(whitescore,blackscore)

def materialAdvantage(material,player):
    """Finds advantage in material score on 0-1 scale
    Args:
    material -Tuple of material scores
    player -Side to eval for
    Returns: int -rating (0-1) with 1 as winning"""
    whitescore,blackscore = material
    if player == 0:
        return(whitescore-blackscore+39.0)/78.0
    else:
        return(blackscore-whitescore+39.0)/78.0
    
def materialPercentage(material,player):
    """Finds percentage of total material score on 0-1 scale
    Args:
    material -Tuple of material scores
    player -Side to eval for
    Returns: int -rating (0-1) with 1 as winning"""
    whitescore,blackscore = material
    if player == 0:
        return (whitescore/(blackscore+whitescore))
    else:
        return (blackscore/(blackscore+whitescore))

def checkThreat(state,player):
    """Detirmines if player is threating or being threatened
    Args:
    state -State Object to eval
    player -Side to eval for
    Returns: int -rating (0-1) with 1 as winning"""
    mythreat = state.isInCheck(player)
    opthreat = state.isInCheck(1-player)
    if (mythreat and opthreat)or((not mythreat) and (not opthreat)):
        return 0.5
    if (mythreat) and (not opthreat):
        return 0.0
    if (not mythreat) and (opthreat):
        return 1.0

def coverage(state,player):
    """Detirmines percentage of total board coverage vs oppenent
    Args:
    state -State Object to eval
    player -Side to eval for
    Returns: int -rating (0-1) with 1 as winning"""
    actions = state.getSimpleMoves(player)
    places = []
    mycount = 0.0
    for a in actions:
        if a.piece != None and (not a.dest in places):
            places.append(a.dest)
            mycount += 1
    actions = state.getSimpleMoves(1-player)
    places = []
    opcount = 0.0
    for a in actions:
        if a.piece != None and (not a.dest in places):
            places.append(a.dest)
            opcount += 1
    return mycount/(opcount+mycount)

def randomify():
    """Returns: random int (0-1)"""
    return random.choice([0.0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1.0])

def pawnScore(state):
    pointwhite = 0.0
    pointblack = 0.0
    for p in state.white:
        if chr(p.getType()) == "P":
            r,f = toCoords(p)
            if isValidPos((r,f-1)):
                np = state.getAtPos((r,f-1))
                if np != None and chr(np.getType()) == "P":
                    pointwhite += 1
            if isValidPos((r,f+1)):
                np = state.getAtPos((r,f+1))
                if np != None and chr(np.getType()) == "P":
                    pointwhite += 1
                    
            if isValidPos((r-1,f-1)):
                np = state.getAtPos((r-1,f-1))
                if np != None and chr(np.getType()) == "P":
                    pointwhite += 2
            if isValidPos((r-1,f+1)):
                np = state.getAtPos((r-1,f+1))
                if np != None and chr(np.getType()) == "P":
                    pointwhite += 2
                    
    for p in state.black:
        if chr(p.getType()) == "P":
            r,f = toCoords(p)
            if isValidPos((r,f-1)):
                np = state.getAtPos((r,f-1))
                if np != None and chr(np.getType()) == "P":
                    pointblack += 1
            if isValidPos((r,f+1)):
                np = state.getAtPos((r,f+1))
                if np != None and chr(np.getType()) == "P":
                    pointblack += 1
                    
            if isValidPos((r+1,f-1)):
                np = state.getAtPos((r+1,f-1))
                if np != None and chr(np.getType()) == "P":
                    pointblack += 2
            if isValidPos((r+1,f+1)):
                np = state.getAtPos((r+1,f+1))
                if np != None and chr(np.getType()) == "P":
                    pointblack += 2
                    
    return pointwhite,pointblack

def pawnPercentage(score,player):
    whitescore,blackscore = score
    if player == 0:
        return (whitescore/(0.0001+blackscore+whitescore))
    else:
        return (blackscore/(0.0001+blackscore+whitescore))

def pawnStructure(score,player):
    whitescore,blackscore = score
    if player == 0:
        return (whitescore/14.0)
    else:
        return (blackscore/14.0)

    
#---------------------------------------------------------------------------------------------------------------

# Utility functions  copyed cause importing not working right#

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

#-----------------------------------------------------------------------------------------
    
