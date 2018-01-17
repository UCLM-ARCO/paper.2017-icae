import sys, time
sys.path.append('IceDDS')
sys.path.append('test')

import unittest
import EventFilters as Evt
import filtersUtils as FT

class TestFilterExpression(unittest.TestCase):

    def test_getEventFilter(self):
        filter1 = "x == 2"
        filter2 = "x == 4"

        sut = Evt.EventFilter('x', 2)
        sut2 = Evt.EventFilter('x', 4)

        filterTopic1 = FT.getFilter([filter1])
        filterTopic2 = FT.getFilter([filter1, filter2])

        self.assertEqual(sut.field_name, filterTopic1[0].field_name)
        self.assertEqual(sut.num, filterTopic1[0].num)
        self.assertEqual(type(sut), type(filterTopic1[0]))

        self.assertEqual(sut.field_name, filterTopic2[0].field_name)
        self.assertEqual(sut.num, filterTopic2[0].num)
        self.assertEqual(type(sut), type(filterTopic2[0]))
        self.assertEqual(sut2.field_name, filterTopic2[1].field_name)
        self.assertEqual(sut2.num, filterTopic2[1].num)
        self.assertEqual(type(sut), type(filterTopic2[1]))


    def test_getEventFilterBelow(self):
        filter_ = ["x < 2"]

        sut = Evt.EventFilterBelow('x', 2)

        filterTopic = FT.getFilter(filter_)

        self.assertEqual(sut.field_name, filterTopic[0].field_name)
        self.assertEqual(sut.num, filterTopic[0].num)
        self.assertEqual(type(sut), type(filterTopic[0]))

    def test_getEventFilterOver(self):
        filter_ = ["x > 2"]

        sut = Evt.EventFilterOver('x', 2)

        filterTopic = FT.getFilter(filter_)

        self.assertEqual(sut.field_name, filterTopic[0].field_name)
        self.assertEqual(sut.num, filterTopic[0].num)
        self.assertEqual(type(sut), type(filterTopic[0]))

    def test_getEventFilterRange(self):
        filter_ = ["y in range(22,465)"]

        sut = Evt.EventFilterRange("y", 22, 465)

        filterTopic = FT.getFilter(filter_)

        self.assertEqual(sut.field_name, filterTopic[0].field_name)
        self.assertEqual(sut.valueLow, filterTopic[0].valueLow)
        self.assertEqual(sut.valueHigh, filterTopic[0].valueHigh)
        self.assertEqual(type(sut), type(filterTopic[0]))

    def test_getRangeAndOver(self):
        filter1 = "y in range(2,4)"
        filter2 = "y > 8"

        sut = Evt.EventFilterRange("y", 2, 4)
        sut2 = Evt.EventFilterOver("y", 8)

        filterTopic = FT.getFilter([filter1, filter2])

        self.assertEqual(sut.field_name, filterTopic[0].field_name)
        self.assertEqual(sut.valueLow, filterTopic[0].valueLow)
        self.assertEqual(sut.valueHigh, filterTopic[0].valueHigh)
        self.assertEqual(type(sut), type(filterTopic[0]))

        self.assertEqual(sut2.field_name, filterTopic[1].field_name)
        self.assertEqual(sut2.num, filterTopic[1].num)
        self.assertEqual(type(sut2), type(filterTopic[1]))
