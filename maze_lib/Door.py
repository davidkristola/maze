import unittest
from Coord import *
import Cell as CellModule

class Door(object):
   def __init__(self, start, direction, end):
      self.start = start
      self.direction = direction
      self.end = end
   def get_other_side(self, this_side):
      if this_side == self.start:
         return self.end
      return self.start
   def get_direction(self):
      return self.direction
   def __str__(self):
      return '<%s-%s-%s>' % (self.start, ('N', 'E', 'S', 'W')[self.direction], self.end)
   def __repr__(self):
      return str(self)
   def is_real_door(self):
      return True

class TestDoor(unittest.TestCase):
   def test_opposite_direction(self):
      self.assertEqual(opposite_direction(NORTH), SOUTH)
      self.assertEqual(opposite_direction(SOUTH), NORTH)
      self.assertEqual(opposite_direction(EAST), WEST)
      self.assertEqual(opposite_direction(WEST), EAST)
   def test_get_other_side(self):
      a = CellModule.Cell(Coord(1, 3))
      b = CellModule.Cell(Coord(2, 3))
      door = Door(a, SOUTH, b)
      answer = door.get_other_side(a)
      self.assertEqual(answer, b)
      answer = door.get_other_side(b)
      self.assertEqual(answer, a)
   def test_str(self):
      a = CellModule.Cell(Coord(1, 3))
      b = CellModule.Cell(Coord(2, 3))
      door = Door(a, SOUTH, b)
      self.assertEqual(str(door), '<Cell(1,3)-S-Cell(2,3)>')

class DoorToTheOutside(object):
   def __init__(self, start, direction):
      self.start = start
      self.direction = direction
   def get_other_side(self, this_side):
      return None
   def get_direction(self):
      return self.direction
   def __str__(self):
      return 'Escape<%s-%s-None>' % (self.start, ('N', 'E', 'S', 'W')[self.direction])
   def __repr__(self):
      return str(self)
   def is_real_door(self):
      return False

