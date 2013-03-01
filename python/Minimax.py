##################################
# Minimax.py By Matthew Terneus
# Updated 3/6/12
# Contains classes and methods to preform a minimax search
##################################

from OrderHeuristics import *

#-----------------------------------------------------------------------------
# heuristic minimax#
def minimax(state,player,depth):
    """
    Uses minimax algorithm to find the best utility value and action recursively
    Args:
    state- Current board state
    player- Player to maximize
    depth- depth limit
    Returns: tuple- (int,Action) Value and action to get value
    """
    # check if goal found
    terminate = state.termTest(player)
    #if not and the depth limit has not been reached be recursive
    if terminate == -1 and depth > 0:
        actions = state.getMoves(state.turn)
        # If a player can't move
        if len(actions) == 0:
            if state.isInCheck(state.turn):
                #Somebody lost
                if player == state.turn:
                    #I lost
                    return(0.0,None)
                else:
                    #I didn't lose so I must win
                    return(1.0,None)
            #it was a tie
            return(.5,None)
        
        # create a record of all values and corresponding actions from this state
        record = []
        for a in actions:
            value,futureaction = minimax(state.move(a),player,depth-1)
            record.append((value,a))
            
        if player == state.turn:
            # Maximize on my turn
            return max(record)
        else:
            # Oppenent will Minimize me on thier turn
            return min(record)
    elif terminate != -1:
        # If a goal was found
        return (terminate,None)
    else:
        # if depth limit reached evaluate the current state
        return (state.evaluate(player),None)

#----------------------------------------------------------------------
# Alpha Beta Pruning #

def abMinimax(state,player,depth,alpha,beta):
    # check if goal found
    terminate = state.termTest(player)
    #if not and the depth limit has not been reached be recursive
    if terminate == -1 and depth > 0:
        actions = state.getMoves(state.turn)
        # If a player can't move
        if len(actions) == 0:
            if state.isInCheck(state.turn):
                #Somebody lost
                if player == state.turn:
                    #I lost
                    return(0.0,None)
                else:
                    #I didn't lose so I must win
                    return(1.0,None)
            #it was a tie
            return(.5,None)
        
        if player == state.turn:
            # Maximize on my turn
            valueaction,a = abMaxVal(state,player,depth,actions,alpha,beta)
            alpha = a
            return valueaction
        else:
            # Oppenent will Minimize me on thier turn
            valueaction,b = abMinVal(state,player,depth,actions,alpha,beta)
            beta = b
            return valueaction
    elif terminate != -1:
        # If a goal was found
        return (terminate,None)
    else:
        # if depth limit reached evaluate the current state
        return (state.evaluate(player),None)

def abMaxVal(state,player,depth,actions,alpha,beta):
    # Dummy max value, smaller than any possible value
    maxval = (-1,"I AM ERROR")
    for act in actions:
        value,futureaction = abMinimax(state.move(act),player,depth-1,alpha,beta)
        if (value,futureaction) > maxval:
            #update max
            maxval = (value,act)
        if beta <= value:
            #prune
            break
        if value > alpha:
            # did not fail high or low so update alpha
            alpha = value
    return (maxval,alpha)


def abMinVal(state,player,depth,actions,alpha,beta):
    # Dummy min value, bigger than any possible value
    minval = (2,"I AM ERROR")
    for act in actions:
        value,futureaction = abMinimax(state.move(act),player,depth-1,alpha,beta)
        if (value,futureaction) < minval:
            #update min
            minval = (value,act)
        if value <= alpha:
            #prune
            break
        if value < beta:
            # did not fail high or low so update beta
            beta = value
    return (minval,beta)

#----------------------------------------------------------------------
# Alpha Beta Pruning with move ordering #

def abOrderMinimax(state,player,depth,alpha,beta,table):
    #st = str(state.turn)
    #for i in range(depth+1):
        #st = st + ">>"
    #print st,"------"
        
    # check if goal found
    terminate = state.termTest(player)
    #if not and the depth limit has not been reached be recursive
    if terminate == -1 and depth > 0:
        actions = state.getMoves(state.turn)
        # If a player can't move
        if len(actions) == 0:
            if state.isInCheck(state.turn):
                #Somebody lost
                if player == state.turn:
                    #I lost
                    #print st," Lose: 0"
                    return(0.0,None)
                else:
                    #I didn't lose so I must win
                    #print st," Win: 1"
                    return(1.0,None)
            #it was a tie
            #print st," Stale: .5"
            return(.5,None)
        
        if player == state.turn:
            # Maximize on my turn
            valueaction,a = abOrderMaxVal(state,player,depth,actions,alpha,beta,table)
            value,act = valueaction
            table.update(act)
            alpha = a
            #print st," MAX: ", value
            return valueaction
        else:
            # Oppenent will Minimize me on thier turn
            valueaction,b = abOrderMinVal(state,player,depth,actions,alpha,beta,table)
            value,act = valueaction
            table.update(act)
            beta = b
            #print st," MIN: ", value
            return valueaction
    elif terminate != -1:
        # If a goal was found
        #print st," Stale: ", terminate
        return (terminate,None)
    else:
        # if depth limit reached evaluate the current state
        #print st," EVAL: ", state.evaluate(player)
        return (state.evaluate(player),None)

