import sys, time
sys.path.append('IceDDS')
sys.path.append('test/unit/')

import unittest, Ice, IceDDS, IceStorm
import EventFilters as Evt
from mock import Mock
import mocks
SLICE_LS     = '/usr/share/mlp-slice/slice'

Ice.loadSlice('slices/DDS.ice --all -I {0} -I{1}'.format(SLICE_LS,
                                                      Ice.getSliceDir()))

import DDS

class TestFiltersExceptions(unittest.TestCase):

    def setUp(self):
        argv = ["--Ice.Config=test/unit/topics.config"]
        self.ic = Ice.initialize(argv)


        self.point_typecode = [DDS.VariableTypeCode('x','double'),
                               DDS.VariableTypeCode('y','double'),
                               DDS.VariableTypeCode('z','double')]

        self.filter1 = ["x in range(1,5)"]

        self.adapter = self.ic.createObjectAdapter("OA")
        self.adapter.activate()

        self.topicManager = IceDDS.TopicManager(self.adapter)

    def tearDown(self):
        for topic in self.topicManager.retrieveAll().values():
            topic.destroy()

        self.ic.destroy()

    def test_incorrectFilterExpressionInCreateTopic(self):
        # The expression of filter is incorrect when a filtered topic is
        # created

        filter_ = ["== s 1"]

        self.assertRaises(DDS.FilterError,
                          self.topicManager.createFilteredTopic,
                          "foo", self.point_typecode, filter_)

    def test_incorrectFilterExpressionInPublisher(self):
        # The expression of filter is incorrect when the filtered publisher is
        # created

        filter_ = ["== y 1"]
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        self.assertRaises(DDS.FilterError, topic.getFilteredPublisher,
                          "fooPub", filter_)


    def test_incorrectFilterExpressionInSubscribe(self):
        # The expresion of filter is incorrect in the subscription of a object

        filter_ = ["1 2 >"]
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        subscriber = mocks.Subscriber(self.adapter)
        self.assertRaises(DDS.FilterError,
                         topic.subscribeWithFilters,
                         subscriber.proxy, filter_)
