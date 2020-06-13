import unittest

# directions
NORTH = 0
EAST  = 1
SOUTH = 2
WEST  = 3

def opposite_direction(direction):
   return (direction+2)%4


class Coord(object):
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
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
    def get_x(self):
        return self.x
    def get_y(self):
        return self.y
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
