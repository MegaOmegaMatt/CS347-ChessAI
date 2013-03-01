// -*-c++-*-

#ifndef MOVE_H
#define MOVE_H

#include <iostream>
#include "structures.h"


///A chess move
class Move {
  public:
  void* ptr;
  Move(_Move* ptr = NULL);

  // Accessors
  ///Unique Identifier
  int id();
  ///The initial file location
  int fromFile();
  ///The initial rank location
  int fromRank();
  ///The final file location
  int toFile();
  ///The final rank location
  int toRank();
  ///The type of the piece for pawn promotion. Q=Queen, B=Bishop, N=Knight, R=Rook
  int promoteType();

  // Actions

  // Properties


  friend std::ostream& operator<<(std::ostream& stream, Move ob);
};

#endif

