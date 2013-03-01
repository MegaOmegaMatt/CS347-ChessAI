//Copyright (C) 2009 - Missouri S&T ACM AI Team
//Please do not modify this file while building your AI
//See AI.h & AI.cpp for that
#pragma warning(disable : 4996)

#include <string>
#include <cstring>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <fstream>
#include <memory>

#include "game.h"
#include "network.h"
#include "structures.h"

#include "sexp/sfcompat.h"

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>

#ifdef _WIN32
//Doh, namespace collision.
namespace Windows
{
    #include <Windows.h>
};
#else
#include <unistd.h>
#endif

#ifdef ENABLE_THREADS
#define LOCK(X) pthread_mutex_lock(X)
#define UNLOCK(X) pthread_mutex_unlock(X)
#else
#define LOCK(X)
#define UNLOCK(X)
#endif

using std::cout;
using std::cerr;
using std::endl;
using std::stringstream;
using std::string;
using std::ofstream;

DLLEXPORT Connection* createConnection()
{
  Connection* c = new Connection;
  c->socket = -1;
  #ifdef ENABLE_THREADS
  pthread_mutex_init(&c->mutex, NULL);
  #endif

  c->turnNumber = 0;
  c->playerID = 0;
  c->gameNumber = 0;
  c->TurnsToStalemate = 0;
  c->Moves = NULL;
  c->MoveCount = 0;
  c->Pieces = NULL;
  c->PieceCount = 0;
  c->Players = NULL;
  c->PlayerCount = 0;
  return c;
}

DLLEXPORT void destroyConnection(Connection* c)
{
  #ifdef ENABLE_THREADS
  pthread_mutex_destroy(&c->mutex);
  #endif
  if(c->Moves)
  {
    for(int i = 0; i < c->MoveCount; i++)
    {
    }
    delete[] c->Moves;
  }
  if(c->Pieces)
  {
    for(int i = 0; i < c->PieceCount; i++)
    {
    }
    delete[] c->Pieces;
  }
  if(c->Players)
  {
    for(int i = 0; i < c->PlayerCount; i++)
    {
      delete[] c->Players[i].playerName;
    }
    delete[] c->Players;
  }
  delete c;
}

DLLEXPORT int serverConnect(Connection* c, const char* host, const char* port)
{
  c->socket = open_server_connection(host, port);
  return c->socket + 1; //false if socket == -1
}

DLLEXPORT int serverLogin(Connection* c, const char* username, const char* password)
{
  string expr = "(login \"";
  expr += username;
  expr += "\" \"";
  expr += password;
  expr +="\")";

  send_string(c->socket, expr.c_str());

  sexp_t* expression, *message;

  char* reply = rec_string(c->socket);
  expression = extract_sexpr(reply);
  delete[] reply;

  message = expression->list;
  if(message->val == NULL || strcmp(message->val, "login-accepted") != 0)
  {
    cerr << "Unable to login to server" << endl;
    destroy_sexp(expression);
    return 0;
  }
  destroy_sexp(expression);
  return 1;
}

DLLEXPORT int createGame(Connection* c)
{
  sexp_t* expression, *number;

  send_string(c->socket, "(create-game)");

  char* reply = rec_string(c->socket);
  expression = extract_sexpr(reply);
  delete[] reply;

  number = expression->list->next;
  c->gameNumber = atoi(number->val);
  destroy_sexp(expression);

  std::cout << "Creating game " << c->gameNumber << endl;

  c->playerID = 0;

  return c->gameNumber;
}

