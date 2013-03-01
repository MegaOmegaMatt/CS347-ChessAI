// -*-c++-*-

#ifndef PIECE_H
#define PIECE_H

#include <iostream>
#include "structures.h"


///A chess piece
class Piece {
  public:
  void* ptr;
  Piece(_Piece* ptr = NULL);

  // Accessors
  ///Unique Identifier
  int id();
  ///The owner of the piece
  int owner();
  ///The letter this piece is at (1-8)
  int file();
  ///The number this piece is at (1-8)
  int rank();
  ///1=has moved, 0=has not moved
  int hasMoved();
  ///The letter that describes this piece's type. K=King, Q=Queen, B=Bishop, N=Knight, R=Rook, P=Pawn
  int type();

  // Actions
  ///
  int move(int file, int rank, int type);

  // Properties


  friend std::ostream& operator<<(std::ostream& stream, Piece ob);
};

#endif