def abOrderMaxVal(state,player,depth,actions,alpha,beta,table):
    # Dummy max value, smaller than any possible value
    maxval = (-1,"I AM ERROR")
    sort = orderByHistory(actions,table)
    for act in sort:
        value,futureaction = abOrderMinimax(state.move(act),player,depth-1,alpha,beta,table)
        if (value,futureaction) > maxval:
            #update max
            maxval = (value,act)
        if beta <= value:
            #prune
            break
        if value > alpha:
            # did not fail high or low so update alpha
            alpha = value
    return (maxval,alpha)


def abOrderMinVal(state,player,depth,actions,alpha,beta,table):
    # Dummy min value, bigger than any possible value
    minval = (2,"I AM ERROR")
    sort = orderByHistory(actions,table)
    for act in sort:
        value,futureaction = abOrderMinimax(state.move(act),player,depth-1,alpha,beta,table)
        if (value,futureaction) < minval:
            #update min
            minval = (value,act)
        if value <= alpha:
            #prune
            break
        if value < beta:
            # did not fail high or low so update beta
            beta = value
    return (minval,beta)

#----------------------------------------------------------------------
# Alpha Beta Pruning with move ordering and Quiesent Extensions#

def abQuiOrderMinimax(state,player,depth,extension,alpha,beta,table):        
    # check if goal found
    terminate = state.termTest(player)
    #if not terminal and the depth limit or extension has not been reached be recursive
    if terminate == -1 and extension > 0 and (depth > 0 or not state.quiet):
        actions = state.getMoves(state.turn)
        # If a player can't move
        if len(actions) == 0:
            if state.isInCheck(state.turn):
                #Somebody lost
                if player == state.turn:
                    #I lost
                    return(0.0,None)
                else:
                    #I didn't lose so I must win
                    return(1.0,None)
            #it was a tie
            return(.5,None)

        if player == state.turn:
            # Maximize on my turn
            valueaction,a = abQuiOrderMaxVal(state,player,depth,extension,actions,alpha,beta,table)
            value,act = valueaction
            table.update(act)
            alpha = a
            return valueaction
        else:
            # Oppenent will Minimize me on thier turn
            valueaction,b = abQuiOrderMinVal(state,player,depth,extension,actions,alpha,beta,table)
            value,act = valueaction
            table.update(act)
            beta = b
            return valueaction
    elif terminate != -1:
        # If a goal was found
        return (terminate,None)
    else:
        # if depth limit reached evaluate the current state
        return (state.evaluate(player),None)

def abQuiOrderMaxVal(state,player,depth,extension,actions,alpha,beta,table):
    # Dummy max value, smaller than any possible value
    maxval = (-1,"I AM ERROR")
    sort = orderByHistory(actions,table)
    if depth > 0:
        newdepth = depth-1
        newextension = extension
    else:
        newdepth = 0
        newextension = extension-1
        
    for act in sort:
        value,futureaction = abQuiOrderMinimax(state.move(act),player,newdepth,newextension,alpha,beta,table)
        if (value,futureaction) > maxval:
            #update max
            maxval = (value,act)
        if beta <= value:
            #prune
            break
        if value > alpha:
            # did not fail high or low so update alpha
            alpha = value
    return (maxval,alpha)


def abQuiOrderMinVal(state,player,depth,extension,actions,alpha,beta,table):
    # Dummy min value, bigger than any possible value
    minval = (2,"I AM ERROR")
    sort = orderByHistory(actions,table)
    if depth > 0:
        newdepth = depth-1
        newextension = extension
    else:
        newdepth = 0
        newextension = extension-1
    
    for act in sort:
        value,futureaction = abQuiOrderMinimax(state.move(act),player,newdepth,newextension,alpha,beta,table)
        if (value,futureaction) < minval:
            #update min
            minval = (value,act)
        if value <= alpha:
            #prune
            break
        if value < beta:
            # did not fail high or low so update beta
            beta = value
    return (minval,beta)


