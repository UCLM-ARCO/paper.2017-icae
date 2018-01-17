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

Ice.loadSlice('slices/DDS.ice slices/Listener.ice \
--all -I{0} -I{1}'.format(SLICE_LS, Ice.getSliceDir()))

import DDS, MLP, Event

class TestTopicFilter(unittest.TestCase):

    def setUp(self):
        argv = ["--Ice.Config=test/unit/topics.config"]
        self.ic = Ice.initialize(argv)

        self.point_typecode = [DDS.VariableTypeCode('x', 'double'),
                               DDS.VariableTypeCode('y', 'double'),
                               DDS.VariableTypeCode('z', 'double')]

        self.filter1 = "x in range(1,5)"

        self.data1 = MLP.Coord(1.0, 12.0, 0.0)
        self.data2 = MLP.Coord(4.0, 23.0, 0.0)
        self.invalidData = MLP.Coord(6.0, 32.0, 0.0)

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

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends several events
        publisher.sendData(self.data1)
        publisher.sendData(self.data2)
        subscriber.servant.wait(2)

        # then the subscriber receives the events
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (4.0, 23.0)))

        self.assertEqual(len(subscriber.servant.get_registered_calls()), 2)

    def test_filteredInTopicTwoSubscribers(self):
        # given a filtered topic, a publisher, two subscribers
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.filter1])

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber1 = mocks.Subscriber(self.adapter, 'sub1')
        topic.subscribeAndGetPublisher(subscriber1.proxy)
        subscriber2 = mocks.Subscriber(self.adapter, 'sub2')
        topic.subscribeAndGetPublisher(subscriber2.proxy)

        # when the publisher sends several events
        publisher.sendData(self.data1)
        publisher.sendData(self.data2)
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

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends a invalid event
        publisher.sendData(self.invalidData)
        subscriber.servant.wait(2)

        # the suscriber doesn't receive event
        self.assert_(not(subscriber.servant.method_was_called('send_data',
                                                              (6.0, 32.0))))

        self.assertEqual(len(subscriber.servant.get_registered_calls()), 0)

    def test_subscriberAndPublisher(self):
        # given a filteredTopic with several filters, a subscriber and a
        # general publisher
        # filter2 = self.filter1 + " and y > 10"
        filter2 = "y > 10"

        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.filter1, filter2])

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends several events

        publisher.sendData(self.data1)
        # subscriber.servant.wait(2)
        publisher.sendData(self.data2)
        subscriber.servant.wait(2)

        # then the subscriptor receives the events
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (4.0, 23.0)))
