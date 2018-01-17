import sys, time
sys.path.append('IceDDS')
sys.path.append('test')

import unittest
import EventFilters as Evt

class TestMatchFilter(unittest.TestCase):
    def test_value(self):
        sut = Evt.EventFilter('x', 1)
        self.assert_(sut.match(1))
        self.assertFalse(sut.match(2))

    def test_range(self):
        sut = Evt.EventFilterRange('x', 1, 6)

        self.assert_(sut.match(1.5))
        self.assertFalse(sut.match(0.0))
        self.assertFalse(sut.match(7.5))
        self.assert_(sut.match(2, 4))
        self.assertFalse(sut.match(5, 4))
        self.assertFalse(sut.match(0, 4))
        self.assertFalse(sut.match(2, 7))

    def test_valuesBelow(self):
        sut = Evt.EventFilterBelow('x', 3)

        self.assert_(sut.match(2.4))
        self.assertFalse(sut.match(4.3))


    def test_valuesOver(self):
        sut = Evt.EventFilterOver('x', 3)

        self.assert_(sut.match(4.7))
        self.assertFalse(sut.match(0.8))
