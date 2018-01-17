#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import sys, time
sys.path.append('IceDDS')
sys.path.append('test')


import unittest, Ice, IceStorm
import IceDDS, IceDoubles, EventFilters as Evt
from mock import Mock
import mocks

SLICE_LS     = '/usr/share/mlp-slice/slice'
SLICE_ENERGOS = '../prj.energos-middleware/examples/icedds-java/slice'

Ice.loadSlice('slices/DDS.ice  {0}/Energos.ice \
--all -I{1} -I{2}'.format(SLICE_ENERGOS, SLICE_LS, Ice.getSliceDir()))

import DDS, Energos

class TestTopicFilter(unittest.TestCase):

    def setUp(self):
        argv = ["--Ice.Config=test/unit/topics.config"]
        self.ic = Ice.initialize(argv)

        self.point_typecode = [DDS.VariableTypeCode('source', 'string'),
                               DDS.VariableTypeCode('resourceId', 'string'),
                               DDS.VariableTypeCode('timeStamp', 'long'),
                               DDS.VariableTypeCode('eventType', 'int'),
                               DDS.VariableTypeCode('svStatus', 'int'),
                               DDS.VariableTypeCode('eventValueQuality', 'string')]


        self.filter1 = "resourceId == 'HUJE345'"

        self.data1 = Energos.ControlMsg("101", "HUJE345", long(time.time()), 8, 12, "GOOD")
        self.data2 = Energos.ControlMsg("102", "BACD145", long(time.time()), 5, 3, "GOOD")

        self.adapter = self.ic.createObjectAdapter("OA")
        self.adapter.activate()

        self.topicManager = IceDDS.TopicManager(self.adapter)

    def tearDown(self):
        for topic in self.topicManager.retrieveAll().values():
            topic.destroy()

        self.ic.destroy()

    def subscribe_to_topic(self, tp):
        subscriber = mocks.Subscriber(self.adapter)
        tp.subscribeAndGetPublisher(subscriber.proxy)
        return subscriber

    ### !!! Tests when the filter is in the topic !!! ####

    def test_filteredInTopicOneSubscriber(self):
        # given a filtered topic, a publisher and a subscriptor

        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.filter1])

        publisher = Energos.ControlSinkPrx.uncheckedCast(topic.getPublisher())

        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends several events
        publisher.status(self.data1)
        publisher.status(self.data2)
        subscriber.servant.wait(2)

        # then the subscriber receives the events
        self.assert_(subscriber.servant.method_was_called('status',
                                                          ("101", 12)))

        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)

    def test_filteredInTopicTwoSubscribers(self):
        # given a filtered topic, a publisher, two subscribers
        filter1 = "eventType in range(3,20)"

        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [filter1])

        publisher = Energos.ControlSinkPrx.uncheckedCast(topic.getPublisher())

        subscriber1 = mocks.Subscriber(self.adapter, 'sub1')
        topic.subscribeAndGetPublisher(subscriber1.proxy)
        subscriber2 = mocks.Subscriber(self.adapter, 'sub2')
        topic.subscribeAndGetPublisher(subscriber2.proxy)

        # when the publisher sends several events
        publisher.status(self.data1)
        publisher.status(self.data2)
        subscriber1.servant.wait(2)
        subscriber2.servant.wait(2)

        # then the subscriptors receive the events
        self.assertEqual(len(subscriber1.servant.get_registered_calls()), 2)
        self.assertEqual(len(subscriber2.servant.get_registered_calls()), 2)

    def test_sendInvalidDataInFilteredTopic(self):
        # given a filtered topic, a publisher and a subscriptor
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.filter1])

        publisher = Energos.ControlSinkPrx.uncheckedCast(topic.getPublisher())

        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends a invalid event
        publisher.status(self.data2)
        subscriber.servant.wait(2)

        # the suscriber doesn't receive event

        self.assertEqual(len(subscriber.servant.get_registered_calls()), 0)

    def test_subscriberAndPublisher(self):
        # given a filteredTopic with several filters, a subscriber and a
        # general publisher
        filter2 = "eventType > 2"

        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.filter1,
                                                       filter2])

        publisher = Energos.ControlSinkPrx.uncheckedCast(topic.getPublisher())

        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends several events

        publisher.status(self.data1)
        publisher.status(self.data2)
        subscriber.servant.wait(2)

        # then the subscriptor receives the events
        self.assert_(subscriber.servant.method_was_called('status',
                                                          ("101", 12)))
