import unittest
from Coord import *
import Door as DoorModule

global_next_id = 1
def get_next_id():
   global global_next_id
   answer = global_next_id
   global_next_id += 1
   return answer

class Cell(object):
    def __init__(self, coord, zone=''):
        self.coord = coord
        self.zone = zone
        self.doors = [None for x in range(4)] # no doors in any of the directions
        self.color = 0
        self.prev = coord
        self.distance = 0
        self.id = get_next_id()
        self.under_cell = None
        self.free_template = True
        self.free_link = True
    def get_id(self):
        return self.id
    def set_color(self, color):
        self.color = color
    def get_color(self):
        return self.color
    def is_color(self, color):
        return self.color == color
    def __str__(self):
        return 'Cell_%d%s' % (self.id, self.coord)
    def __repr__(self):
        return str(self)
    def has_door(self, direction):
        return self.doors[direction] is not None
    def get_doors(self):
        return [d for d in self.doors if d is not None and d.is_real_door()]
    def get_door_count(self):
        c = 0;
        for d in self.doors:
            if d is not None:
                c += 1
        return c
    def is_unlinked(self):
        return self.get_door_count() == 0
    def add_door(self, direction, door):
        if door is not None:
            _ = door.get_direction() # will throw an exception of door isn't a Door
        self.doors[direction] = door
    def get_coord(self):
        return self.coord
    def get_neighbors(self):
        doors = [d for d in self.get_doors() if d.is_real_door()]
        return [d.get_other_side(self) for d in doors]
    def set_prev(self, prev):
        self.prev = prev
    def get_prev(self):
        return self.prev
    def set_distance(self, distance):
        self.distance = distance
    def get_distance(self):
        return self.distance
    def set_under_cell(self, other):
        self.under_cell = other
    def get_under_cell(self):
        return self.under_cell
    def has_under_cell(self):
        return self.under_cell is not None
    def is_free_to_use_in_template(self):
        return self.free_template
    def is_free_to_link(self):
        return self.free_link
    def lock_template(self):
        self.free_template = False
    def lock_link(self):
        self.free_link = False

class TestCell(unittest.TestCase):
   def setUp(self):
      self.a = Cell(Coord(8, 13))
   def test_str(self):
      self.assertEqual(str(self.a), 'Cell_%d(8,13)'%self.a.get_id())
   def test_color(self):
      self.assertEqual(self.a.get_color(), 0)
      self.a.set_color(8)
      self.assertEqual(self.a.get_color(), 8)
      self.assertTrue(self.a.is_color(8))
      self.assertFalse(self.a.is_color(3))
   def test_no_get_doors(self):
      doors = self.a.get_doors()
      self.assertEqual(doors, [])
   def test_one_get_doors(self):
      b = Cell(Coord(8, 14))
      door = DoorModule.Door(self.a, EAST, b)
      self.a.add_door(EAST, door)
      b.add_door(WEST, door)
      doors = self.a.get_doors()
      self.assertEqual(doors, [door])
      doors = b.get_doors()
      self.assertEqual(doors, [door])
   def test_get_neigghbors(self):
      b = Cell(Coord(8, 14))
      door = DoorModule.Door(self.a, EAST, b)
      self.a.add_door(EAST, door)
      b.add_door(WEST, door)
      neighbors = self.a.get_neighbors()
      self.assertEqual(neighbors, [b])
      neighbors = b.get_neighbors()
      self.assertEqual(neighbors, [self.a])
   def test_get_id(self):
      b = Cell(Coord(8, 13))
      self.assertNotEqual(self.a.get_id(), b.get_id())
   def test_get_id_grid(self):
      height = 3
      width = 3
      grid = [[Cell(Coord(x, y), "Z") for y in range(width)] for x in range(height)]
      first = grid[0][0]
      last = grid[2][2]
      self.assertNotEqual(first.get_id(), last.get_id())
      self.assertEqual(first.get_id(), grid[0][0].get_id())
   def test_locks(self):
         self.assertTrue(self.a.is_free_to_use_in_template())
         self.assertTrue(self.a.is_free_to_link())
         self.a.lock_template()
         self.assertFalse(self.a.is_free_to_use_in_template())
         self.assertTrue(self.a.is_free_to_link())
         self.a.lock_link()
         self.assertFalse(self.a.is_free_to_use_in_template())
         self.assertFalse(self.a.is_free_to_link())

class UnderCell(Cell):
   def __init__(self, over_cell):
       Cell.__init__(self, over_cell.coord, over_cell.zone)
       over_cell.set_under_cell(self)
       self.over_cell = over_cell
   def __str__(self):
      return 'UnderCell%s%s' % (self.zone, self.coord)


class TestUnderCell(unittest.TestCase):
    def setUp(self):
        self.over = Cell(Coord(8, 13))
        self.under = UnderCell(self.over)
    def test_str(self):
        self.assertEqual(str(self.under), 'UnderCell(8,13)')
    def test_linkage(self):
        self.assertEqual(self.over.get_under_cell(), self.under)

