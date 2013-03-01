import objects

class ObjectHolder(dict):
  def __init__(self, *args, **kwargs):
    dict.__init__(self, *args, **kwargs)
    self.moves = []
    self.pieces = []
    self.players = []

  def __setitem__(self, key, value):
    if key in self:
      self.__delitem__(key)
    dict.__setitem__(self, key, value)
    if isinstance(value, objects.Move):
      self.moves.append(value)
    if isinstance(value, objects.Piece):
      self.pieces.append(value)
    if isinstance(value, objects.Player):
      self.players.append(value)

  def __delitem__(self, key):
    value = self[key]
    dict.__delitem__(self, key)
    if value in self.moves:
      self.moves.remove(value)
    if value in self.pieces:
      self.pieces.remove(value)
    if value in self.players:
      self.players.remove(value)
