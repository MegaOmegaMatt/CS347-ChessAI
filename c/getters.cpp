#include "getters.h"

int moveGetId(_Move* ptr)
{
  return ptr->id;
}
int moveGetFromFile(_Move* ptr)
{
  return ptr->fromFile;
}
int moveGetFromRank(_Move* ptr)
{
  return ptr->fromRank;
}
int moveGetToFile(_Move* ptr)
{
  return ptr->toFile;
}
int moveGetToRank(_Move* ptr)
{
  return ptr->toRank;
}
int moveGetPromoteType(_Move* ptr)
{
  return ptr->promoteType;
}
int pieceGetId(_Piece* ptr)
{
  return ptr->id;
}
int pieceGetOwner(_Piece* ptr)
{
  return ptr->owner;
}
int pieceGetFile(_Piece* ptr)
{
  return ptr->file;
}
int pieceGetRank(_Piece* ptr)
{
  return ptr->rank;
}
int pieceGetHasMoved(_Piece* ptr)
{
  return ptr->hasMoved;
}
int pieceGetType(_Piece* ptr)
{
  return ptr->type;
}
int playerGetId(_Player* ptr)
{
  return ptr->id;
}
char* playerGetPlayerName(_Player* ptr)
{
  return ptr->playerName;
}
float playerGetTime(_Player* ptr)
{
  return ptr->time;
}

