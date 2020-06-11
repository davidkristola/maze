import unittest
from Coord import *

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
    def coord(self):
        #TODO: use round
        return Coord(int(self.x),int(self.y))

class TestPoint(unittest.TestCase):
    def test_coord(self):
        self.assertEqual(Coord(3,4), Point(3.001,4.001).coord())

class DirectionVector(object):
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1
        self.delta_x = p1.x - p0.x
        self.delta_y = p1.y - p0.y
    def perpendicular(self):
        new_vector = DirectionVector(self.p0, self.p1)
        new_vector.delta_x = -self.delta_y
        new_vector.delta_y = self.delta_x
        return new_vector
    def dot(self, other):
        return (self.delta_x * other.delta_x) + (self.delta_y * other.delta_y)
    def are_parallel(self, other):
        #TODO: use math.close
        return other.dot(self.perpendicular()) == 0
    def xy(self, other):
        return self.delta_x*other.delta_y

class TestDirectionVector(unittest.TestCase):
    def test_perpendicular(self):
        dv1 = DirectionVector(Point(1,1), Point(2,2))
        dv2 = dv1.perpendicular()
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
        self.debug = False
    def __eq__(self, other):
        if type(self) is not type((other)):
            return False
        return (self.p1 == other.p1) and (self.p2 == other.p2)
    def __ne__(self, other):
        return not self.__eq__(other)
    def __str__(self):
        return 'Line{%s->%s}' % (self.p1, self.p2)
    def __repr__(self):
        return str(self)
    def get_p1(self):
        return self.p1
    def get_p2(self):
        return self.p2
    def parallel(self, other):
        return self.dv.are_parallel(other.dv)
    def coincide(self, other): # invalid if not parallel
        dv = DirectionVector(self.p1, other.p1)
        return self.dv.are_parallel(dv)
    def in_x_range(self, x):
        return min(self.p1.x, self.p2.x) < x < max(self.p1.x, self.p2.x)
    def intersect(self, other):
        """
        Returs True if this line intersects other.
        """
        if type(self) is not type((other)):
            # other must be a Cross
            return other.intersect(self)
        # http://geomalgorithms.com/a05-_intersect-1.html
        if self.parallel(other):
            if self.coincide(other):
                return (self.in_x_range(other.p1.x)) or (self.in_x_range(other.p2.x)) or (other.in_x_range(self.p1.x)) or (other.in_x_range(self.p2.x))
            else:
                return False
        w = DirectionVector(other.p1, self.p1)
        v = other.dv
        u = self.dv
        #s_intersect = ((v.delta_y*w.delta_x)-(v.delta_x*w.delta_y))/((v.delta_x*u.delta_y)-(v.delta_y*u.delta_x))
        s_intersect = (w.xy(v)-v.xy(w))/(v.xy(u)-u.xy(v))
        t_intersect = (u.xy(w)-w.xy(u))/(u.xy(v)-v.xy(u))
        if self.debug:
            print('s = %f, t = %f' % (s_intersect, t_intersect))
        return (0.0 <= s_intersect <= 1.0) and (0.0 <= t_intersect <= 1.0)
    def intersection_point(self, other):
        # precondition: not parallel
        w = DirectionVector(other.p1, self.p1)
        v = other.dv
        u = self.dv
        s_intersect = (w.xy(v)-v.xy(w))/(v.xy(u)-u.xy(v))
        i_x = s_intersect*u.delta_x + self.p1.get_x()
        i_y = s_intersect*u.delta_y + self.p1.get_y()
        return Point(i_x, i_y)