DLLEXPORT int joinGame(Connection* c, int gameNum, const char* playerType)
{
  sexp_t* expression;
  stringstream expr;

  c->gameNumber = gameNum;

  expr << "(join-game " << c->gameNumber << " "<< playerType << ")";
  send_string(c->socket, expr.str().c_str());

  char* reply = rec_string(c->socket);
  expression = extract_sexpr(reply);
  delete[] reply;

  if(strcmp(expression->list->val, "join-accepted") == 0)
  {
    destroy_sexp(expression);
    c->playerID = 1;
    send_string(c->socket, "(game-start)");
    return 1;
  }
  else if(strcmp(expression->list->val, "create-game") == 0)
  {
    std::cout << "Game did not exist, creating game " << c->gameNumber << endl;
    destroy_sexp(expression);
    c->playerID = 0;
    return 1;
  }
  else
  {
    cerr << "Cannot join game "<< c->gameNumber << ": " << expression->list->next->val << endl;
    destroy_sexp(expression);
    return 0;
  }
}

DLLEXPORT void endTurn(Connection* c)
{
  LOCK( &c->mutex );
  send_string(c->socket, "(end-turn)");
  UNLOCK( &c->mutex );
}

DLLEXPORT void getStatus(Connection* c)
{
  LOCK( &c->mutex );
  send_string(c->socket, "(game-status)");
  UNLOCK( &c->mutex );
}



DLLEXPORT int pieceMove(_Piece* object, int file, int rank, int type)
{
  stringstream expr;
  expr << "(game-move " << object->id
       << " " << file
       << " " << rank
       << " " << type
       << ")";
  LOCK( &object->_c->mutex);
  send_string(object->_c->socket, expr.str().c_str());
  UNLOCK( &object->_c->mutex);
  return 1;
}



//Utility functions for parsing data
void parseMove(Connection* c, _Move* object, sexp_t* expression)
{
  sexp_t* sub;
  sub = expression->list;

  object->_c = c;

  object->id = atoi(sub->val);
  sub = sub->next;
  object->fromFile = atoi(sub->val);
  sub = sub->next;
  object->fromRank = atoi(sub->val);
  sub = sub->next;
  object->toFile = atoi(sub->val);
  sub = sub->next;
  object->toRank = atoi(sub->val);
  sub = sub->next;
  object->promoteType = atoi(sub->val);
  sub = sub->next;

}
void parsePiece(Connection* c, _Piece* object, sexp_t* expression)
{
  sexp_t* sub;
  sub = expression->list;

  object->_c = c;

  object->id = atoi(sub->val);
  sub = sub->next;
  object->owner = atoi(sub->val);
  sub = sub->next;
  object->file = atoi(sub->val);
  sub = sub->next;
  object->rank = atoi(sub->val);
  sub = sub->next;
  object->hasMoved = atoi(sub->val);
  sub = sub->next;
  object->type = atoi(sub->val);
  sub = sub->next;

}
void parsePlayer(Connection* c, _Player* object, sexp_t* expression)
{
  sexp_t* sub;
  sub = expression->list;

  object->_c = c;

  object->id = atoi(sub->val);
  sub = sub->next;
  object->playerName = new char[strlen(sub->val)+1];
  strncpy(object->playerName, sub->val, strlen(sub->val));
  object->playerName[strlen(sub->val)] = 0;
  sub = sub->next;
  object->time = atof(sub->val);
  sub = sub->next;

}

