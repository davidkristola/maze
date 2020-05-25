import Tkinter
import sys
import unittest
import random

class FibApp(object):
   HEIGHT = 1150
   WIDTH = 800
   X = 30
   Y = 40
   MOVES = 1100
   def __init__(self, master):
      self.frame = Tkinter.Frame(master)
      self.frame.pack()
      self.button_quit = Tkinter.Button(self.frame, text='Quit', command=self.frame.quit)
      self.button_quit.pack(side=Tkinter.LEFT)
      self.button_print = Tkinter.Button(self.frame, text='Print', command=self.print_window)
      self.button_print.pack(side=Tkinter.LEFT)
      self.button_draw = Tkinter.Button(self.frame, text='Draw', command=self.draw_next_maze)
      self.button_draw.pack(side=Tkinter.RIGHT)
      self.area = Tkinter.Canvas(master, width=self.WIDTH, height=self.HEIGHT)
      self.area.pack(side=Tkinter.RIGHT)
      self.s = self.WIDTH/(self.X+2)

   def clear_canvas(self):
      for i in self.area.find_all():
         self.area.delete(i)

   def prepare_maze(self):
      self.maze = Maze(self.X, self.Y)
      self.maze.zigzag_connect_all()
      for i in range(self.MOVES):
         self.maze.move_door()
      self.maze.get(Coord(0,0)).add_door(WEST, 'door')
      self.maze.get(Coord(self.X-1,self.Y-1)).add_door(EAST, 'door')

   def draw_next_maze(self):
      self.clear_canvas()
      self.prepare_maze()
      self.draw_maze()

   def draw_maze(self):
      for x in range(self.X):
         for y in range(self.Y):
            x1 = (x+1) * self.s
            y1 = (y+1) * self.s
            x2 = x1 + self.s
            y2 = y1 + self.s
            self.draw_cell_at(x1, y1, Coord(x, y))
            #self.area.create_rectangle(x1, y1, x2, y2)

   def draw_cell_at(self, x, y, coord):
      cell = self.maze.get(coord)
      (x1, y1) = (x, y)
      for direction in range(4):
         (x2, y2) = self.step(direction, x1, y1)
         if not cell.has_door(direction):
            self.area.create_line(x1, y1, x2, y2) # wall
         else:
            pass # open, draw nothing
         (x1, y1) = (x2, y2)

   def step(self, direction, x, y):
      new_x = x + (0, self.s, 0, -self.s)[direction]
      new_y = y + (self.s, 0, -self.s, 0)[direction]
      return (new_x, new_y)

   def print_window(self):
      self.area.postscript(file='maze.ps')

# directions
NORTH = 0
EAST  = 1
SOUTH = 2
WEST  = 3

def opposite_direction(direction):
   return (direction+2)%4

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


class Cell(object):
   def __init__(self, coord):
      self.coord = coord
      self.doors = [None for x in range(4)] # no doors in any of the directions
      self.color = 0
   def set_color(self, color):
      self.color = color
   def get_color(self):
      return self.color
   def is_color(self, color):
      return self.color == color
   def __str__(self):
      return 'Cell%s' % (self.coord)
   def __repr__(self):
      return str(self)
   def has_door(self, direction):
      return self.doors[direction] is not None
   def get_doors(self):
      return [d for d in self.doors if d is not None]
   def add_door(self, direction, door):
      self.doors[direction] = door
   def get_coord(self):
      return self.coord
   def get_neighbors(self):
      doors = self.get_doors()
      return [d.get_other_side(self) for d in doors]

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

class Coord(object):
   def __init__(self, x, y):
      self.x = x
      self.y = y
   def __eq__(self, other):
      return (self.x == other.x) and (self.y == other.y)
   def step(self, direction):
      new_x = self.x + (-1,  0, +1,  0)[direction]
      new_y = self.y + ( 0, +1,  0, -1)[direction]
      return Coord(new_x, new_y)
   def __str__(self):
      return '(%d,%d)' % (self.x, self.y)
   def __repr__(self):
      return str(self)

class TestCoord(unittest.TestCase):
   def test_eq(self):
      a = Coord(1, 4)
      b = Coord(4, 1)
      c = Coord(1, 4)
      self.assertTrue(a == c)
      self.assertFalse(a == b)
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