class TestLine(unittest.TestCase):
    def test_coincide(self):
        l1 = Line(Point(0,0), Point(4,2))
        l2 = Line(Point(0,1), Point(4,3))
        l3 = Line(Point(8,4), Point(12,6))
        self.assertTrue(l1.parallel(l2))
        self.assertFalse(l1.coincide(l2))
        self.assertTrue(l1.parallel(l3))
        self.assertTrue(l1.coincide(l3))
    def test_equal(self):
        l1 = Line(Point(0,0), Point(4,2))
        self.assertEqual(l1, l1)
    def test_not_equal(self):
        l2 = Line(Point(0,1), Point(4,3))
        l3 = Line(Point(8,4), Point(12,6))
        self.assertNotEqual(l2,l3)
    def test_intersect1(self):
        l1 = Line(Point(0,0), Point(4,2))
        l2 = Line(Point(1,2), Point(3,1))
        self.assertTrue(l1.intersect(l2))
        self.assertTrue(l2.intersect(l1))
    def test_intersect2(self):
        l1 = Line(Point(0,0), Point(4,4))
        l2 = Line(Point(3,3), Point(5,5))
        self.assertTrue(l1.intersect(l2))
        self.assertTrue(l2.intersect(l1))
    def test_intersect3(self):
        l1 = Line(Point(0,0), Point(2,2))
        l2 = Line(Point(3,3), Point(5,5))
        self.assertFalse(l1.intersect(l2))
        self.assertFalse(l2.intersect(l1))
    def test_intersect4(self):
        l1 = Line(Point(0,0), Point(2,2))
        l2 = Line(Point(0,9), Point(9,0))
        self.assertFalse(l1.intersect(l2))
        self.assertFalse(l2.intersect(l1))
    def test_intersectin_point(self):
        l1 = Line(Point(0,0), Point(2,2))
        l2 = Line(Point(0,8), Point(8,0))
        i = Point(4,4)
        self.assertAlmostEqual(i.get_x(), l1.intersection_point(l2).get_x())
        self.assertAlmostEqual(i.get_y(), l1.intersection_point(l2).get_y())
        self.assertAlmostEqual(i.get_x(), l2.intersection_point(l1).get_x())
        self.assertAlmostEqual(i.get_y(), l2.intersection_point(l1).get_y())

class Cross(object):
    def __init__(self, coord):
        self.x = coord.get_x()
        self.y = coord.get_y()
    def intersect(self, other):
        if type(self) is not type((other)):
            # the other myst be a line
            my_lines = self.get_lines()
            return other.intersect(my_lines[0]) or other.intersect(my_lines[1])
        else:
            m = self.get_lines()
            o = other.get_lines()
            return m[0].intersect(o[0]) or m[0].intersect(o[1]) or m[1].intersect(o[0]) or m[1].intersect(o[1])
    def get_lines(self):
        return (Line(Point(self.x,self.y-1),Point(self.x,self.y+1)), Line(Point(self.x-1,self.y),Point(self.x+1,self.y)))

class TestCross(unittest.TestCase):
    def test_cross_line(self):
        cross = Cross(Coord(5,5))
        line = Line(Point(1,1),Point(9,9))
        self.assertTrue(cross.intersect(line))
    def test_line_cross(self):
        cross = Cross(Coord(5,5))
        line = Line(Point(1,1),Point(9,9))
        self.assertTrue(line.intersect(cross))
    def test_cross_cross(self):
        cross1 = Cross(Coord(5,5))
        cross2 = Cross(Coord(5,6))
        self.assertTrue(cross1.intersect(cross2))
    def test_not_cross_line(self):
        cross = Cross(Coord(5,5))
        line = Line(Point(1,1),Point(1,9))
        self.assertFalse(cross.intersect(line))
    def test_not_line_cross(self):
        cross = Cross(Coord(5,5))
        line = Line(Point(1,1),Point(1,9))
        self.assertFalse(line.intersect(cross))
    def test_not_cross_cross(self):
        cross1 = Cross(Coord(5,5))
        cross2 = Cross(Coord(7,7))
        self.assertFalse(cross1.intersect(cross2))

class LineLikeCollection(object):
    def __init__(self, line_list):
        self.line_list = line_list
    def crossing(self):
        '''return the two crossing line-like items, or None,None'''
        for i in range(len(self.line_list)):
            for j in range(i,len(self.line_list)):
                a = self.line_list[i]
                b = self.line_list[j]
                if a.intersect(b):
                    # found an intersecting pair!
                    del self.line_list[j]
                    del self.line_list[i]
                    return (a,b)
        return (None,None)
    def count(self):
        return len(self.line_list)

class TestLineLikeCollection(unittest.TestCase):
    def line(self, x1,y1,x2,y2):
        return Line(Point(x1,y1),Point(x2,y2))
    def test_crossing_yes(self):
        l1 = self.line(1,1,1,5)
        l2 = self.line(2,5,9,5)
        l3 = self.line(2,2,8,8)
        llc = LineLikeCollection([l1, l2, l3])
        self.assertEqual(3, llc.count())
        a, b = llc.crossing()
        self.assertEqual(a, l2)
        self.assertEqual(b, l3)
        self.assertEqual(1, llc.count())
    def test_crossing_no(self):
        l1 = self.line(1,1,1,5)
        l2 = self.line(2,5,9,5)
        l3 = self.line(9,4,3,1)
        llc = LineLikeCollection([l1, l2, l3])
        self.assertEqual(3, llc.count())
        a, b = llc.crossing()
        self.assertEqual(a, None)
        self.assertEqual(b, None)
        self.assertEqual(3, llc.count())
