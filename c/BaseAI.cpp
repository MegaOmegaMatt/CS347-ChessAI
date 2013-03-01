//Copyright (C) 2009 - Missouri S&T ACM AI Team
//Please do not modify this file while building your AI
//See AI.h & AI.cpp for that

#include "BaseAI.h"
#include "game.h"

int BaseAI::turnNumber()
{
  return getTurnNumber(c);
}
int BaseAI::playerID()
{
  return getPlayerID(c);
}
int BaseAI::gameNumber()
{
  return getGameNumber(c);
}
int BaseAI::TurnsToStalemate()
{
  return getTurnsToStalemate(c);
}

bool BaseAI::startTurn()
{
  static bool initialized = false;
  int count = 0;
  count = getMoveCount(c);
  moves.clear();
  moves.resize(count);
  for(int i = 0; i < count; i++)
  {
    moves[i] = Move(getMove(c, i));
  }

  count = getPieceCount(c);
  pieces.clear();
  pieces.resize(count);
  for(int i = 0; i < count; i++)
  {
    pieces[i] = Piece(getPiece(c, i));
  }

  count = getPlayerCount(c);
  players.clear();
  players.resize(count);
  for(int i = 0; i < count; i++)
  {
    players[i] = Player(getPlayer(c, i));
  }

  if(!initialized)
  {
    initialized = true;
    init();
  }
  return run();
}

BaseAI::BaseAI(Connection* conn) : c(conn) {}
BaseAI::~BaseAI() {}
