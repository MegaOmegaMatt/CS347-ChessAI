##################################
# OrderHeuristics By Matthew Terneus
# Updated 3/7/12
# Contains methods to effectively order a minimax search
##################################

from Utils import toCoords
import heapq

#-----------------------------------------------------------------------------
# History table and associated methods #

def hashify(action):
    """Extracts all important data from action to be hashed in a dictionary
    Args:
    action -Action object
    Returns: hashable tuple
    """
    if action.piece != None:
        frm = toCoords(action.piece)
        to = action.dest
        p = action.piece.getType()
    else:
        (king,kpos),rook = action.dest
        frm = toCoords(king)
        to = kpos
        p = ord("K")
    return(p,(frm,to))

class HistoryTable:
    """Hash Table to aid in effective move ordering"""
    def __init__(self):
        """Constructor"""
        self.tbl = dict()
    def update(self,action):
        """Adds or increments a key for a action
        Args:
        action -Action object
        """
        h = hashify(action)
        if h in self.tbl:
            self.tbl[hashify(action)] += 1
        else:
            self.tbl[hashify(action)] = 1
    def get(self,action):
        """Gets stored value for action
        Args:
        action -Action object
        Returns: int -number of times updated
        """
        h = hashify(action)
        if h in self.tbl:
            return self.tbl[hashify(action)]
        else:
            return 0

#-----------------------------------------------------------------------------
# Move ordering functions #

def orderByHistory(actions,table):
    sort = []
    for each in actions:
        sort.append((table.get(each),each))

    sort.sort()
    sort.reverse()

    final = []
    for val,item in sort:
        final.append(item)
        
    return final
