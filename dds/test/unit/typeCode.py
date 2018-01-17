import sys, time
sys.path.append('IceDDS')
sys.path.append('test')

import unittest, Ice, IceDDS, IceStorm
import EventFilters as Evt
import filtersUtils as FT
import mocks
SLICE_LS     = '/usr/share/mlp-slice/slice'

Ice.loadSlice('slices/DDS.ice --all -I {0} -I{1}'.format(SLICE_LS,
                                                      Ice.getSliceDir()))

import DDS

class TestTypeCode(unittest.TestCase):

    def setUp(self):
        argv = ["--Ice.Config=test/unit/topics.config"]
        self.ic = Ice.initialize(argv)


        self.point_typecode = [DDS.VariableTypeCode('x','double'),
                               DDS.VariableTypeCode('y','double'),
                               DDS.VariableTypeCode('z','double')]

        self.filter1 = "attributes:x in range(1,5)"

        self.adapter = self.ic.createObjectAdapter("OA")
        self.adapter.activate()

        self.topicManager = IceDDS.TopicManager(self.adapter)

    def tearDown(self):
        for topic in self.topicManager.retrieveAll().values():
            topic.destroy()

        self.ic.destroy()

    # def test_incorrectFilterTypeCodeCreateTopic(self):
    #     # The name of variable in typecode is incorrect
    #     typecode = [DDS.VariableTypeCode('2','int'),
    #                 DDS.VariableTypeCode('y','int')]

    #     self.assertRaises(DDS.FilterError,
    #                       self.topicManager.createFilteredTopic,
    #                       "foo", typecode, [self.filter1])

    #     # The type of variable in typecode is incorrect
    #     typecode = [DDS.VariableTypeCode('x','int'),
    #                 DDS.VariableTypeCode('y','3')]

    #     self.assertRaises(DDS.FilterError,
    #                       self.topicManager.createFilteredTopic,
    #                       "foo", typecode, [self.filter1])

    # def test_filterVariableNotMatchWithTypeCode(self):
    #     # The specific fields in typecode don't match with the field of filter
    #     # in topic
    #     typecode = [DDS.VariableTypeCode('x','int'),
    #                 DDS.VariableTypeCode('x','int')]

    #     filter_ = "attributes:y in range(1,5)"
    #     self.assertRaises(DDS.FilterError,
    #                       self.topicManager.createFilteredTopic,
    #                       "foo", typecode, [filter_])

    #     self.assertRaises(DDS.FilterError,
    #                       self.topicManager.createFilteredTopic,
    #                       "foo", typecode, [self.filter1, filter_])


    # def test_notPossibleExpressionFilterInPublisher(self):
    #     # The specific variable in filter doesn't match with the typecode
    #     # in publisher
    #     topic = self.topicManager.createTopic("foo", self.point_typecode)

    #     filter_ = ["attributes:p in range(1,5)"]

    #     self.assertRaises(DDS.FilterError, topic.getFilteredPublisher,
    #                       'Filter_', filter_)

    # def test_notPossibleExpressionFilterInSubscriber(self):
    #     # The specific variable in filter doesn't match with the typecode
    #     # in publisher
    #     topic = self.topicManager.createTopic("foo", self.point_typecode)

    #     filter_ = ["attributes:p in range(1,5)"]

    #     subscriber = mocks.Subscriber(self.adapter)

    #     self.assertRaises(DDS.FilterError, topic.subscribeWithFilters,
    #                       subscriber.proxy, filter_)

    def test_typeCodata(self):
        typecode = [DDS.VariableTypeCode("voltage", "sequence 4" \
                                             +" {double,double,double}")]

        datadisec = FT.DataDissector("", typecode)

        print datadisec.fmt
