//Copyright (C) 2009 - Missouri S&T ACM AI Team
//Please do not modify this file while building your AI
//See AI.h & AI.cpp for that
#ifndef STRUCTURES_H
#define STRUCTURES_H

struct Connection;
struct _Move;
struct _Piece;
struct _Player;


struct _Move
{
  Connection* _c;
  int id;
  int fromFile;
  int fromRank;
  int toFile;
  int toRank;
  int promoteType;
};
struct _Piece
{
  Connection* _c;
  int id;
  int owner;
  int file;
  int rank;
  int hasMoved;
  int type;
};
struct _Player
{
  Connection* _c;
  int id;
  char* playerName;
  float time;
};

#endif
