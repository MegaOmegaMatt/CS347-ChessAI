//Copyright (C) 2009 - Missouri S&T ACM AI Team
//Please do not modify this file while building your AI
//See AI.h & AI.cpp for that
#ifndef GAME_H
#define GAME_H

#include "network.h"
#include "structures.h"

#ifdef _WIN32
#define DLLEXPORT extern "C" __declspec(dllexport)

#ifdef ENABLE_THREADS
#include "pthread.h"
#endif

#else
#define DLLEXPORT

#ifdef ENABLE_THREADS
#include <pthread.h>
#endif

#endif

struct Connection
{
  int socket;
  
  #ifdef ENABLE_THREADS
  pthread_mutex_t mutex;
  #endif
  
  int turnNumber;
  int playerID;
  int gameNumber;
  int TurnsToStalemate;

  _Move* Moves;
  int MoveCount;
  _Piece* Pieces;
  int PieceCount;
  _Player* Players;
  int PlayerCount;
};

#ifdef __cplusplus
extern "C"
{
#endif
  DLLEXPORT Connection* createConnection();
  DLLEXPORT void destroyConnection(Connection* c);
  DLLEXPORT int serverConnect(Connection* c, const char* host, const char* port);

  DLLEXPORT int serverLogin(Connection* c, const char* username, const char* password);
  DLLEXPORT int createGame(Connection* c);
  DLLEXPORT int joinGame(Connection* c, int id, const char* playerType);

  DLLEXPORT void endTurn(Connection* c);
  DLLEXPORT void getStatus(Connection* c);


//commands

  ///
  DLLEXPORT int pieceMove(_Piece* object, int file, int rank, int type);

//derived properties



//accessors

DLLEXPORT int getTurnNumber(Connection* c);
DLLEXPORT int getPlayerID(Connection* c);
DLLEXPORT int getGameNumber(Connection* c);
DLLEXPORT int getTurnsToStalemate(Connection* c);

DLLEXPORT _Move* getMove(Connection* c, int num);
DLLEXPORT int getMoveCount(Connection* c);

DLLEXPORT _Piece* getPiece(Connection* c, int num);
DLLEXPORT int getPieceCount(Connection* c);

DLLEXPORT _Player* getPlayer(Connection* c, int num);
DLLEXPORT int getPlayerCount(Connection* c);



  DLLEXPORT int networkLoop(Connection* c);
#ifdef __cplusplus
}
#endif

#endif
