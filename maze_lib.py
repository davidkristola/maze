import unittest
import random
import itertools
import heapq

# maze initialization styles
RANDOM = 0
ZIGZAG = 1
SPIRAL = 2
BI_SPI = 3
ZAGZIG = 4
R_WALK = 5
RANRUN = 6
KRUSKAL = 7
EXP_2 = 8
SPLIT_TREE = 9
LAST_STYLE = SPLIT_TREE

# directions
NORTH = 0
EAST  = 1
SOUTH = 2
WEST  = 3

def opposite_direction(direction):
   return (direction+2)%4


class Coord(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)
    def __ne__(self, other):
        return not self.__eq__(other)
    def step(self, direction):
        new_x = self.x + (-1,  0, +1,  0)[direction]
        new_y = self.y + ( 0, +1,  0, -1)[direction]
        return Coord(new_x, new_y)
    def __str__(self):
        return '(%d,%d)' % (self.x, self.y)
    def __repr__(self):
        return str(self)
    def direction_to_other(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        if dx == 0:
            if dy == -1:
                return WEST
            elif dy == 1:
                return EAST
        elif dy == 0:
            if dx == -1:
                return NORTH
            elif dx == 1:
                return SOUTH
        raise Exception('Coordinates are not adjacent!')
    def shift(self, x_offset, y_offset):
        new_x = self.x + x_offset
        new_y = self.y + y_offset
        return Coord(new_x, new_y)


class TestCoord(unittest.TestCase):
    def test_eq(self):
        a = Coord(1, 4)
        b = Coord(4, 1)
        c = Coord(1, 4)
        self.assertTrue(a == c)
        self.assertFalse(a == b)
    def test_neq(self):
        a = Coord(1, 4)
        b = Coord(4, 1)
        c = Coord(1, 4)
        self.assertTrue(a != b)
        self.assertFalse(a != c)
    def test_step_south(self):
        new = Coord(2, 7).step(SOUTH)
        self.assertEqual(new, Coord(3, 7))
    def test_step_north(self):
        new = Coord(2, 7).step(NORTH)
        self.assertEqual(new, Coord(1, 7))
    def test_step_east(self):
        new = Coord(2, 7).step(EAST)
        self.assertEqual(new, Coord(2, 8))
    def test_step_west(self):
        new = Coord(2, 7).step(WEST)
        self.assertEqual(new, Coord(2, 6))
    def test_direction_to_other(self):
         a = Coord(5,5)
         for d in range(4):
             b = a.step(d)
             self.assertEqual(a.direction_to_other(b), d)
    def test_shift(self):
        start = Coord(7, 7)
        a1 = start.shift(-1, 0)
        e1 = Coord(6, 7)
        self.assertEqual(a1, e1)
        a2 = start.shift(0, 1)
        e2 = Coord(7, 8)
        self.assertEqual(a2, e2)


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
      a = Cell(Coord(1, 3))
      b = Cell(Coord(2, 3))
      door = Door(a, SOUTH, b)
      answer = door.get_other_side(a)
      self.assertEqual(answer, b)
      answer = door.get_other_side(b)
      self.assertEqual(answer, a)
   def test_str(self):
      a = Cell(Coord(1, 3))
      b = Cell(Coord(2, 3))
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
        #self.id = (coord.x * 10000000) + coord.y
        self.under_cell = None
    def get_id(self):
        return self.id
    def set_color(self, color):
        self.color = color
    def get_color(self):
        return self.color
    def is_color(self, color):
        return self.color == color
    def __str__(self):
        return 'Cell%s%s' % (self.zone, self.coord)
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

class TestCell(unittest.TestCase):
   def setUp(self):
      self.a = Cell(Coord(8, 13))
   def test_str(self):
      self.assertEqual(str(self.a), 'Cell(8,13)')
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
      door = Door(self.a, EAST, b)
      self.a.add_door(EAST, door)
      b.add_door(WEST, door)
      doors = self.a.get_doors()
      self.assertEqual(doors, [door])
      doors = b.get_doors()
      self.assertEqual(doors, [door])
   def test_get_neigghbors(self):
      b = Cell(Coord(8, 14))
      door = Door(self.a, EAST, b)
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




class PathQueue(object):
    def __init__(self, upper_limit):
        self.upper_limit = upper_limit
        self.heap = []
    def add(self, path):
        inverted_length = self.upper_limit - len(path)
        heapq.heappush(self.heap, (inverted_length, path))
    def pop(self):
        (inverted_length, path) = heapq.heappop(self.heap)
        return path
    def count(self):
        return len(self.heap)

class TestPathQueue(unittest.TestCase):
    def test_1(self):
        uut = PathQueue(1000)
        uut.add([1, 2, 3, 4])
        uut.add([5, 6])
        uut.add([7, 8, 9, 10, 11, 12, 13, 14])
        self.assertEqual(uut.pop(), [7, 8, 9, 10, 11, 12, 13, 14])
        self.assertEqual(uut.pop(), [1, 2, 3, 4])
        self.assertEqual(uut.pop(), [5, 6])
    def test_2(self):
        uut = PathQueue(1000)
        uut.add([1, 2, 3, 4])
        uut.add([5, 6])
        uut.add([7, 8, 9, 10, 11, 12, 13, 14])
        self.assertEqual(uut.count(), 3)

class SilentProgressReporter(object):
   def __init__(self):
      self.debug = False
   def report(self, x, out_of_y):
      if self.debug:
         print("%d out of %d" % (x, out_of_y))

class Maze(object):
   def __init__(self, height, width, zone):
      self.width = width
      self.height = height
      self.zone = zone
      self.grid = [[Cell(Coord(x, y), zone) for y in range(width)] for x in range(height)] # grid of cells
      self.debug = False
      self.out_west = None
      self.out_east = None
      self.first_coord = Coord(0, 0)
      self.last_coord = Coord(height-1, width-1)

   def get_first_coord(self):
      return self.first_coord
   def get_last_coord(self):
      return self.last_coord
   def get_first_cell(self):
      return self.grid[0][0]
   def get_last_cell(self):
      return self.get(self.last_coord)
   def get_x_range(self):
      return range(self.height)
   def get_y_range(self):
      return range(self.width)

   def get(self, coord):
      return self.grid[coord.x][coord.y]

   def get_cell_in_direction_from_coord(self, coord, direction):
       actual = coord.step(direction)
       assert self.is_valid_coord(actual)
       return self.grid[actual.x][actual.y]

   #TODO: change style from an input here to a subclass of Maze
   def connect_all(self, style, progress_reporter = SilentProgressReporter()):
      if style == RANDOM:
         self.connect_all(random.randint(ZIGZAG, LAST_STYLE), progress_reporter)
      elif style == ZIGZAG:
         self.zigzag_connect_all(progress_reporter)
      elif style == SPIRAL:
         self.mono_spiral_connect_all(progress_reporter)
      elif style == BI_SPI:
         self.bi_spiral_connect_all(progress_reporter)
      elif style == ZAGZIG:
         self.zagzig_connect_all(progress_reporter)
      elif style == R_WALK:
         self.walk_connect_all(progress_reporter)
      elif style == RANRUN:
         self.run_connect_all(progress_reporter)
      elif style == KRUSKAL:
         self.kruskal(progress_reporter)
      elif style == EXP_2:
         self.kruskal_weave(self.height*self.width//50, progress_reporter)
      elif style == SPLIT_TREE:
          self.split_tree(5, 5, self.height//5, self.width//5, R_WALK, R_WALK, progress_reporter)
      self.validate_maze()

   def validate_maze(self):
       return
       #print("Validating maze...")
       #self.color_all(0)
       #cycles = self.color_from(1, Coord(0,0))
       #if cycles != 0:
       #    print("ERROR: Maze has %d cycles!" % cycles)
       #other_end = Coord(self.height-1, self.width-1)
       #if self.get(other_end).get_color() != 1:
       #    print("ERROR: Maze ends are not connected!")

   def zigzag_connect_all(self, progress_reporter = None):
      for x in range(self.height):
         for y in range(self.width - 1):
            self.add_door(Coord(x, y), EAST)
      right = True
      for x in range(self.height - 1):
         y = self.width-1 if right else 0
         self.add_door(Coord(x, y), SOUTH)
         right = not right

   def zagzig_connect_all(self, progress_reporter = None):
      for x in range(self.height - 1):
         for y in range(self.width):
            self.add_door(Coord(x, y), SOUTH)
      top = True
      for y in range(self.width - 1):
         x = self.height-1 if top else 0
         self.add_door(Coord(x, y), EAST)
         top = not top

   def mono_spiral_connect_all(self, progress_reporter = None):
      self.color_all(0)
      current = Coord(0,0)
      direction = SOUTH
      for i in range((self.height * self.width) - 1):
         c = self.get(current)
         c.set_color(1)
         next = current.step(direction)
         if self.invalid_coordinate(next):
            direction = (direction + 3) % 4
            next = current.step(direction)
         n = self.get(next)
         if n.get_color() != 0:
            direction = (direction + 3) % 4
            next = current.step(direction)
            n = self.get(next)
         self.add_door(current, direction)
         current = next

   def bi_spiral_connect_all(self, progress_reporter = None):
      self.color_all(0)
      current = [Coord(0,0), Coord(self.height-1, self.width-1)]
      direction = [SOUTH, NORTH]
      ab = 0
      for i in range((self.height * self.width) - 1):
         c = self.get(current[ab])
         c.set_color(1)
         next = current[ab].step(direction[ab])
         if self.invalid_coordinate(next):
            direction[ab] = (direction[ab] + 3) % 4
            next = current[ab].step(direction[ab])
         n = self.get(next)
         if n.get_color() != 0:
            direction[ab] = (direction[ab] + 3) % 4
            next = current[ab].step(direction[ab])
            n = self.get(next)
         self.add_door(current[ab], direction[ab])
         current[ab] = next
         ab = (ab + 1) % 2

   def walk_connect_all(self, progress = None):
      self.color_all(1)
      current = self.pick_random_cell()
      complete = (self.height*self.width)-1
      for i in range(complete):
         if progress:
            progress.report(i, complete-1)
         current.set_color(5)
         step_direction = self.pick_random_bicolor_wall(current)
         if step_direction is None:
             if self.debug: print('start new walk at %d' % (i))
             choices = self.walls_between_colors()
             assert choices != []
             (coord_1, direction) = random.choice(choices)
             coord_2 = coord_1.step(direction)
             assert self.get(coord_1).get_color() != self.get(coord_2).get_color()
             self.add_door(coord_1, direction)
             #next_coord = coord_1 if current.get_coord() != coord_1 else coord_2
             if self.get(coord_1).is_color(5):
                 next_coord = coord_2
             elif self.get(coord_2).is_color(5):
                 next_coord = coord_1
             else:
                 assert False
         else:
             next_coord = current.get_coord().step(step_direction)
             assert current.get_color() != self.get(next_coord).get_color()
             self.add_door(current.get_coord(), step_direction)
         current = self.get(next_coord)

   def run_connect_all(self, progress = None):
       self.color_all(1)
       current = self.pick_random_cell()
       color = 5
       current.set_color(color)
       step_direction = random.choice([0, 1, 2, 3])
       complete = (self.height*self.width)-1
       for i in range(complete):
           if progress:
              progress.report(i, complete-1)
           if not self.can_build(current, step_direction):
               #print('start new run at %d' % (i))
               (current, step_direction) = self.pick_new_current(current, color)
           current = self.extend_one_step(current, step_direction, color)

   def add_door(self, coord, direction):
      if self.debug: print('Add door from %s %s to %s' % (coord, ('N', 'E', 'S', 'W')[direction], coord.step(direction)))
      assert not self.invalid_coordinate(coord)
      destination = coord.step(direction)
      assert not self.invalid_coordinate(destination)
      start = self.get(coord)
      end = self.get(destination)
      door = Door(start, direction, end)
      start.add_door(direction, door)
      end.add_door(opposite_direction(direction), door)

   def add_under_door(self, under_cell, direction):
       coord = under_cell.get_coord()
       if self.debug: print('Add under door from %s %s to %s' % (coord, ('N', 'E', 'S', 'W')[direction], coord.step(direction)))
       assert not self.invalid_coordinate(coord)
       destination = coord.step(direction)
       assert not self.invalid_coordinate(destination)
       end = self.get(destination)
       door = Door(under_cell, direction, end)
       under_cell.add_door(direction, door)
       end.add_door(opposite_direction(direction), door)

   def remove_door(self, coord, direction):
      first = self.get(coord)
      second = self.get(coord.step(direction))
      first.add_door(direction, None)
      second.add_door(opposite_direction(direction), None)

   def random_walk(self, start, color, limit):
       '''Start a random walk from start and return the path built.'''
       path_taken = [start.get_coord()]
       current = start
       current.set_color(color)
       step_direction = self.pick_random_bicolor_wall(current)
       while (step_direction != None) and (len(path_taken) < limit):
           next_coord = current.get_coord().step(step_direction)
           assert current.get_color() != self.get(next_coord).get_color()
           self.add_door(current.get_coord(), step_direction)
           current = self.get(next_coord)
           current.set_color(color)
           current.set_distance(len(path_taken))
           current.set_prev(path_taken[-1])
           path_taken += [next_coord]
           step_direction = self.pick_random_bicolor_wall(current)
       return path_taken

   def can_build(self, current, step_direction):
       next_coord = current.get_coord().step(step_direction)
       if self.invalid_coordinate(next_coord):
           #print('Coordinate %s is invalid' % (next_coord))
           return False
       if current.has_door(step_direction):
           #print('Current %s has a door in direction %d' % (current, step_direction))
           return False
       next_coord = current.get_coord().step(step_direction)
       colors_are_different = current.get_color() != self.get(next_coord).get_color()
       #print('colors_are_different = %s' % (colors_are_different))
       return colors_are_different

   def pick_new_current(self, current, color):
       choices = self.walls_between_colors()
       assert choices != []
       (coord_1, direction) = random.choice(choices)
       coord_2 = coord_1.step(direction)
       assert self.get(coord_1).get_color() != self.get(coord_2).get_color()
       if self.get(coord_1).is_color(color):
           next_coord = coord_1
           next_direction = direction
       elif self.get(coord_2).is_color(color):
           next_coord = coord_2
           next_direction = opposite_direction(direction)
       else:
           assert False
       #print('NEW current = %s, step_direrction = %d' % (self.get(next_coord), next_direction))
       return self.get(next_coord), next_direction

   def extend_one_step(self, current, step_direction, color):
       next_coord = current.get_coord().step(step_direction)
       assert current.get_color() != self.get(next_coord).get_color()
       #print('Adding door from %s to %s' % (current.get_coord(), next_coord))
       self.add_door(current.get_coord(), step_direction)
       next_cell = self.get(next_coord)
       next_cell.set_color(color)
       next_cell.set_prev(current.get_coord())
       next_cell.set_distance(current.get_distance()+1)
       return next_cell

   def get_neighbors(self, coord):
      it = self.get(coord)
      return it.get_neighbors()

   def color_all(self, color):
      for x in self.get_x_range():
         for y in self.get_y_range():
            cell = self.grid[x][y]
            cell.set_color(color)
            if cell.has_under_cell():
                cell.get_under_cell().set_color(color)
      if self.out_west is not None:
         self.out_west.set_color(color)
      if self.out_east is not None:
         self.out_east.set_color(color)

   def get_all_color(self, color):
      answer = []
      for x in range(self.height):
         for y in range(self.width):
            if self.grid[x][y].is_color(color):
               answer += [self.grid[x][y]]
      return answer

   def open_outer_walls(self):
      west_coord = self.get_first_coord()
      east_coort = self.get_last_coord()
      self.out_west = Cell(west_coord.step(WEST))
      self.out_east = Cell(east_coort.step(EAST))
      self.get_first_cell().add_door(WEST, DoorToTheOutside(self.get(west_coord), WEST))
      self.get_last_cell().add_door(EAST, DoorToTheOutside(self.get(east_coort), EAST))

   def color_from(self, color, coord):
      '''BFS'''
      cycles = 0
      x = self.get(coord)
      x.set_color(color)
      explore = x.get_neighbors()
      while len(explore) != 0:
         x = explore[0]
         del(explore[0])
         if x is not None:
             x.set_color(color)
             cycles += max(0, len([y for y in x.get_neighbors() if y.is_color(color)]) - 1)
             explore += [y for y in x.get_neighbors() if not y.is_color(color)]
      return cycles

   def path_from_to(self, from_coord, to_coord, color):
      '''BFS'''
      x = self.get(to_coord)
      x.set_color(color)
      x.set_prev(to_coord)
      x.set_distance(0)
      neighbors = x.get_neighbors()
      for n in neighbors:
          n.set_prev(to_coord)
      explore = neighbors
      while len(explore) != 0:
         x = explore[0]
         del(explore[0])
         x.set_color(color)
         neighbors = [y for y in x.get_neighbors() if not y.is_color(color)]
         d = x.get_distance() + 1
         for n in neighbors:
             n.set_prev(x.get_coord())
             n.set_distance(d)
         explore += neighbors
      path = [from_coord]
      c = from_coord
      while c != to_coord:
          #print('c is %s' % (c))          
          c = self.get(c).get_prev()
          path += [c]
      return path

   def pick_random_door(self):
      # precondition: every cell must have at least one door
      x = random.randint(0, self.height-1)
      y = random.randint(0, self.width-1)
      d = random.randint(0, 4-1)
      c = Coord(x, y)
      focus = self.get(c)
      for dd in range(4):
         ddd =  (d + dd) % 4
         if focus.has_door(ddd):
            return (c, ddd)
      #print('WARNING: %s has no doors!' % (focus))
      return self.pick_random_door() # try a different one

   def pick_random_coord(self):
      x = random.randint(0, self.height-1)
      y = random.randint(0, self.width-1)
      return Coord(x, y)

   def pick_random_cell(self):
      #x = random.randint(0, self.height-1)
      #y = random.randint(0, self.width-1)
      #c = Coord(x, y)
      c = self.pick_random_coord()
      return self.get(c)

   def pick_random_bicolor_wall(self, cell):
      candidates = []
      color = cell.get_color()
      loc = cell.get_coord()
      for direction in range(4):
         neighbor = loc.step(direction)
         if (not self.invalid_coordinate(neighbor)):
            if (not cell.has_door(direction)):
               if (not self.get(neighbor).is_color(color)):
                  candidates += [direction]
      if len(candidates) == 0:
         return None
      return random.choice(candidates)

   def invalid_coordinate(self, coord):
      if coord.x < 0 or coord.x >= self.height:
         return True
      if coord.y < 0 or coord.y >= self.width:
         return True
      return False

   def is_valid_coord(self, coord):
       return not self.invalid_coordinate(coord)

   def bicolor_wall_or_none(self, coord_1, direction):
      cell_1 = self.get(coord_1)
      if cell_1.has_door(direction):
         return None
      coord_2 = coord_1.step(direction)
      if self.invalid_coordinate(coord_2):
         return None
      cell_2 = self.get(coord_2)
      if cell_1.get_color() == cell_2.get_color():
         return None
      return coord_1, direction

   def walls_between_colors(self):
      walls = []
      for x in range(self.height):
         for y in range(self.width):
            c = Coord(x, y)
            answer = self.bicolor_wall_or_none(c, EAST)
            if answer is not None:
               walls.append(answer)
            answer = self.bicolor_wall_or_none(c, SOUTH)
            if answer is not None:
               walls.append(answer)
      return walls

   def all_nextdoor_pairs(self):
       answer = []
       for x in range(self.height):
           for y in range(self.width):
               c1 = Coord(x, y)
               c2 = c1.step(NORTH)
               c3 = c1.step(EAST)
               if not self.invalid_coordinate(c2):
                   answer += [(self.get(c1), NORTH, self.get(c2))]
               if not self.invalid_coordinate(c3):
                   answer += [(self.get(c1), EAST, self.get(c3))]
       return answer

   def set_up_unlinked_kruskal(self):
       self.set_for_cell = {} # dictionary over cells of their set number
       self.cells_in_set = {} # dictionary over set number of sets of connected cells
       for x in range(self.height):
           for y in range(self.width):
               co_1 = Coord(x, y)
               ce_1 = self.get(co_1)
               set_number = len(self.set_for_cell)
               self.set_for_cell[ce_1.get_id()] = set_number
               self.cells_in_set[set_number] = set([ce_1.get_id()])

   def kruskal(self, progress_reporter = None):
       self.set_up_unlinked_kruskal()
       self.kruskal_join_all()

   def kruskal_weave(self, weave_count, progress_reporter = None):
       self.set_up_unlinked_kruskal()
       for _ in range(weave_count):
           self.kruskal_weave_over_under_cross(self.pick_random_coord())
       self.kruskal_join_all()

   def kruskal_join_all(self):
       self.color_all(1)
       neighbors = self.all_nextdoor_pairs()
       random.shuffle(neighbors)
       for (c1, d, c2) in neighbors:
           if self.can_kruskal_join(c1, c2):
               self.kruskal_join(c1, d, c2)

   def can_kruskal_join(self, c1, c2):
       if c1.has_under_cell() or c2.has_under_cell():
           return False # don't violate the weave criteria
       return self.set_for_cell[c1.get_id()] != self.set_for_cell[c2.get_id()]

   def kruskal_join(self, c1, d, c2):
       self.add_door(c1.get_coord(), d)
       self.kruskal_join_sets(c1.get_id(), c2.get_id())

   def kruskal_join_sets(self, c1_id, c2_id):
       set_number_to_expand = self.set_for_cell[c1_id]
       set_number_to_disband = self.set_for_cell[c2_id]
       #print('joining set expand:%s and set disband:%s' % (self.cells_in_set[set_number_to_expand], self.cells_in_set[set_number_to_disband]))
       cells_to_move = [cell_id for cell_id in self.cells_in_set[set_number_to_disband]]
       for cell_id in cells_to_move:
           #print('moving id %d from set %d to %d' % (cell_id, set_number_to_disband, set_number_to_expand))
           update_set = self.cells_in_set[set_number_to_expand]
           update_set.add(cell_id)
           self.cells_in_set[set_number_to_expand] = update_set
           self.set_for_cell[cell_id] = set_number_to_expand
       self.cells_in_set[set_number_to_disband] = set()

   def get_kruskal_set(self, cell_id):
       return self.set_for_cell[cell_id]

   def kruskal_weave_over_under_cross(self, coord):
       if not self.can_kruskal_weave_over_under_cross(coord):
           return False
       if random.randint(0, 1) == 0:
           #self.add_door(coord, EAST)
           self.kruskal_join(self.get(coord), EAST, self.get_cell_in_direction_from_coord(coord, EAST))
           #self.add_door(coord, WEST)
           self.kruskal_join(self.get(coord), WEST, self.get_cell_in_direction_from_coord(coord, WEST))
       else:
           #self.add_door(coord, NORTH)
           self.kruskal_join(self.get(coord), NORTH, self.get_cell_in_direction_from_coord(coord, NORTH))
           #self.add_door(coord, SOUTH)
           self.kruskal_join(self.get(coord), SOUTH, self.get_cell_in_direction_from_coord(coord, SOUTH))
       self.tunnel_under_existing_path(coord)
       return True

   def tunnel_under_existing_path(self, coord):
       # coord has either a vertical or horizontal path over it
       over_cell = self.get(coord)
       under_cell = UnderCell(over_cell)
       if over_cell.has_door(NORTH):
           # tunnel under east/west
           d = (EAST, WEST)
       else:
           d = (NORTH, SOUTH)
       self.add_under_door(under_cell, d[0])
       self.add_under_door(under_cell, d[1])
       self.kruskal_join_sets(self.get_cell_in_direction_from_coord(coord, d[0]).get_id(), self.get_cell_in_direction_from_coord(coord, d[1]).get_id())

   def can_kruskal_weave_over_under_cross(self, coord):
       ''' make sure all of the surrounding cells are valid and not weaved. '''
       for x_offset in [-1, 0, +1]:
           for y_offset in [-1, 0, +1]:
               try_here = coord.shift(x_offset, y_offset)
               if self.invalid_coordinate(try_here):
                   return False
               cell_here = self.get(try_here)
               if cell_here.has_under_cell():
                   return False
       return True
       
   # This is not Weaved Kruskal... is it dead code?
   def exp_2(self):
       path_maker = PathMaker(self.height, self.width, 8)
       #path_maker.make_unordered_point_list()
       #path = path_maker.a_non_crossing_path()
       path = path_maker.new_path(8)
       self.color_all(1)
       color = 5
       if path is None:
           self.build_from_to(Coord(self.height-1,self.width-1), Coord(0,0), color)
       else:
           for line in path:
               p1 = Coord(int(line.get_p1().x), int(line.get_p1().y))
               p2 = Coord(int(line.get_p2().x), int(line.get_p2().y))
               try:
                   self.build_from_to(p1, p2, color)
               except:
                   pass

   def split_tree(self, grid_x, grid_y, sub_x, sub_y, outer_style, inner_style, progress_reporter = None):
       path_maker = PathMaker2(grid_x, grid_y, sub_x, sub_y)
       path = path_maker.make_path(outer_style, inner_style)
       self.build_path(path, 8)
       self.path_queue = PathQueue(self.height*self.width)
       self.path_queue.add(path)

   def split_tree_again(self, progress_reporter = None):
       #for i in range(10):
       while (self.path_queue.count() > 0):
           self.split_tree_more()
       self.validate_maze()

   def split_tree_more(self):
       p = self.path_queue.pop()
       #print('length of the longest queued path is %d' % len(p))
       (a, b, c) = self.divide_path_at_junction_near_middle(p)
       if b is None:
           #print('could not divide path of length %d' % len(p))
           return
       d = self.random_walk(self.get(b), 8, 200)
       self.path_queue.add(a)
       self.path_queue.add(c)
       self.path_queue.add(d)

   def divide_path_at_junction_near_middle(self, path):
       m = self.junction_nearest_middle(path)
       if m is None:
           return (path, None, None)
       return (path[:m-1], path[m], path[m+1:])

   def junction_nearest_middle(self, path):
       if len(path) == 0:
           return None
       m = len(path)//2
       if self.has_junction(path[m]):
           return m
       ml = m-1
       mu = m+1
       while (ml >= 0) and (mu < len(path)):
           if ml >= 0:
               if self.has_junction(path[ml]):
                   return ml
           ml -= 1
           if mu < len(path):
               if self.has_junction(path[mu]):
                   return mu
           mu += 1
       return None

   def has_junction(self, loc):
       cell = self.get(loc)
       #print('has_junction %s' % loc)
       color = cell.get_color()
       candidates = []
       for direction in range(4):
           neighbor = loc.step(direction)
           #print('checking %s' % neighbor)
           if (not self.invalid_coordinate(neighbor)):
               if (not cell.has_door(direction)):
                   if (not self.get(neighbor).is_color(color)):
                       candidates += [direction]
                       #print('candidate!')
       return len(candidates) > 0


   # this is only used in split_tree
   def build_path(self, path, color):
       for i in range(len(path)-1):
           current = path[i]
           self.get(current).set_color(color)
           next = path[i+1]
           step_direction = current.direction_to_other(next)
           self.add_door(current, step_direction)
       self.get(path[-1]).set_color(color)

   # this is only used in the weaved kruskal (but is it usefull elsewhere?
   def build_from_to(self, from_coord, to_coord, color):
       current = self.get(from_coord)
       current.set_color(color)
       current.set_distance(0)
       while current.get_coord() != to_coord:
           step_direction, second_choice = self.pick_direction_from_to(current.get_coord(), to_coord)
           #print('current = %s, step_direrction = %d' % (current, step_direction))
           if not self.can_build(current, step_direction):
               if current.get_coord().step(step_direction) == to_coord:
                   print('Adding door from %s to line destination %s' % (current.get_coord(), to_coord))
                   self.add_door(current.get_coord(), step_direction)
                   return
               if self.can_build(current, second_choice):
                   step_direction = second_choice
               else:
                   step_direction = self.pick_random_bicolor_wall(current)
                   while step_direction == None:
                       current = self.get(current.get_prev()) # back up one step
                       step_direction = self.pick_random_bicolor_wall(current)
                       if current.get_distance() == 1:
                           raise Exception('end of line')
                       #print('Back up!')
           current = self.extend_one_step(current, step_direction, color)

   # this is only used in the weaved kruskal
   def pick_direction_from_to(self, current, goal):
       delta_x = goal.x - current.x
       delta_y = goal.y - current.y
       neg_x, plus_y, plus_x, neg_y = (0, 1, 2, 3)
       if abs(delta_x) > abs(delta_y):
           if delta_x > 0:
               return plus_x, plus_y if delta_y > 0 else neg_y
           else:
               return neg_x, plus_y if delta_y > 0 else neg_y
       else:
            if delta_y > 0:
                return plus_y, plus_x if delta_x > 0 else neg_x
            else:
                return neg_y, plus_x if delta_x > 0 else neg_x

   def move_door(self):
      self.color_all(0)
      (c1, d) = self.pick_random_door()
      c2 = c1.step(d)
      self.remove_door(c1, d)
      self.color_from(1, c1)
      self.color_from(2, c2)
      candidate_walls = self.walls_between_colors()
      if len(candidate_walls) > 0:
         (cell, direction) = random.choice(candidate_walls)
         self.add_door(cell, direction)
      else:
         print('WARNING: no candidate walls between %s and %s' % (c1, c2))
      self.color_all(0)


class ZigZagMaze(Maze):
   def __init__(self, height, width, zone):
      Maze.__init__(self, height, width, zone)
      self.style = ZIGZAG

class ZagZigMaze(Maze):
   def __init__(self, height, width, zone):
      Maze.__init__(self, height, width, zone)
      self.style = ZAGZIG

class SpiralMaze(Maze):
   def __init__(self, height, width, zone):
      Maze.__init__(self, height, width, zone)
      self.style = SPIRAL

class DoubleSpiralMaze(Maze):
   def __init__(self, height, width, zone):
      Maze.__init__(self, height, width, zone)
      self.style = BI_SPI

class RandomWalkMaze(Maze):
   def __init__(self, height, width, zone):
      Maze.__init__(self, height, width, zone)
      self.style = R_WALK

class RandomRunMaze(Maze):
   def __init__(self, height, width, zone):
      Maze.__init__(self, height, width, zone)
      self.style = RANRUN

class KruskalMaze(Maze):
   def __init__(self, height, width, zone):
      Maze.__init__(self, height, width, zone)
      self.style = KRUSKAL

class WeavedKruskalMaze(Maze):
   def __init__(self, height, width, zone):
      Maze.__init__(self, height, width, zone)
      self.style = EXP_2

class SplitTreeMaze(Maze):
   def __init__(self, height, width, zone):
      Maze.__init__(self, height, width, zone)
      self.style = SPLIT_TREE

def NewMaze(style, height, width, zone):
    if style == RANDOM:
        return NewMaze(random.randint(ZIGZAG, LAST_STYLE), height, width, zone)
    elif style == ZIGZAG:
        return ZigZagMaze(height, width, zone)
    elif style == SPIRAL:
        return SpiralMaze(height, width, zone)
    elif style == BI_SPI:
        return DoubleSpiralMaze(height, width, zone)
    elif style == ZAGZIG:
        return ZagZigMaze(height, width, zone)
    elif style == R_WALK:
        return RandomWalkMaze(height, width, zone)
    elif style == RANRUN:
        return RandomRunMaze(height, width, zone)
    elif style == KRUSKAL:
        return KruskalMaze(height, width, zone)
    elif style == EXP_2:
        return WeavedKruskalMaze(height, width, zone)
    elif style == SPLIT_TREE:
        return SplitTreeMaze(height, width, zone)
    return None




class TestMaze(unittest.TestCase):
   def setUp(self):
      self.maze = NewMaze(ZIGZAG, 5, 10, 'Q')

   def debug_print_maze(self, the_maze):
      def d(c):
         answer = ''
         for direction in range(4):
            answer += '_' if not c.has_door(direction) else ('N','E','S','W')[direction]
         return answer
      doors = [[d(c) for c in row] for row in the_maze.grid]
      print('doors:')
      for line in doors:
         print(line)
   def debug_print_maze_colors(self, the_maze):
      grid = [['%03d'%c.get_color() for c in row] for row in the_maze.grid]
      print('colors:')
      for line in grid:
         print(line)
   def debug_print_under_maze(self, the_maze):
       def d(c):
          u = c.get_under_cell()
          if u is None:
              return '    '
          answer = ''
          for direction in range(4):
              answer += '_' if not u.has_door(direction) else ('N','E','S','W')[direction]
          return answer
       doors = [[d(c) for c in row] for row in the_maze.grid]
       print('doors:')
       for line in doors:
           print(line)

   # (implicit) ZigZag maze tests
   def test_index(self):
      self.assertEqual(len(self.maze.grid), 5)
      self.assertEqual(len(self.maze.grid[0]), 10)
   def test_get(self):
      x2y7 = self.maze.get(Coord(2, 7))
      self.assertEqual(str(x2y7), 'CellQ(2,7)')
   def test_add_door(self):
      self.maze.add_door(Coord(3, 3), NORTH)
      c1 = self.maze.get(Coord(3, 3))
      c2 = self.maze.get(Coord(2, 3))
      doors1 = c1.get_doors()
      doors2 = c2.get_doors()
      self.assertEqual(doors1, doors2)
      self.assertEqual(len(doors1), 1)
   def test_get_all_color(self):
      self.maze.color_all(0)
      one = self.maze.get(Coord(1,2))
      two = self.maze.get(Coord(2,4))
      three = self.maze.get(Coord(3,9))
      one.set_color(8)
      two.set_color(8)
      three.set_color(8)
      eights = self.maze.get_all_color(8)
      self.assertTrue(one in eights)
      self.assertTrue(two in eights)
      self.assertTrue(three in eights)
      self.assertEqual(len(eights), 3)
   def test_pick_random_bicolor_wall(self):
      self.maze.color_all(3)
      xy = Coord(3,3)
      start = self.maze.get(xy)
      start.set_color(7)
      for i in range(4):
         direction = self.maze.pick_random_bicolor_wall(start)
         self.assertTrue(direction in range(4))
         self.maze.add_door(xy, direction)
   def test_open_outer_walls(self):
       self.maze.open_outer_walls()
       self.assertTrue(self.maze.get_first_cell().has_door(WEST))
       self.assertTrue(self.maze.get_last_cell().has_door(EAST))

   def check_all_connected(self, coord_of_one, neighbors_1, neighbors_2):
      zero = self.maze.get(Coord(0, 0))
      doors = zero.get_doors()
      self.assertTrue(len(doors) > 0)
      if coord_of_one is not None:
         one = self.maze.get(coord_of_one)
         n = self.maze.get_neighbors(Coord(0, 0))
         self.assertEqual(n, [one])
      self.maze.color_all(0)
      cycles = self.maze.color_from(1, Coord(0,0))
      self.assertEqual(cycles, 0)
      self.assertEqual(self.maze.get(Coord(4,9)).get_color(), 1) # all connected
      color_1 = self.maze.get_all_color(1)
      self.assertEqual(len(color_1), 5*10)
      if neighbors_1 is not None:
          self.assertTrue(self.maze.get(neighbors_1[0]) in self.maze.get_neighbors(neighbors_1[1]))
      if neighbors_2 is not None:
          self.assertTrue(self.maze.get(neighbors_2[0]) in self.maze.get_neighbors(neighbors_2[1]))

   # Explicit ZigZag maze tests
   def test_neg(self):
      self.maze.zagzig_connect_all()
      self.check_all_connected(Coord(1, 0), (Coord(0, 9), Coord(1, 9)), (Coord(1, 0), Coord(2, 0)))
   def test_zigzag(self):
      self.maze.zigzag_connect_all()
      self.check_all_connected(Coord(0, 1), (Coord(0, 9), Coord(1, 9)), (Coord(1, 0), Coord(2, 0)))
   def test_zagzig_connect_all(self):
      self.maze.zagzig_connect_all()
      self.check_all_connected(Coord(1, 0), (Coord(0, 9), Coord(1, 9)), (Coord(1, 0), Coord(2, 0)))

   # SpiralMaze tests
   def test_mono_spiral_connect_all(self):
      self.maze.mono_spiral_connect_all()
      self.check_all_connected(Coord(1, 0), (Coord(0, 9), Coord(1, 9)), (Coord(1, 0), Coord(2, 0)))

   # RandomWalkMaze
   def test_walk_connect_all(self):
      #self.maze.debug = True
      self.maze.walk_connect_all()
      #self.debug_print_maze(self.maze)
      self.check_all_connected(None, None, None)

   # RandomRunMaze
   def test_run_connect_all(self):
      #self.maze.debug = True
      self.maze.run_connect_all()
      #self.debug_print_maze(self.maze)
      self.check_all_connected(None, None, None)
   def test_pick_new_current(self):
       self.maze.color_all(1)
       c = self.maze.pick_random_cell()
       c.set_color(5)
       n, d = self.maze.pick_new_current(c, 5)
       self.assertEqual(c, n)

   # DoubleSpiralMaze
   def test_bi_spiral_connect_all(self):
      self.maze.bi_spiral_connect_all()
      self.check_all_connected(Coord(1, 0), (Coord(0, 9), Coord(1, 9)), (Coord(1, 0), Coord(2, 0)))
   def test_bi_spiral_connect_all_2(self):
      test_maze = NewMaze(BI_SPI, 5, 11, 'P')
      test_maze.bi_spiral_connect_all()
      test_maze.color_all(0)
      cycles = test_maze.color_from(1, Coord(0,0))
      self.assertEqual(cycles, 0)
      self.assertEqual(test_maze.get(Coord(4,10)).get_color(), 1) # all connected
   def test_bi_spiral_connect_all_3(self):
      test_maze = NewMaze(BI_SPI, 6, 10, 'S')
      test_maze.bi_spiral_connect_all()
      test_maze.color_all(0)
      cycles = test_maze.color_from(1, Coord(0,0))
      self.assertEqual(cycles, 0)
      self.assertEqual(test_maze.get(Coord(5,9)).get_color(), 1) # all connected
      #self.debug_print_maze(test_maze)
   def test_bi_spiral_connect_all_4(self):
      test_maze = NewMaze(BI_SPI, 6, 11, 'R')
      test_maze.bi_spiral_connect_all()
      test_maze.color_all(0)
      cycles = test_maze.color_from(1, Coord(0,0))
      self.assertEqual(cycles, 0)
      self.assertEqual(test_maze.get(Coord(5,10)).get_color(), 1) # all connected
      #self.debug_print_maze(test_maze)
   def test_bi_spiral_connect_all_5(self):
      test_maze = NewMaze(BI_SPI, 3, 3, 'T')
      test_maze.bi_spiral_connect_all()
      test_maze.color_all(0)
      cycles = test_maze.color_from(1, Coord(0,0))
      self.assertEqual(cycles, 0)
      self.assertEqual(test_maze.get(Coord(2,2)).get_color(), 1) # all connected
      #self.debug_print_maze(test_maze)
   def test_bi_spiral_connect_all_6(self):
      test_maze = NewMaze(BI_SPI, 4, 4, 'A')
      test_maze.bi_spiral_connect_all()
      test_maze.color_all(0)
      cycles = test_maze.color_from(1, Coord(0,0))
      self.assertEqual(cycles, 0)
      self.assertEqual(test_maze.get(Coord(3,3)).get_color(), 1) # all connected
      #self.debug_print_maze(test_maze)

   # ZigZag tests
   def test_color_all(self):
      self.maze.color_all(3)
      self.assertEqual(self.maze.get(Coord(4,9)).get_color(), 3)
   def test_color_from_1(self):
      self.maze.zigzag_connect_all() # all are now connected
      self.maze.color_from(8, Coord(2,4))
      self.assertEqual(self.maze.get(Coord(4,9)).get_color(), 8)
      self.assertEqual(self.maze.get(Coord(0,0)).get_color(), 8)
      self.assertEqual(self.maze.get(Coord(2,5)).get_color(), 8)
   def test_color_from_2(self):
      self.maze.zigzag_connect_all() # all are now connected
      cycle_count = self.maze.color_from(8, Coord(2,4))
      self.assertEqual(cycle_count, 0)

   def test_color_from_3(self):
      self.maze.zigzag_connect_all() # all are now connected
      (c, d) = self.maze.pick_random_door()
      self.maze.remove_door(c, d)
      self.maze.color_from(8, Coord(0,0))
      self.assertEqual(self.maze.get(Coord(4,9)).get_color(), 0)

   def test_remove_door(self):
      self.maze.add_door(Coord(3, 3), NORTH)
      self.maze.remove_door(Coord(2, 3), SOUTH)
      self.assertEqual(len(self.maze.get_neighbors(Coord(3, 3))), 0)
   def test_pick_random_door(self):
      self.maze.zigzag_connect_all() # all are now connected
      for i in range(100):
         (c, d) = self.maze.pick_random_door()
         cell = self.maze.get(c)
         self.assertTrue(cell.has_door(d))
   def test_walls_between_colors(self):
      one = self.maze.get(Coord(3, 3))
      one.set_color(3)
      walls = self.maze.walls_between_colors()
      self.assertEqual(len(walls), 4)
      #print(str(walls))
      self.assertEqual(walls[0][1], SOUTH)
      self.assertEqual(walls[1][1], EAST)
      self.assertEqual(walls[2][1], EAST)
      self.assertEqual(walls[3][1], SOUTH)
      self.assertEqual(walls[0][0], Coord(2,3))
      self.assertEqual(walls[1][0], Coord(3,2))
      self.assertEqual(walls[2][0], Coord(3,3))
      self.assertEqual(walls[3][0], Coord(3,3))
   def test_move_door(self):
      self.maze.zigzag_connect_all() # all are now connected
      for color in range(1, 500):
         self.maze.move_door()
         self.maze.color_from(color, Coord(0,0))
         for x in range(5):
            for y in range(10):
               coord = Coord(x,y)
               cell = self.maze.get(coord)
               is_color = cell.get_color()
               self.assertEqual(is_color, color, '%s is color %d, not %d' % (cell, is_color, color))

   # DoubleSpiralMaze
   def test_path_from_to(self):
      test_maze = NewMaze(BI_SPI, 3, 3, 'T')
      test_maze.bi_spiral_connect_all()
      test_maze.color_all(0)
      test_maze.color_from(1, Coord(0,0))
      #self.debug_print_maze(test_maze)
      path = test_maze.path_from_to(Coord(0,0), Coord(2,2), 2)
      #print(path)
      #self.assertEqual(path, [Coord(2,2), Coord(1,2), Coord(0,2), Coord(0,1), Coord(1,1), Coord(2,1), Coord(2,0), Coord(1,0), Coord(0,0)])
      self.assertEqual(path, [Coord(0,0), Coord(1,0), Coord(2,0), Coord(2,1), Coord(1,1), Coord(0,1), Coord(0,2), Coord(1,2), Coord(2,2)])

   # WeavedKruskal
   def test_pick_direction_from_to(self):
       a = Coord(5,5)
       self.assertEqual(self.maze.pick_direction_from_to(a, Coord(5,3))[0], 3)
       self.assertEqual(self.maze.pick_direction_from_to(a, Coord(4,3))[1], 0)
       self.assertEqual(self.maze.pick_direction_from_to(a, Coord(5,7))[0], 1)
       self.assertEqual(self.maze.pick_direction_from_to(a, Coord(6,7))[1], 2)
       self.assertEqual(self.maze.pick_direction_from_to(a, Coord(7,5))[0], 2)
       self.assertEqual(self.maze.pick_direction_from_to(a, Coord(7,4))[1], 3)
       self.assertEqual(self.maze.pick_direction_from_to(a, Coord(3,5))[0], 0)
       self.assertEqual(self.maze.pick_direction_from_to(a, Coord(3,6))[1], 1)
   def test_build_from_to(self):
       test_maze = Maze(3, 3, 'T')
       test_maze.color_all(1)
       color = 5
       test_maze.get(Coord(1,1)).set_color(5)
       test_maze.build_from_to(Coord(2,2), Coord(0,0), color)
       #self.debug_print_maze(test_maze)
       self.assertEqual(test_maze.get(Coord(2,0)).get_color(), 5)

   def test_random_walk(self):
       test_maze = Maze(100, 100, 'T')
       p = test_maze.random_walk(test_maze.get(Coord(20,20)), 5, 5) # limit 5 must be reachable in an empty maze
       self.assertEqual(len(p), 5)
       self.assertEqual(p[0], Coord(20,20))
       l = test_maze.get(p[-1])
       self.assertEqual(l.get_distance(), 4)
       self.assertEqual(l.get_color(), 5)
       self.assertEqual(l.get_prev(), p[-2])
   def test_random_walk2(self):
       test_maze = Maze(2, 2, 'T')
       p = test_maze.random_walk(test_maze.get(Coord(0,0)), 5, 5) # only 4 cells
       self.assertEqual(len(p), 4)
       self.assertEqual(p[2], Coord(1,1)) # no matter what the ssecond cell is, the third is this one
       self.assertEqual(p[1], test_maze.get(Coord(1,1)).get_prev())
   def test_has_junction(self):
       test_maze = Maze(100, 100, 'T')
       test_maze.color_all(0)
       test_maze.build_path([Coord(5,5), Coord(5,6), Coord(5,7), Coord(4,7), Coord(4,8), Coord(5,8), Coord(6,8), Coord(6,7)], 2)
       self.assertTrue(test_maze.has_junction(Coord(5,6)))
       self.assertFalse(test_maze.has_junction(Coord(5,7)))
   def test_junction_nearest_middle_1(self):
       test_maze = Maze(100, 100, 'T')
       test_maze.color_all(0)
       p = [Coord(x,10) for x in range(5,15)]
       test_maze.build_from_to(p[0], p[-1], 5)
       a = test_maze.junction_nearest_middle(p)
       self.assertEqual(p[a], Coord(10,10))
       q = [Coord(x,9) for x in range(5,15)]
       test_maze.build_from_to(q[0], q[-1], 5)
       q = [Coord(x,11) for x in range(5,15)]
       test_maze.build_from_to(q[0], q[-1], 5)
       a = test_maze.junction_nearest_middle(p)
       self.assertTrue((a == 0) or (a == len(p)-1))
       #print(str(a))
       for l in p[1:-2]:
           self.assertFalse(test_maze.has_junction(l))
   def test_junction_nearest_middle_2(self):
       test_maze = Maze(10, 10, 'T')
       test_maze.color_all(0)
       p = [Coord(5,5), Coord(5,6), Coord(5,7), Coord(4,7), Coord(4,8), Coord(5,8), Coord(6,8), Coord(6,7)]
       test_maze.build_path(p, 2)
       a = test_maze.junction_nearest_middle(p)
       self.assertEqual(a, 4)
       a = test_maze.junction_nearest_middle(p[:-1])
       self.assertEqual(a, 3)
       a = test_maze.junction_nearest_middle(p[:-3])
       self.assertEqual(a, 1) # because (5,7) is middle but it is surrounded, closest is (5,6)
       self.assertEqual(None, test_maze.junction_nearest_middle([Coord(5,7)]))
       self.assertEqual(None, test_maze.junction_nearest_middle([]))
   def test_tunnel_under_existing_path(self):
       test_maze = Maze(3, 3, 'U')
       test_maze.set_up_unlinked_kruskal()
       test_maze.add_door(Coord(1,1), EAST)
       test_maze.add_door(Coord(1,1), WEST)
       test_maze.tunnel_under_existing_path(Coord(1,1))
       #print("test_tunnel_under_existing_path")
       #self.debug_print_maze(test_maze)
       test_maze.color_from(5, Coord(1,1).step(NORTH))
       self.assertEqual(test_maze.get(Coord(1,1).step(SOUTH)).get_color(), 5)
   def test_kruskal_weave_over_under_cross(self):
       test_maze = Maze(3, 3, 'U')
       test_maze.set_up_unlinked_kruskal()
       center = Coord(1,1)
       test_maze.kruskal_weave_over_under_cross(center)
       #self.debug_print_maze(test_maze)
       test_maze.color_from(5, center.step(NORTH))
       test_maze.color_from(7, center.step(EAST))
       self.assertEqual(test_maze.get(center.step(SOUTH)).get_color(), 5)
       self.assertEqual(test_maze.get(center.step(WEST)).get_color(), 7)
       def kset(direction):
           return test_maze.get_kruskal_set(test_maze.get(center.step(direction)).get_id())
       # now make sure the kruskal set numbers for the north and south neighbors are the same
       self.assertEqual(kset(NORTH), kset(SOUTH))
       # and east and west
       self.assertEqual(kset(EAST), kset(WEST))
       self.assertNotEqual(kset(NORTH), kset(WEST))
   def test_kruskal_weave_color(self):
       # has_under_cell
       test_maze = Maze(3, 3, 'U')
       test_maze.set_up_unlinked_kruskal()
       test_maze.color_all(13)
       center = Coord(1,1)
       test_maze.kruskal_weave_over_under_cross(center)
       test_maze.color_all(11)
       over_cell = test_maze.get(center)
       self.assertTrue(over_cell.has_under_cell())
       under_cell = over_cell.get_under_cell()
       self.assertEqual(11, under_cell.get_color())
   def test_all_nextdoor_pairs(self):
       test_maze = Maze(3, 3, 'T')
       n = test_maze.all_nextdoor_pairs()
       self.assertEqual(len(n), 12)
   def test_kruskal(self):
       test_maze = Maze(3, 3, 'T')
       test_maze.kruskal()
       #self.debug_print_maze(test_maze)
       cycles = test_maze.color_from(5, Coord(0, 0))
       self.assertEqual(cycles, 0)
       self.assertEqual(test_maze.get(Coord(1,1)).get_color(), 5)
   def test_color_from_kruskal(self):
       test_maze = Maze(3, 3, 'T')
       test_maze.set_up_unlinked_kruskal()
       test_maze.kruskal_weave_over_under_cross(Coord(1,1))
       test_maze.kruskal_join(test_maze.get(Coord(0,0)),SOUTH,test_maze.get(Coord(1,0)))
       test_maze.kruskal_join(test_maze.get(Coord(0,0)),EAST,test_maze.get(Coord(0,1)))
       test_maze.kruskal_join(test_maze.get(Coord(2,1)),EAST,test_maze.get(Coord(2,2)))
       test_maze.kruskal_join(test_maze.get(Coord(1,2)),NORTH,test_maze.get(Coord(0,2)))
       test_maze.kruskal_join(test_maze.get(Coord(2,0)),EAST,test_maze.get(Coord(2,1)))
       cycles = test_maze.color_from(5, Coord(0, 0))
       self.assertEqual(cycles, 0)
       self.debug_print_maze(test_maze)
       self.debug_print_under_maze(test_maze)
       self.debug_print_maze_colors(test_maze)
   def test_kruskal_weave(self):
       test_maze = Maze(20, 20, 'K')
       #test_maze.debug = True
       test_maze.kruskal_weave(5)
#       self.debug_print_maze(test_maze)
       test_maze.color_all(0)
       cycles = test_maze.color_from(1, Coord(0,0))
#       self.debug_print_maze_colors(test_maze)
#       self.debug_print_under_maze(test_maze)
       self.assertEqual(cycles, 0) ####################################################### this sometimes fails!!!!!!!!!!!!!!!!!!!!!!
       self.assertEqual(test_maze.get(Coord(4,10)).get_color(), 1) # all connected
   def test_kruskal_exclusion(self):
       test_maze = Maze(5, 5, 'T')
       test_maze.set_up_unlinked_kruskal()
       test_maze.kruskal_weave_over_under_cross(Coord(2,2))
       for x1 in range(5):
           for y1 in range(5):
               c1 = Coord(x1,y1)
               answer = test_maze.kruskal_weave_over_under_cross(c1)
               if answer:
                   print('kruskal_weave_over_under_cross %s' % (c1))
               self.assertFalse(answer)
   def test_kruskal_cycle_cw(self):
       test_maze = Maze(5, 5, 'T')
       test_maze.set_up_unlinked_kruskal()
       test_maze.kruskal_weave_over_under_cross(Coord(2,2))
       # can_kruskal_join
       c1 = Coord(1,1)
       c2 = c1.step(EAST)
       if not test_maze.can_kruskal_join(test_maze.get(c1), test_maze.get(c2)):
           self.fail('Cant join c1 and c2')
       test_maze.kruskal_join(test_maze.get(c1), EAST, test_maze.get(c2))
       c3 = c2.step(EAST)
       if not test_maze.can_kruskal_join(test_maze.get(c2), test_maze.get(c3)):
           self.fail('Cant join c2 and c3')
       test_maze.kruskal_join(test_maze.get(c2), EAST, test_maze.get(c3))
       c4 = c3.step(SOUTH)
       if not test_maze.can_kruskal_join(test_maze.get(c3), test_maze.get(c4)):
           self.fail('Cant join c3 and c4')
       test_maze.kruskal_join(test_maze.get(c3), SOUTH, test_maze.get(c4))
       c5 = c4.step(SOUTH)
       if not test_maze.can_kruskal_join(test_maze.get(c4), test_maze.get(c5)):
           self.fail('Cant join c4 and c5')
       test_maze.kruskal_join(test_maze.get(c4), SOUTH, test_maze.get(c5))
       c6 = c5.step(WEST)
       self.assertFalse(test_maze.can_kruskal_join(test_maze.get(c5), test_maze.get(c6)))



class Zone(object):
   def __init__(self, total_x, total_y, maze_x, maze_y, hollow):
      self.total_x = total_x
      self.total_y = total_y
      self.maze_x = maze_x
      self.maze_y = maze_y
      self.X = total_x * maze_x
      self.Y = total_y * maze_y
      self.hollow = hollow # center zone has no maze/is one large open space
      self.grid = [[Maze(maze_x, maze_y, '_Maze_%d_%d' % (x,y)) for y in range(total_y)] for x in range(total_x)] # grid of mazes
      if hollow:
         self.grid[total_x//2][total_y//2] = None
   def prepare(self, shuffle, inner_style=BI_SPI, outer_shuffle=None, outer_style=BI_SPI):
      for x in range(self.total_x):
         for y in range(self.total_y):
            if self.grid[x][y] is not None:
               self.grid[x][y].connect_all(inner_style)
               for i in range(shuffle):
                  self.grid[x][y].move_door()
      self._link(outer_shuffle, outer_style)
   def _link(self, outer_shuffle, outer_style):
      self.link_map = Maze(self.total_x, self.total_y, 'link_map')
      self.link_map.connect_all(outer_style)
      shuffle_count = outer_shuffle if outer_shuffle is not None else self.total_x * self.total_y
      for i in range(shuffle_count):
         self.link_map.move_door()
      for x in range(self.total_x):
         for y in range(self.total_y):
            c = Coord(x, y)
            z = self.link_map.get(c)
            for d in range(2): # only cover half the directions because the other side of the door has the opposite direction and will be covered
               if z.has_door(d):
                  self._connect(x, y, d)
   def _connect(self, x, y, direction):
      maze_1 = self.grid[x][y]
      c = Coord(x, y).step(direction)
      maze_2 = self.grid[c.x][c.y]
      delta = random.randint(0, min(self.maze_x, self.maze_y)-1)
      m1_coord = self._delta_of_wall(direction, delta)
      m2_coord = self._delta_of_wall(opposite_direction(direction), delta)
      c1 = maze_1.get(m1_coord)
      c2 = maze_2.get(m2_coord)
      door = Door(c1, direction, c2)
      c1.add_door(direction, door)
      c2.add_door(opposite_direction(direction), door)
   def _center_of_wall(self, direction):
      x = (0, self.maze_x//2, self.maze_x-1, self.maze_x//2)[direction]
      y = (self.maze_y//2, self.maze_y-1, self.maze_y//2, 0)[direction]
      return Coord(x,y)
   def _delta_of_wall(self, direction, delta):
      x = (0, delta, self.maze_x-1, delta)[direction]
      y = (delta, self.maze_y-1, delta, 0)[direction]
      return Coord(x,y)
   def open_outer_walls(self):
      self.get(Coord(0, 0)).add_door(WEST, Door(self.get(Coord(0, 0)), WEST, None))
      self.get(Coord(self.X-1,self.Y-1)).add_door(EAST, Door(None, EAST, self.get(Coord(self.X-1,self.Y-1))))
   def get(self, coord):
      # compute zone x and y from coord, and then create an adjusted coord
      # if hollow, return a room with doors on all sides
      x_maze = coord.x // self.maze_x
      y_maze = coord.y // self.maze_y
      #print('zone maze getting maze at (%d, %d), then down to (%d, %d)' % (x_maze, y_maze, coord.x % self.maze_x, coord.y % self.maze_y))
      maze = self.grid[x_maze][y_maze]
      c = Coord(coord.x % self.maze_x, coord.y % self.maze_y)
      return maze.get(c)




class TestZone(unittest.TestCase):
   def test_init_hollow(self):
      z = Zone(3, 3, 4, 4, True)
      self.assertEqual(z.grid[1][1], None)
   def test_init_not_hollow(self):
      z = Zone(3, 3, 4, 4, False)
      self.assertNotEqual(z.grid[1][1], None)
   def test_get_1(self):
      z = Zone(3, 3, 4, 4, False)
      c = z.get(Coord(0, 0))
      self.assertEqual(str(c), 'Cell_Maze_0_0(0,0)')
      c = z.get(Coord(3, 3))
      self.assertEqual(str(c), 'Cell_Maze_0_0(3,3)')
      c = z.get(Coord(4, 4))
      self.assertEqual(str(c), 'Cell_Maze_1_1(0,0)')
   def test_prepare_0(self):
      z = Zone(3, 3, 4, 4, False)
      z.prepare(0)
   def test_prepare_5(self):
      z = Zone(3, 3, 4, 4, False)
      z.prepare(5)
      z.open_outer_walls()



class Point(object):
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    def __str__(self):
        return '(%f,%f)' % (self.x, self.y)
    def __repr__(self):
        return str(self)
    def get_x(self):
        return self.x
    def get_y(self):
        return self.y
    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)
    def __ne__(self, other):
        return not self.__eq__(other)

class DirectionVector(object):
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1
        self.delta_x = p1.x - p0.x
        self.delta_y = p1.y - p0.y
    def perp(self):
        new_vector = DirectionVector(self.p0, self.p1)
        new_vector.delta_x = -self.delta_y
        new_vector.delta_y = self.delta_x
        return new_vector
    def dot(self, other):
        return (self.delta_x * other.delta_x) + (self.delta_y * other.delta_y)
    def are_parallel(self, other):
        return other.dot(self.perp()) == 0

class TestDirectionVector(unittest.TestCase):
    def test_perp(self):
        dv1 = DirectionVector(Point(1,1), Point(2,2))
        dv2 = dv1.perp()
        self.assertEqual(dv2.delta_x, -1)
        self.assertEqual(dv2.delta_y, 1)
    def test_are_parallel_1(self):
        dv1 = DirectionVector(Point(1,1), Point(2,2))
        dv2 = DirectionVector(Point(1,3), Point(2,4))
        self.assertTrue(dv1.are_parallel(dv2))
    def test_are_parallel_2(self):
        dv1 = DirectionVector(Point(1,1), Point(2,2))
        dv2 = DirectionVector(Point(1,3), Point(2,5))
        self.assertFalse(dv1.are_parallel(dv2))

class Line(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.dv = DirectionVector(p1, p2)
    def __str__(self):
        return 'Line{%s->%s}' % (self.p1, self.p2)
    def __repr__(self):
        return str(self)
    def get_p1(self):
        return self.p1
    def get_p2(self):
        return self.p2
    def slope(self):
        return self.m
    def intercept(self):
        return self.b
    def _slope(self):
        return float(self.p2.y - self.p1.y)/float(self.p2.x - self.p1.x)
    def _intercept(self):
        return self.p2.y - (self.p2.x * self._slope())
    def project_x(self, x):
        return (self.m * x) + self.b
    def project_y(self, y):
        return (y - self.b) / self.m
    def in_x_segment(self, x):
        if self.p1.x < self.p2.x:
            return (self.p1.x <= x) and (x <= self.p2.x)
        else:
            return (self.p2.x <= x) and (x <= self.p1.x)
    def in_y_segment(self, y):
        if self.p1.y < self.p2.y:
            return (self.p1.y <= y) and (y <= self.p2.y)
        else:
            return (self.p2.y <= y) and (y <= self.p1.y)
    def parallel(self, other):
        return self.dv.are_parallel(other.dv)
    def coincide(self, other): # invalid if not parallel
        dv = DirectionVector(self.p1, other.p1)
        return self.dv.are_parallel(dv)
    def in_x_range(self, x):
        return min(self.p1.x, self.p2.x) < x < max(self.p1.x, self.p2.x)
    def intersect(self, other):
        # http://geomalgorithms.com/a05-_intersect-1.html
        if self.parallel(other):
            if self.coincide(other):
                return (self.in_x_range(other.p1.x)) or (self.in_x_range(other.p2.x)) or (other.in_x_range(self.p1.x)) or (other.in_x_range(self.p2.x))
            else:
                return False
        w = DirectionVector(other.p1, self.p1)
        v = other.dv
        u = self.dv
        s_intersect = ((v.delta_y*w.delta_x)-(v.delta_x*w.delta_y))/((v.delta_x*u.delta_y)-(v.delta_y*u.delta_x))
        #print('s_intersect = %f' % (s_intersect))
        return 0.0 < s_intersect < 1.0

class TestLine(unittest.TestCase):
    def test_coincide(self):
        l1 = Line(Point(0,0), Point(4,2))
        l2 = Line(Point(0,1), Point(4,3))
        l3 = Line(Point(8,4), Point(12,6))
        self.assertTrue(l1.parallel(l2))
        self.assertFalse(l1.coincide(l2))
        self.assertTrue(l1.parallel(l3))
        self.assertTrue(l1.coincide(l3))

class PathMaker(object):
    def __init__(self, span_x, span_y, inner_point_count):
        self.span_x = span_x
        self.span_y = span_y
        self.inner_point_count = inner_point_count
    def make_unordered_point_list(self):
        point_list = [Point(0,0)]
        self.inner_points = []
        for p in range(self.inner_point_count):
            x = random.randint(0, self.span_x-1)
            y = random.randint(0, self.span_y-1)
            point_list += [Point(x,y)]
            self.inner_points += [Point(x,y)]
        point_list += [Point(self.span_x-1, self.span_y-1)]
        self.point_list = point_list
        return point_list
    def cross(self, line_1, line_2):
        try:
            return line_1.intersect(line_2)
        except:
            return line_2.intersect(line_1)
    def point_list_to_line_list(self, point_list=None):
        if point_list is None:
            point_list = self.point_list
        ll = []
        for i in range(len(point_list)-1):
            ll.append(Line(point_list[1], point_list[i+1]))
        self.line_list = ll
        return ll
    def has_cross(self, ll=None):
        if ll is None:
            ll = self.line_list
        for l1 in ll:
            for l2 in ll:
                if (not l1 == l2) and self.cross(l1, l2):
                    #print('l1 %s crosses l2 %s' % (str(l1), str(l2)))
                    return True
        return False
    def a_non_crossing_path(self):
        for option in itertools.permutations(self.inner_points, len(self.inner_points)):
            ll = self.augmented_line(option)
            if not self.has_cross(ll):
                return ll
        return None
    def augmented_line(self, inner_point_list):
        ll = [Line(Point(0,0), inner_point_list[0])]
        for pi in range(len(inner_point_list)-1):
            p1 = inner_point_list[pi]
            p2 = inner_point_list[pi+1]
            ll += [Line(p1, p2)]
        ll += [Line(inner_point_list[-1], Point(self.span_x-1, self.span_y-1))]
        return ll
    def first_point(self):
        return Point(0,0)
    def last_point(self):
        return Point(self.span_x-1, self.span_y-1)
    def random_point(self):
        x = random.randint(0, self.span_x-1)
        y = random.randint(0, self.span_y-1)
        return Point(x,y)
    def random_point_near(self, point):
        DELTA = 10
        print('random_point_near x range: %d .. %d' % (max(0, int(point.get_x())-DELTA), min(self.span_x-1, int(point.get_x())+DELTA)))
        x = random.randint(max(0, int(point.get_x())-DELTA), min(self.span_x-1, int(point.get_x())+DELTA))
        print('random_point_near y range: %d .. %d' % (max(0, int(point.get_y())-DELTA), min(self.span_y-1, int(point.get_y())+DELTA)))
        y = random.randint(max(0, int(point.get_y())-DELTA), min(self.span_y-1, int(point.get_y())+DELTA))
        print('random_point_near x: %d -> %d, y: %d -> %d' % (int(point.get_x()), x, int(point.get_y()), y))
        return Point(x,y)
    def crosses(self, line_list, candidate):
        for line in line_list:
            if self.cross(line, candidate):
                return True
        return False
    def new_path(self, inner_point_count=None):
        if inner_point_count is None:
            inner_point_count = self.inner_point_count
        working_from = [self.first_point(), self.last_point()]
        lines = []
        for x in range(inner_point_count):
            working = working_from[0]
            del working_from[0]
            next_point = self.random_point_near(working)
            next_line = Line(working, next_point)
            while self.crosses(lines, next_line):
                next_point = self.random_point_near(working)
                next_line = Line(working, next_point)
            lines += [next_line]
            print('Adding line %s' % (str(next_line)))
            working_from += [next_point]
        last_line = Line(working_from[0], working_from[1])
        print('Last line %s (%s)' % (str(last_line), 'crosses!' if self.crosses(lines, last_line) else 'not crossing'))
        lines += [last_line]
        # does this cross?
        return lines

class TestPathMaker(unittest.TestCase):
    def setUp(self):
        self.path_maker = PathMaker(10, 20, 4)
    def test_make_unordered_point_list(self):
        path = self.path_maker.make_unordered_point_list()
        self.assertEqual(len(path), 6)
    def test_cross_1(self):
        l_1 = Line(Point(1,1), Point(9,9))
        l_2 = Line(Point(1,9), Point(9,1))
        self.assertTrue(self.path_maker.cross(l_1, l_2))
    def test_cross_2(self):
        l_1 = Line(Point(1,1), Point(2,2))
        l_2 = Line(Point(3,3), Point(4,4))
        self.assertFalse(self.path_maker.cross(l_1, l_2))
    def test_line_list(self):
        path = self.path_maker.make_unordered_point_list()
        ll = self.path_maker.point_list_to_line_list(path)
        self.assertEqual(len(ll), 5)
        #if self.path_maker.has_cross(ll):
        #    print('has_cross')
    def test_line_list2(self):
        path_maker = PathMaker(10, 20, 2)
        path = path_maker.make_unordered_point_list()
        ll = path_maker.point_list_to_line_list(path)
        self.assertEqual(len(ll), 3)
        #if self.path_maker.has_cross(ll):
        #    print('has_cross')
    def test_augmented_line(self):
        inner = [Point(2,2), Point(4,4), Point(8,8)]
        answer = self.path_maker.augmented_line(inner)
        #print(str(answer))
        self.assertFalse( self.path_maker.has_cross(answer) )
    def test_a_non_crossing_path(self):
        self.path_maker.make_unordered_point_list()
        foo = self.path_maker.a_non_crossing_path()
        #print(str(foo))

class PathMaker2(object):
    COLOR = 7
    def __init__(self, grid_x, grid_y, sub_x, sub_y):
        '''grid_x and grid_y define the x,y grid that the path goes through, sub_x and sub_y define the geometry of each grid.'''
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.sub_x = sub_x
        self.sub_y = sub_y
        self.total_x = grid_x * sub_x
        self.total_y = grid_y * sub_y
        self.start = Coord(0,0)
        self.grid_end = Coord(self.grid_x-1, self.grid_y-1)
        self.sub_end = Coord(self.sub_x-1, self.sub_y-1)
    def _make_master_path(self, style=R_WALK):
        link_map = Maze(self.grid_x, self.grid_y, 'link_map')
        link_map.connect_all(style)
        master_path = link_map.path_from_to(self.start, self.grid_end, self.COLOR)
        return master_path
    def _intergrid_door(self, direction):
        delta = random.randint(0, self._wall_length((direction+1)%4)-1)
        m1_coord = self._delta_of_wall(direction, delta)
        m2_coord = self._delta_of_wall(opposite_direction(direction), delta)
        return (m1_coord, m2_coord)
    def _wall_length(self, direction):
        if (direction == NORTH) or (direction == SOUTH):
            return self.sub_x
        else:
            return self.sub_y
    def _delta_of_wall(self, direction, delta):
        x = (0, delta, self.sub_x-1, delta)[direction]
        y = (delta, self.sub_y-1, delta, 0)[direction]
        return Coord(x,y)
    def _inner_coordinates(self, master_path):
        inner = [self.start]
        for i in range(len(master_path)-1):
            d = master_path[i].direction_to_other(master_path[i+1])
            (m1, m2) = self._intergrid_door(d)
            inner.append(m1)
            inner.append(m2)
        inner.append(self.sub_end)
        return inner
    def _inner_subpath(self, start, end, style=R_WALK):
        grid = Maze(self.sub_x, self.sub_y, 'zone')
        grid.connect_all(style)
        subpath = grid.path_from_to(start, end, self.COLOR)
        return subpath
    def _translate_path(self, x, y, path):
        new_path = []
        for p in path:
            new_x = p.x + (x * self.sub_x)
            new_y = p.y + (y * self.sub_y)
            new_path += [Coord(new_x, new_y)]
        return new_path
    def _link_master_path(self, master_path, inner_style=R_WALK):
        path = []
        inner = self._inner_coordinates(master_path)
        for i in range(len(master_path)):
            s = inner[i*2]
            e = inner[(i*2)+1]
            p = self._inner_subpath(s, e, inner_style)
            pp = self._translate_path(master_path[i].x, master_path[i].y, p)
            path.extend(pp)
        return path
    def make_path(self, outer_style=R_WALK, inner_style=R_WALK):
        mp = self._make_master_path(outer_style)
        return self._link_master_path(mp, inner_style)
        


class TestPathMaker2(unittest.TestCase):
    def test_make_master_path(self):
        uut = PathMaker2(3, 3, 5, 5)
        mp = uut._make_master_path(ZIGZAG)
        #print(str(mp))
        self.assertEqual(mp[0], Coord(0,0))
        self.assertEqual(mp[1], Coord(0,1))
        self.assertEqual(mp[4], Coord(1,1))
        self.assertEqual(mp[7], Coord(2,1))
        self.assertEqual(mp[8], Coord(2,2))
    def test_wall_length(self):
        uut = PathMaker2(3,3,5,20)
        l = uut._wall_length(EAST)
        self.assertEqual(l, 20, 'the length of the EAST wall should be 20, was %d'%(l))
    def test_intergrid_door(self):
        uut = PathMaker2(3, 3, 200, 2)
        (m1, m2) = uut._intergrid_door(NORTH)
        self.assertEqual(m1.x, 0)
        self.assertTrue(0 <= m1.y < 2, 'm1 (%s) should be a coordinate on the NORTH wall with x=0 and y as 0 or 1' % (str(m1)))
        self.assertEqual(m2.x, 199)
        self.assertTrue(0 <= m2.y < 2)
        self.assertEqual(m1.y, m2.y)
    def test_inner_coordinates(self):
        uut = PathMaker2(3, 3, 200, 2)
        path = uut._inner_coordinates(uut._make_master_path(ZIGZAG))
        self.assertEqual(len(path), 18)
        self.assertEqual(path[0], Coord(0,0))
        self.assertEqual(path[17], Coord(199,1))
        self.assertEqual(Coord(0,0).direction_to_other(Coord(0,1)), EAST) # zigzag starts out easterly
        self.assertEqual(path[1].y, 1)
        self.assertEqual(path[1].x, path[2].x)
        self.assertEqual(path[2].y, 0)
    def test_translate_path(self):
        uut = PathMaker2(3, 3, 2, 2)
        t = uut._translate_path(1, 1, [Coord(0,0), Coord(0,1), Coord(1,1)])
        self.assertEqual(t[0], Coord(2,2))
    def test_inner_subpath(self):
        uut = PathMaker2(3, 3, 5, 5)
        s = uut._inner_subpath(Coord(0,3), Coord(2,4), ZIGZAG)
        #print(str(s))
        self.assertEqual(len(s), 12, 'The length of a ZIGZAG path through a 5x5 maze from (0,3) to (2,4) should be 12 (was %d)' % len(s))


class BreadthFirstSearchColorTool(object):
   def __init__(self, graph, start_location, color):
      self.graph = graph
      self.starting_cell = graph.get(start_location)
      self.color = color
      self.cycles = 0
      self.cells_to_explore = []
   def color_graph(self):
      self.verify_precondition_color_not_in_use()
      self.explore_first_cell()
      while self.there_are_cells_to_explore():
         self.explore_next_cell()
   def get_cycle_count(self):
      return self.cycles

   def verify_precondition_color_not_in_use(self):
      if len(self.graph.get_all_color(self.color)) != 0:
         raise Exception('color %s in use' % (self.color))
   def explore_first_cell(self):
      self.explore_cell(self.starting_cell)
   def explore_next_cell(self):
      next_cell = self.take_cell_from_list(self.cells_to_explore)
      self.explore_cell(next_cell)
   def explore_cell(self, current_cell):
      current_cell.set_color(self.color)
      self.cycles += self.cycles_from_this_cell(current_cell)
      self.cells_to_explore += self.neighbors_of_a_different_color(current_cell)
   def there_are_cells_to_explore(self):
      return len(self.cells_to_explore) != 0
   def take_cell_from_list(self, cell_list):
      # Taking the first of the list makes this breadth first.
      next_cell = cell_list[0]
      del(cell_list[0])
      return next_cell
   def neighbors_of_a_different_color(self, cell):
      return [neighbor for neighbor in cell.get_neighbors() \
              if not neighbor.is_color(self.color)]
   def neighbors_of_the_same_color(self, cell):
      return [neighbor for neighbor in cell.get_neighbors() \
              if neighbor.is_color(self.color)]
   def cycles_from_this_cell(self, cell):
      neighbors_of_the_same_color = self.neighbors_of_the_same_color(cell)
      same_color_count = len(neighbors_of_the_same_color)
      if same_color_count > 1: # 1 is the (non cycle) neighbor that brought us here
         return same_color_count - 1
      return 0

class RefactorPlayMaze(Maze):
   def color_from(self, color, coordinate):
      # Keep old name until calling code can be refactored
      return self.color_reachable_cells_and_report_cycles(color, coordinate)

   def color_reachable_cells_and_report_cycles(self, color, coordinate):
      color_tool = BreadthFirstSearchColorTool(self, coordinate, color)
      color_tool.color_graph()
      return color_tool.get_cycle_count()

class TestRefactorPlayMaze(unittest.TestCase):
   def setUp(self):
      self.maze = RefactorPlayMaze(5, 10, 'Q')
   def test_take_cell_from_list(self):
      cells = [1, 2, 3, 4]
      color_tool = BreadthFirstSearchColorTool(self.maze, Coord(2,4), 2)
      x = color_tool.take_cell_from_list(cells)
      self.assertEqual(x, 1)
      self.assertEqual(len(cells), 3)
   def test_color_all(self):
      self.maze.color_all(3)
      self.assertEqual(self.maze.get(Coord(4,9)).get_color(), 3)
   def test_color_from_1(self):
      self.maze.zigzag_connect_all() # all are now connected
      self.maze.color_from(8, Coord(2,4))
      self.assertEqual(self.maze.get(Coord(4,9)).get_color(), 8)
      self.assertEqual(self.maze.get(Coord(0,0)).get_color(), 8)
      self.assertEqual(self.maze.get(Coord(2,5)).get_color(), 8)
   def test_color_from_2(self):
      self.maze.zigzag_connect_all() # all are now connected
      cycle_count = self.maze.color_from(8, Coord(2,4))
      self.assertEqual(cycle_count, 0)

   def test_color_from_3(self):
      self.maze.zigzag_connect_all() # all are now connected
      (c, d) = self.maze.pick_random_door()
      self.maze.remove_door(c, d)
      self.maze.color_from(8, Coord(0,0))
      self.assertEqual(self.maze.get(Coord(4,9)).get_color(), 0)

