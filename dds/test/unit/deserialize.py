#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import sys
sys.path.append('IceDDS')
sys.path.append('test')

import unittest, Ice

import EventFilters as Evt
import filtersUtils as FT

SLICE_LS     = '/usr/share/mlp-slice/slice'
Ice.loadSlice('slices/DDS.ice slices/Listener.ice \
--all -I{0} -I{1}'.format(SLICE_LS, Ice.getSliceDir()))



import DDS, MLP

import struct

class TestDeserialize(unittest.TestCase):
    def setUp(self):
        self.point_typecode = (DDS.VariableTypeCode('x','double'),
                               DDS.VariableTypeCode('y','double'),
                               DDS.VariableTypeCode('z','double'))


    def test_point(self):
        filter_ = [Evt.EventFilterRange("x", 3, 8)]
        dissector = FT.DataDissector(filter_, self.point_typecode)

        data = MLP.Coord(4.0, 6.0, 0.0)

        st = struct.pack('ddd', data.x, data.y, data.z)

        self.assertTrue(dissector.dissector_match_with_filter_classes(st))

    def test_point_out(self):
        filter1 = Evt.EventFilterOver("x", 3)
        filter2 = Evt.EventFilterBelow("y", 8)

        dissector1 = FT.DataDissector([filter1], self.point_typecode)
        dissector2 = FT.DataDissector([filter2], self.point_typecode)
        dissector3 = FT.DataDissector([filter1,filter2], self.point_typecode)

        data = MLP.Coord(2.0, 9.0, 0.0)
        data2 = MLP.Coord(2.0, 9.0, 0.0)

        st = struct.pack('ddd', data.x, data.y, data.z)
        st2 = struct.pack('ddd', data2.x, data2.y, data2.z)

        self.assertTrue(not(dissector1.dissector_match_with_filter_classes(st)))
        self.assertTrue(not(dissector2.dissector_match_with_filter_classes(st)))
        self.assertTrue(not(
                dissector3.dissector_match_with_filter_classes(st2)))


    def test_missing_field(self):
        filter1 = Evt.EventFilterRange('p', 3, 8)
        filter2 = Evt.EventFilterRange('x', 3, 8)

        dissector1 = FT.DataDissector([filter1], self.point_typecode)
        dissector2 = FT.DataDissector([filter2], self.point_typecode)
        dissector3 = FT.DataDissector([filter1, filter2], self.point_typecode)

        self.assertTrue(not(dissector1.checkedFields_with_filter_classes()))
        self.assertTrue(dissector2.checkedFields_with_filter_classes())
        self.assertTrue(not(dissector3.checkedFields_with_filter_classes()))

    def test_data_unexpected(self):
        filter_ = Evt.EventFilterRange('x', 3, 8)
        filter2 = Evt.EventFilterRange('y', 3, 8)

        point_typecode = [DDS.VariableTypeCode('x','double')]
        dissector = FT.DataDissector([filter_], point_typecode)

        data = MLP.Coord(4.0, 6.0, 0.0)
        st = struct.pack('ddd', data.x, data.y, data.z)

        self.assertRaises(ValueError,
                          dissector.dissector_match_with_filter_classes, st)
