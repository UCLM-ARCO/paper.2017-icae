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


    def test_changefilters(self):
        # given a topic, a publisher and a subcriptor with filters
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber = mocks.Subscriber(self.adapter)
        topicofSubscriber = topic.subscribeWithFilters(subscriber.proxy,
                                                       [self.filter1])

        # when the publisher sends several events
        publisher.sendData(self.data1)
        time.sleep(1)
        publisher.sendData(self.data2)
        time.sleep(1)

        # then the subscriber receives the events
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (4.0, 23.0)))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 2)

        # when the subscriber changes the filter and publisher sends a event
        filter2 = "x > 5"
        topicofSubscriber.setFilters([filter2])

        data = MLP.Coord(8.0, 2.0, 0.0)
        publisher.sendData(data)
        time.sleep(1)

        # the subscriber receives the new event
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 3)


    def test_changefiltersAndNotReceive(self):
        # given a filtered topic, a publisher and a subcriptor
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber = mocks.Subscriber(self.adapter)
        topicofSubscriber = topic.subscribeWithFilters(subscriber.proxy,
                                                       [self.filter1])

        # when the publisher sends several events
        publisher.sendData(self.data1)
        time.sleep(1)
        publisher.sendData(self.data2)
        time.sleep(1)

        # then the subscriber receives the events
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (4.0, 23.0)))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 2)

        # when the subscriber changes the filter and publisher sends a event
        filter2 = "x > 8"
        topicofSubscriber.setFilters([filter2])


        data = MLP.Coord(3.0, 2.0, 0.0)
        publisher.sendData(data)
        time.sleep(1)

        # then the subscriber doesn't receive the new event
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 2)