DLLEXPORT int networkLoop(Connection* c)
{
  while(true)
  {
    sexp_t* base, *expression, *sub, *subsub;

    char* message = rec_string(c->socket);
    string text = message;
    base = extract_sexpr(message);
    delete[] message;
    expression = base->list;
    if(expression->val != NULL && strcmp(expression->val, "game-winner") == 0)
    {
      expression = expression->next->next->next;
      int winnerID = atoi(expression->val);
      if(winnerID == c->playerID)
      {
        cout << "You win!" << endl << expression->next->val << endl;
      }
      else
      {
        cout << "You lose. :(" << endl << expression->next->val << endl;
      }
      stringstream expr;
      expr << "(request-log " << c->gameNumber << ")";
      send_string(c->socket, expr.str().c_str());
      destroy_sexp(base);
      return 0;
    }
    else if(expression->val != NULL && strcmp(expression->val, "log") == 0)
    {
      ofstream out;
      stringstream filename;
      expression = expression->next;
      filename << expression->val;
      filename << ".gamelog";
      expression = expression->next;
      out.open(filename.str().c_str());
      if (out.good())
        out.write(expression->val, strlen(expression->val));
      else
        cerr << "Error : Could not create log." << endl;
      out.close();
      destroy_sexp(base);
      return 0;
    }
    else if(expression->val != NULL && strcmp(expression->val, "game-accepted")==0)
    {
      char gameID[30];

      expression = expression->next;
      strcpy(gameID, expression->val);
      cout << "Created game " << gameID << endl;
    }
    else if(expression->val != NULL && strstr(expression->val, "denied"))
    {
      cout << expression->val << endl;
      cout << expression->next->val << endl;
    }
    else if(expression->val != NULL && strcmp(expression->val, "status") == 0)
    {
      while(expression->next != NULL)
      {
        expression = expression->next;
        sub = expression->list;
        if(string(sub->val) == "game")
        {
          sub = sub->next;
          c->turnNumber = atoi(sub->val);
          sub = sub->next;

          c->playerID = atoi(sub->val);
          sub = sub->next;

          c->gameNumber = atoi(sub->val);
          sub = sub->next;

          c->TurnsToStalemate = atoi(sub->val);
          sub = sub->next;

        }
        else if(string(sub->val) == "Move")
        {
          if(c->Moves)
          {
            for(int i = 0; i < c->MoveCount; i++)
            {
            }
            delete[] c->Moves;
          }
          c->MoveCount =  sexp_list_length(expression)-1; //-1 for the header
          c->Moves = new _Move[c->MoveCount];
          for(int i = 0; i < c->MoveCount; i++)
          {
            sub = sub->next;
            parseMove(c, c->Moves+i, sub);
          }
        }
        else if(string(sub->val) == "Piece")
        {
          if(c->Pieces)
          {
            for(int i = 0; i < c->PieceCount; i++)
            {
            }
            delete[] c->Pieces;
          }
          c->PieceCount =  sexp_list_length(expression)-1; //-1 for the header
          c->Pieces = new _Piece[c->PieceCount];
          for(int i = 0; i < c->PieceCount; i++)
          {
            sub = sub->next;
            parsePiece(c, c->Pieces+i, sub);
          }
        }
        else if(string(sub->val) == "Player")
        {
          if(c->Players)
          {
            for(int i = 0; i < c->PlayerCount; i++)
            {
              delete[] c->Players[i].playerName;
            }
            delete[] c->Players;
          }
          c->PlayerCount =  sexp_list_length(expression)-1; //-1 for the header
          c->Players = new _Player[c->PlayerCount];
          for(int i = 0; i < c->PlayerCount; i++)
          {
            sub = sub->next;
            parsePlayer(c, c->Players+i, sub);
          }
        }
      }
      destroy_sexp(base);
      return 1;
    }
    else
    {
#ifdef SHOW_WARNINGS
      cerr << "Unrecognized message: " << text << endl;
#endif
    }
    destroy_sexp(base);
  }
}

DLLEXPORT _Move* getMove(Connection* c, int num)
{
  return c->Moves + num;
}
DLLEXPORT int getMoveCount(Connection* c)
{
  return c->MoveCount;
}

DLLEXPORT _Piece* getPiece(Connection* c, int num)
{
  return c->Pieces + num;
}
DLLEXPORT int getPieceCount(Connection* c)
{
  return c->PieceCount;
}

DLLEXPORT _Player* getPlayer(Connection* c, int num)
{
  return c->Players + num;
}
DLLEXPORT int getPlayerCount(Connection* c)
{
  return c->PlayerCount;
}


DLLEXPORT int getTurnNumber(Connection* c)
{
  return c->turnNumber;
}
DLLEXPORT int getPlayerID(Connection* c)
{
  return c->playerID;
}
DLLEXPORT int getGameNumber(Connection* c)
{
  return c->gameNumber;
}
DLLEXPORT int getTurnsToStalemate(Connection* c)
{
  return c->TurnsToStalemate;
}
