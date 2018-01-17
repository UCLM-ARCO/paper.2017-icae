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

class TestSubscribersWithFilters(unittest.TestCase):
    def setUp(self):
        argv = ["--Ice.Config=test/unit/topics.config"]
        self.ic = Ice.initialize(argv)


        self.point_typecode = [DDS.VariableTypeCode('x', 'double'),
                               DDS.VariableTypeCode('y', 'double'),
                               DDS.VariableTypeCode('z', 'double')]

        self.filter1 = "x in range(1,5)"

        self.data1 = MLP.Coord(1.0, 12.0, 0.0)
        self.data2 = MLP.Coord(4.0, 23.0, 0.0)
        self.invalidData = MLP.Coord(6.0, 2.0, 0.0)

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

    def test_topicGeneralAndPublisherGeneral(self):

        # given a general topic, a general publisher and a filtered subscriber
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber1 = mocks.Subscriber(self.adapter)

        topic.subscribeWithFilters(subscriber1.proxy, [self.filter1])

        # when the publisher sends several events
        data3 = MLP.Coord(7.0, 2.0, 0.0)
        publisher.sendData(self.data1)
        subscriber1.servant.wait(2)
        publisher.sendData(self.data2)
        subscriber1.servant.wait(2)
        publisher.sendData(data3)
        subscriber1.servant.wait(2)

        # the subscriber receives the events matched with its filters
        self.assert_(subscriber1.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))
        self.assert_(subscriber1.servant.method_was_called('send_data',
                                                          (4.0, 23.0)))
        self.assertEqual(len(subscriber1.servant.get_registered_calls()), 2)

    def test_topicGeneralAndPublisherGeneralWithSeveralSubscribers(self):

        # given a general topic, a general publisher, a general suscriber and a
        # filtered subscriber
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber1 = mocks.Subscriber(self.adapter)
        subscriber2 = mocks.Subscriber(self.adapter)

        topic.subscribeWithFilters(subscriber1.proxy, [self.filter1])


        topic.subscribeAndGetPublisher(subscriber2.proxy)

        # when the publisher sends several events
        data3 = MLP.Coord(7.0, 2.0, 0.0)
        publisher.sendData(self.data1)
        publisher.sendData(self.data2)
        publisher.sendData(data3)
        subscriber1.servant.wait(2)
        subscriber2.servant.wait(2)

        # the filtered subscripber receives the events matched with its filters
        # and the general subscriptor receives all the events
        self.assert_(subscriber1.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))
        self.assert_(subscriber1.servant.method_was_called('send_data',
                                                          (4.0, 23.0)))
        self.assertEqual(len(subscriber1.servant.get_registered_calls()), 2)
        self.assert_(subscriber2.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))
        self.assert_(subscriber2.servant.method_was_called('send_data',
                                                          (4.0, 23.0)))
        self.assert_(subscriber2.servant.method_was_called('send_data',
                                                          (7.0, 2.0)))
        self.assertEqual(len(subscriber2.servant.get_registered_calls()), 3)

    def test_filteredTopicAndPublisherGeneral(self):

        # given a general filtered Topic, a general publisher and a filtered
        # subscriber
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.filter1])
        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber1 = mocks.Subscriber(self.adapter)

        filter_ = ["x > 2"]
        topic.subscribeWithFilters(subscriber1.proxy, filter_)

        # when the publisher sends several events
        data3 = MLP.Coord(3.0, 2.0, 0.0)
        data4 = MLP.Coord(8.0, 2.0, 0.0)
        publisher.sendData(self.data1)
        subscriber1.servant.wait(2)
        publisher.sendData(self.data2)
        # subscriber1.servant.wait(2)
        publisher.sendData(data3)
        # subscriber1.servant.wait(2)
        publisher.sendData(data4)
        subscriber1.servant.wait(2)

        # the subscriber receives the events matched with its filters and the
        # events are correct in the topic
        self.assert_(subscriber1.servant.method_was_called('send_data',
                                                          (3.0, 2.0)))
        self.assert_(subscriber1.servant.method_was_called('send_data',
                                                          (4.0, 23.0)))
        self.assert_(not(subscriber1.servant.method_was_called('send_data',
                                                          (1.0, 12.0))))
        self.assert_(not(subscriber1.servant.method_was_called('send_data',
                                                          (8.0, 2.0))))
        self.assertEqual(len(subscriber1.servant.get_registered_calls()), 2)

    def test_filteredTopicAndPublisherGeneralWithSeveralSubscribers(self):
        # given a general filtered Topic, a general publisher, a general
        # subscriber and a filtered subscriber
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.filter1])

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber1 = mocks.Subscriber(self.adapter)
        subscriber2 = mocks.Subscriber(self.adapter)

        filter_ = ["x == 3"]
        topic.subscribeWithFilters(subscriber1.proxy, filter_)

        topic.subscribeAndGetPublisher(subscriber2.proxy)

        # when the publisher sends several events
        data3 = MLP.Coord(3.0, 2.0, 0.0)
        data4 = MLP.Coord(8.0, 2.0, 0.0)
        publisher.sendData(self.data1)
        publisher.sendData(self.data2)
        publisher.sendData(data3)
        publisher.sendData(data4)
        subscriber1.servant.wait(2)
        subscriber2.servant.wait(2)

        # the subscriber receives the events matched with its filters and the
        # events are correct in the topic, and the general subscriber receives
        # all the events matched with the filters of topic
        self.assert_(subscriber1.servant.method_was_called('send_data',
                                                          (3.0, 2.0)))
        self.assertEqual(len(subscriber1.servant.get_registered_calls()), 1)
        self.assert_(subscriber2.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))
        self.assert_(subscriber2.servant.method_was_called('send_data',
                                                          (4.0, 23.0)))
        self.assert_(subscriber2.servant.method_was_called('send_data',
                                                          (3.0, 2.0)))
        self.assertEqual(len(subscriber2.servant.get_registered_calls()), 3)

    def test_filteredTopicAndFilteredPublisher(self):

        # given a general filtered Topic, a filtered publisher and a filtered
        # subscriber
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.filter1])

        filter2 = ["x in range(2,4)"]
        prx = topic.getFilteredPublisher("Filterin[2,4]", filter2)

        publisher = Event.ListenerPrx.uncheckedCast(prx)

        subscriber1 = mocks.Subscriber(self.adapter)

        filter3 = ["x == 3"]
        topic.subscribeWithFilters(subscriber1.proxy, filter3)

        # when the publisher sends several events
        data3 = MLP.Coord(3.0, 2.0, 0.0)
        data4 = MLP.Coord(2.0, 2.0, 0.0)
        publisher.sendData(self.data1)
        publisher.sendData(self.data2)
        publisher.sendData(data3)
        publisher.sendData(data4)
        subscriber1.servant.wait(2)

        # the subscriber receives the events matched with its filters
        self.assert_(subscriber1.servant.method_was_called('send_data',
                                                          (3.0, 2.0)))
        self.assertEqual(len(subscriber1.servant.get_registered_calls()), 1)

    def test_filteredTopicAndFilteredPublisherWithSeveralSubscribers(self):

        # given a general filtered Topic, a filtered publisher and a filtered
        # subscriber
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.filter1])

        filter2 = ["x in range(2,4)"]
        prx = topic.getFilteredPublisher("Filterin[2,4]", filter2)

        publisher = Event.ListenerPrx.uncheckedCast(prx)

        subscriber1 = mocks.Subscriber(self.adapter)
        subscriber2 = mocks.Subscriber(self.adapter)

        filter3 = ["x == 3"]
        topic.subscribeWithFilters(subscriber1.proxy, filter3)

        topic.subscribeAndGetPublisher(subscriber2.proxy)

        # when the publisher sends several events
        data3 = MLP.Coord(3.0, 2.0, 0.0)
        data4 = MLP.Coord(2.0, 2.0, 0.0)
        publisher.sendData(self.data1)
        publisher.sendData(self.data2)
        publisher.sendData(data3)
        publisher.sendData(data4)
        subscriber1.servant.wait(2)
        subscriber2.servant.wait(2)

        # the subscribers receive the events matched with its filters
        self.assert_(subscriber1.servant.method_was_called('send_data',
                                                          (3.0, 2.0)))
        self.assertEqual(len(subscriber1.servant.get_registered_calls()), 1)
        self.assert_(subscriber2.servant.method_was_called('send_data',
                                                          (3.0, 2.0)))
        self.assert_(subscriber2.servant.method_was_called('send_data',
                                                          (2.0, 2.0)))
        self.assertEqual(len(subscriber2.servant.get_registered_calls()), 2)

    def test_subscribeWithSeveralFilters(self):

        # given a general topic, a general publisher and a filtered subscriber
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber1 = mocks.Subscriber(self.adapter)

        # filter2 = self.filter1 +" and y > 2"
        filter2 = "y > 2"
        topic.subscribeWithFilters(subscriber1.proxy, [self.filter1, filter2])

        # when the publisher sends several events
        data3 = MLP.Coord(7.0, 12.0, 0.0)
        publisher.sendData(self.data1)
        subscriber1.servant.wait(2)
        publisher.sendData(self.data2)
        publisher.sendData(data3)
        subscriber1.servant.wait(2)

        # the subscriber receives the events matched with its filters
        self.assert_(subscriber1.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))
        self.assert_(subscriber1.servant.method_was_called('send_data',
                                                          (4.0, 23.0)))
        self.assertEqual(len(subscriber1.servant.get_registered_calls()), 2)

    def test_unsubcribe(self):

        # given a general topic, a general publisher and a filtered subscriber
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber1 = mocks.Subscriber(self.adapter)

        topic.subscribeWithFilters(subscriber1.proxy, [self.filter1])

        # when the publisher sends several events
        data = MLP.Coord(3.0, 2.0, 0.0)
        publisher.sendData(self.data1)
        subscriber1.servant.wait(2)

        # the subscriber receives the events matched with its filters
        # print subscriber1.servant.get_registered_calls()
        self.assert_(subscriber1.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))
        self.assertEqual(len(subscriber1.servant.get_registered_calls()), 1)

        # when the subscriber delete the suscription and the publisher sends a
        # event
        topic.unsubscribe(subscriber1.proxy)
        publisher.sendData(self.data2)
        subscriber1.servant.wait(2)

        self.assert_(not(subscriber1.servant.method_was_called('send_data',
                                                          (4.0, 23.0))))
        self.assertEqual(len(subscriber1.servant.get_registered_calls()), 1)