class Maze(object):
   def __init__(self, height, width):
      self.width = width
      self.height = height
      self.grid = [[Cell(Coord(x, y)) for y in range(width)] for x in range(height)] # grid of cells
   def get(self, coord):
      return self.grid[coord.x][coord.y]
   def add_door(self, coord, direction):
      #print('Add door from %s %s to %s' % (coord, ('N', 'E', 'S', 'W')[direction], coord.step(direction)))
      start = self.get(coord)
      end = self.get(coord.step(direction))
      door = Door(start, direction, end)
      start.add_door(direction, door)
      end.add_door(opposite_direction(direction), door)
   def remove_door(self, coord, direction):
      first = self.get(coord)
      second = self.get(coord.step(direction))
      first.add_door(direction, None)
      second.add_door(opposite_direction(direction), None)
   def zigzag_connect_all(self):
      for x in range(self.height):
         for y in range(self.width - 1):
            self.add_door(Coord(x, y), EAST)
      right = True
      for x in range(self.height - 1):
         y = self.width-1 if right else 0
         self.add_door(Coord(x, y), SOUTH)
         right = not right
   def get_neighbors(self, coord):
      it = self.get(coord)
      return it.get_neighbors()
   def color_all(self, color):
      for x in range(self.height):
         for y in range(self.width):
            self.grid[x][y].set_color(color)
   def color_from(self, color, coord):
      x = self.get(coord)
      x.set_color(color)
      explore = x.get_neighbors()
      while len(explore) != 0:
         x = explore[0]
         del(explore[0])
         x.set_color(color)
         explore += [y for y in x.get_neighbors() if y.get_color() != color]
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
      print('WARNING: %s has no doors!' % (focus))
      return self.pick_random_door() # try a different one
   def invalid_coordinate(self, coord):
      if coord.x < 0 or coord.x >= self.height:
         return True
      if coord.y < 0 or coord.y >= self.width:
         return True
      return False
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

class TestMaze(unittest.TestCase):
   def setUp(self):
      self.maze = Maze(5, 10)
   def test_index(self):
      self.assertEqual(len(self.maze.grid), 5)
      self.assertEqual(len(self.maze.grid[0]), 10)
   def test_get(self):
      x2y7 = self.maze.get(Coord(2, 7))
      self.assertEqual(str(x2y7), 'Cell(2,7)')
   def test_add_door(self):
      self.maze.add_door(Coord(3, 3), NORTH)
      c1 = self.maze.get(Coord(3, 3))
      c2 = self.maze.get(Coord(2, 3))
      doors1 = c1.get_doors()
      doors2 = c2.get_doors()
      self.assertEqual(doors1, doors2)
      self.assertEqual(len(doors1), 1)
   def test_zigzag(self):
      self.maze.zigzag_connect_all()
      zero = self.maze.get(Coord(0, 0))
      doors = zero.get_doors()
      #print(str(doors))
      one = self.maze.get(Coord(0, 1))
      n = self.maze.get_neighbors(Coord(0, 0))
      self.assertEqual(n, [one])
      self.assertTrue(self.maze.get(Coord(0, 9)) in self.maze.get_neighbors(Coord(1, 9)))
      self.assertTrue(self.maze.get(Coord(1, 0)) in self.maze.get_neighbors(Coord(2, 0)))
   def test_color_all(self):
      self.maze.color_all(3)
      self.assertEqual(self.maze.get(Coord(4,9)).get_color(), 3)
   def test_color_from_1(self):
      self.maze.zigzag_connect_all() # all are now connected
      self.maze.color_from(8, Coord(2,4))
      self.assertEqual(self.maze.get(Coord(4,9)).get_color(), 8)
      self.assertEqual(self.maze.get(Coord(0,0)).get_color(), 8)
      self.assertEqual(self.maze.get(Coord(2,5)).get_color(), 8)
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


def run_program():
   root = Tkinter.Tk()
   app = FibApp(root)
   root.mainloop()
   root.destroy()

if __name__ == "__main__":
    run_program()
    #int(sys.argv[1])
