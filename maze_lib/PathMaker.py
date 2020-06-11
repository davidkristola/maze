import unittest
import random
from LineStuff import *

class PathMaker(object):
    def __init__(self, span_x, span_y, inner_point_count):
        self.span_x = span_x
        self.span_y = span_y
        self.inner_point_count = inner_point_count
        self.elligable_points = self._all_inner_points()
        random.shuffle(self.elligable_points)
    def _all_inner_points(self):
        inner_points = []
        for x in range(self.span_x-2):
            for y in range(self.span_y-2):
                inner_points.append(Point(x+1,y+1))
        return inner_points
    def _first_point(self):
        return Point(0,0)
    def _last_point(self):
        return Point(self.span_x-1, self.span_y-1)
    def _random_point(self):
        # return a random point that is not on the extreme
        #x = random.randint(1, self.span_x-2)
        #y = random.randint(1, self.span_y-2)
        #return Point(x,y)
        if len(self.elligable_points) == 0:
            return None
        p = self.elligable_points[0]
        del(self.elligable_points[0])
        return p
    def _make_random_point_list(self):
        point_list = [self._first_point()]
        self.inner_points = []
        for p in range(self.inner_point_count):
            point = self._random_point()
            point_list += [point]
            self.inner_points += [point]
        point_list += [self._last_point()]
        self.point_list = point_list
        return point_list
    def _point_list_to_line_list(self, point_list=None):
        if point_list is None:
            point_list = self.point_list
        ll = []
        for i in range(len(point_list)-1):
            ll.append(Line(point_list[i], point_list[i+1]))
        self.line_list = ll
        return ll
    def cross(self, line_1, line_2):
        try:
            return line_1.intersect(line_2)
        except:
            return line_2.intersect(line_1)
    def has_cross(self, ll=None):
        if ll is None:
            ll = self.line_list
        for l1 in ll:
            for l2 in ll:
                if (not l1 == l2) and self.cross(l1, l2):
                    #print('l1 %s crosses l2 %s' % (str(l1), str(l2)))
                    return True
        return False
    def crosses(self, line_list, candidate):
        for line in line_list:
            if self.cross(line, candidate):
                return True
        return False
    def get_line_list(self):
        return self._point_list_to_line_list(self._make_random_point_list())

class TestPathMaker(unittest.TestCase):
    def setUp(self):
        self.path_maker = PathMaker(10, 20, 4)
    def test_all_inner_points_1(self):
        pm = PathMaker(3, 3, 1)
        ip = pm._all_inner_points()
        self.assertEqual([Point(1,1)], ip)
    def test_all_inner_points_2(self):
        pm = PathMaker(3, 4, 1)
        ip = pm._all_inner_points()
        self.assertEqual([Point(1,1),Point(1,2)], ip)
    def test_all_inner_points_3(self):
        pm = PathMaker(4, 3, 1)
        ip = pm._all_inner_points()
        self.assertEqual([Point(1,1),Point(2,1)], ip)
    def test_all_inner_points_4(self):
        pm = PathMaker(4, 4, 1)
        ip = pm._all_inner_points()
        self.assertEqual([Point(1,1),Point(1,2),Point(2,1),Point(2,2)], ip)
    def test_random_point(self):
        pm = PathMaker(3, 3, 1)
        # in a 3x3, there is only one elligable point
        ip = pm._random_point()
        self.assertEqual(Point(1,1), ip)
        ip = pm._random_point()
        self.assertEqual(None, ip)
    def test_make_random_point_list(self):
        path = self.path_maker._make_random_point_list()
        self.assertEqual(len(path), 6)
    def test_cross_1(self):
        l_1 = Line(Point(1,1), Point(9,9))
        l_2 = Line(Point(1,9), Point(9,1))
        self.assertTrue(self.path_maker.cross(l_1, l_2))
    def test_cross_2(self):
        l_1 = Line(Point(1,1), Point(2,2))
        l_2 = Line(Point(3,3), Point(4,4))
        self.assertFalse(self.path_maker.cross(l_1, l_2))
    def test_point_list_to_line_list(self):
        point_list = [Point(1,1), Point(2,2), Point(3,3), Point(4,4)]
        ll = self.path_maker._point_list_to_line_list(point_list)
        self.assertEqual(len(ll), 3)
        self.assertEqual(Line(Point(1,1), Point(2,2)), ll[0])
        self.assertEqual(Line(Point(2,2), Point(3,3)), ll[1])
        self.assertEqual(Line(Point(3,3), Point(4,4)), ll[2])
    def test_get_line_list(self):
        path = self.path_maker.get_line_list()
        self.assertEqual(5, len(path))

