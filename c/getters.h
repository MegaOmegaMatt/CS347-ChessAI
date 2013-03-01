#ifndef GETTERS_H 
#define GETTERS_H
#include "structures.h"

#ifdef __cplusplus
extern "C" {
#endif

int moveGetId(_Move* ptr);
int moveGetFromFile(_Move* ptr);
int moveGetFromRank(_Move* ptr);
int moveGetToFile(_Move* ptr);
int moveGetToRank(_Move* ptr);
int moveGetPromoteType(_Move* ptr);


int pieceGetId(_Piece* ptr);
int pieceGetOwner(_Piece* ptr);
int pieceGetFile(_Piece* ptr);
int pieceGetRank(_Piece* ptr);
int pieceGetHasMoved(_Piece* ptr);
int pieceGetType(_Piece* ptr);


int playerGetId(_Player* ptr);
char* playerGetPlayerName(_Player* ptr);
float playerGetTime(_Player* ptr);



#ifdef __cplusplus
}
#endif

#endif
