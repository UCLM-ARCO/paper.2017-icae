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

class TestTopicsLinks(unittest.TestCase):

    def setUp(self):
        argv = ["--Ice.Config=test/unit/topics.config"]
        self.ic = Ice.initialize(argv)


        self.point_typecode = (DDS.VariableTypeCode('x','double'),
                               DDS.VariableTypeCode('y','double'),
                               DDS.VariableTypeCode('z','double'))

        self.filter1 = ["x in range(1,5)"]

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



    def test_linksDataReceived(self):
        # given two filtered topics, a publisher of topic 1 and a subscriber of
        # topic 2
        filter2 = ["x == 2"]

        topic1 = self.topicManager.createFilteredTopic("foo",
                                                       self.point_typecode,
                                                       self.filter1)

        topic2 = self.topicManager.createFilteredTopic("foo2",
                                                       self.point_typecode,
                                                       filter2)
        # when:

        # --- canal 1 links with canal 2 with filter "x == 2"
        publisher = Event.ListenerPrx.uncheckedCast(topic1.getPublisher())
        publisher2 = Event.ListenerPrx.uncheckedCast(topic2.getPublisher())

        topic1.linkFiltered(publisher2)

        # --- the topic 2 subscribes to subcriber
        subscriber = self.subscribe_to_topic(topic2)

        # --- the publisher sends a event
        data1 = MLP.Coord(2.0, 3.0, 0.0)
        publisher.sendData(data1)
        subscriber.servant.wait(2)

        # the subscriber of topic 2 receives the event
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                           (2.0, 3.0)))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)

    def test_linksDataReceivedWithFilterInPublisher(self):
        # given a filtered topic and a general topic,
        # a general publisher of topic 1,
        # and two subscribers

        filter2 = ["x in range(2,4)"]

        topic1 = self.topicManager.createFilteredTopic("foo",
                                                       self.point_typecode,
                                                       self.filter1)

        topic2 = self.topicManager.createTopic("foo2", self.point_typecode)


        publisher = Event.ListenerPrx.uncheckedCast(topic1.getPublisher())

        subscriber = mocks.Subscriber(self.adapter, 'sub1')
        topic1.subscribeAndGetPublisher(subscriber.proxy)
        subscriber2 = mocks.Subscriber(self.adapter, 'sub2')
        topic2.subscribeAndGetPublisher(subscriber2.proxy)

        # when topic 1 links with topic 2 with range (2,4) and the publisher of
        # topic 1 send events
        prx = topic2.getFilteredPublisher("pubFilterRange", filter2)

        publisher2 = Event.ListenerPrx.uncheckedCast(prx)
        topic1.linkFiltered(publisher2)

        data1 = MLP.Coord(1.0, 15.0, 0.0)
        data2 = MLP.Coord(2.0, 3.0, 0.0)
        publisher.sendData(data1)
        publisher.sendData(data2)
        subscriber.servant.wait(2)
        subscriber2.servant.wait(2)

        # the subscriber 1 receives the event 1, and the subscriber 2
        # receives all the events
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                           (1.0, 15.0)))
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                           (2.0, 3.0)))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 2)
        self.assert_(subscriber2.servant.method_was_called('send_data',
                                                          (2.0, 3.0)))
        self.assertEqual(len(subscriber2.servant.get_registered_calls()), 1)


    def test_linksWithDifferentSubscribers(self):
        # given a general topics, a general publisher of topic 1,
        # a subscriber with filter and other subscriber without filter of topic
        # 2

        filter1 = ["x in range(2,4)"]
        filter2 = ["x > 2"]

        topic1 = self.topicManager.createTopic("foo")

        topic2 = self.topicManager.createTopic("foo2", self.point_typecode)


        publisher = Event.ListenerPrx.uncheckedCast(topic1.getPublisher())

        subscriber = mocks.Subscriber(self.adapter, 'sub1')
        topic2.subscribeAndGetPublisher(subscriber.proxy)
        subscriber2 = mocks.Subscriber(self.adapter, 'sub2')
        topic2.subscribeWithFilters(subscriber2.proxy, filter2)

        # when topic 1 links with topic 2 with range (2,4) and the publisher of
        # topic 1 send events
        prx = topic2.getFilteredPublisher("pubFilterRange", filter1)

        publisher2 = Event.ListenerPrx.uncheckedCast(prx)
        topic1.linkFiltered(publisher2)

        data1 = MLP.Coord(2.0, 15.0, 0.0)
        data2 = MLP.Coord(3.0, 3.0, 0.0)
        publisher.sendData(data1)
        publisher.sendData(data2)
        subscriber.servant.wait(2)
        subscriber2.servant.wait(2)

        # the subscriber2 receives the event 2, and the subscriber 1
        # receives all the events
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                           (2.0, 15.0)))
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                           (3.0, 3.0)))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 2)
        self.assert_(subscriber2.servant.method_was_called('send_data',
                                                          (3.0, 3.0)))
        self.assertEqual(len(subscriber2.servant.get_registered_calls()), 1)


    def test_linksNotDataReceived(self):
        # given two topics, a publisher of topic 1, a subscriber of topic 1 and
        # a subscriber of topic 2
        filter1 = ["x == 8"]

        topic1 = self.topicManager.createTopic("foo")
        topic2 = self.topicManager.createTopic("foo2", self.point_typecode)

        publisher = Event.ListenerPrx.uncheckedCast(topic1.getPublisher())

        subscriber = mocks.Subscriber(self.adapter, 'sub1')
        topic1.subscribeAndGetPublisher(subscriber.proxy)
        subscriber2 = mocks.Subscriber(self.adapter, 'sub2')
        topic2.subscribeAndGetPublisher(subscriber2.proxy)

        # when the publisher1 sends a event
        prx = topic2.getFilteredPublisher("pubFilter", filter1)

        publisher2 = Event.ListenerPrx.uncheckedCast(prx)
        topic1.linkFiltered(publisher2)

        data1 = MLP.Coord(4.0, 5.0, 0.0)
        publisher.sendData(data1)
        subscriber.servant.wait(2)


        # the subscriber 1 receives the event and the subscriber 2 doesn't
        # receive the event, because the topic has other filter
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (4.0, 5.0)))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)
        self.assert_(not(subscriber2.servant.method_was_called('send_data',
                                                               (4.0, 5.0))))
        self.assertEqual(len(subscriber2.servant.get_registered_calls()), 0)

    def test_unlinkFiltered(self):
        # given two filtered topics, a publisher of topic 1 and a subscriber of
        # topic 2
        filter2 = ["x == 2"]

        topic1 = self.topicManager.createFilteredTopic("foo",
                                                       self.point_typecode,
                                                       self.filter1)
        topic2 = self.topicManager.createFilteredTopic("foo2",
                                                       self.point_typecode,
                                                       filter2)

        # when:

        # --- canal 1 links with canal 2 with filter "x == 2"
        publisher = Event.ListenerPrx.uncheckedCast(topic1.getPublisher())
        publisher2 = Event.ListenerPrx.uncheckedCast(topic2.getPublisher())

        topic1.linkFiltered(publisher2)

        # --- the topic 2 subscribes to subcriber
        subscriber = self.subscribe_to_topic(topic2)

        # --- the publisher sends a event
        data1 = MLP.Coord(2.0, 3.0, 0.0)
        publisher.sendData(data1)
        subscriber.servant.wait(2)

        # the subscriber of topic 2 receives the event
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                           (2.0, 3.0)))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)

        # when the topic 2 make unlink with topic 1 and the publisher sends a
        # event
        topic1.unlinkFiltered(publisher2)
        data2 = MLP.Coord(2.0, 10.0, 0.0)
        publisher.sendData(data2)

        # then the subscriber of topic 2 doesn't receive the event
        self.assert_(not(subscriber.servant.method_was_called('send_data',
                                                           (2.0, 10.0))))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)
