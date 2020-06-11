import unittest
import heapq

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
