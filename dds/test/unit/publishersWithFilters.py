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

class TestFilteredPublishers(unittest.TestCase):

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

    def test_filteredInPublisher_Success(self):
        # given a topic, a filtered publisher and a subcriptor
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        prx = topic.getFilteredPublisher("Filter1",
                                         [self.filter1])

        filteredPublisher = Event.ListenerPrx.uncheckedCast(prx)
        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends several events
        filteredPublisher.sendData(self.data1)
        filteredPublisher.sendData(self.data2)
        subscriber.servant.wait(2)

        # the subscriber receives events
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))

        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (4.0, 23.0)))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 2)

    def test_filteredPublisherAndTopic_Success(self):
        # given a filtered topic of values with range (1, 5), a filtered
        # publisher of values > 2, and a subscriber
        filter2 = ["x > 2"]

        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.filter1])


        prx = topic.getFilteredPublisher("Filter2", filter2)

        filteredPublisher = Event.ListenerPrx.uncheckedCast(prx)
        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends events
        data = MLP.Coord(3.0, 5.0, 0.0)
        filteredPublisher.sendData(data)
        filteredPublisher.sendData(self.data2)
        subscriber.servant.wait(2)

        # the subscriber receives event
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (3.0, 5.0)))
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (4.0, 23.0)))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 2)


    def test_InvalidDataWithFilteredInPublisher(self):
        # given a topic and a filteredPublisher
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        prx = topic.getFilteredPublisher("Filter1",
                                         [self.filter1])

        filteredPublisher = Event.ListenerPrx.uncheckedCast(prx)

        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends a invalid event
        filteredPublisher.sendData(self.invalidData)
        subscriber.servant.wait(2)

        # the suscriber doesn't receive event
        self.assert_(not(subscriber.servant.method_was_called('send_data',
                                                              (6.0, 32.0))))

        self.assertEqual(len(subscriber.servant.get_registered_calls()), 0)

    def test_InvalidDataWithFilteredInPublisherAndInTopic(self):
        # given a filtered topic and a filteredPublisher
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.filter1])
        filterInPublisher = "x == 3"
        prx = topic.getFilteredPublisher("Filter1",
                                         [filterInPublisher])

        filteredPublisher = Event.ListenerPrx.uncheckedCast(prx)

        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends a invalid event
        filteredPublisher.sendData(self.data2)
        subscriber.servant.wait(2)

        # the suscriber doesn't receive event
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 0)

    def test_filteredAndNotInpublisherWithGeneralTopic(self):
        # given a general topic, a general publisher, a filtered publisher and
        # a subscriber

        filter2 = ["x == 2"]

        topic = self.topicManager.createTopic("foo", self.point_typecode)

        prx = topic.getFilteredPublisher("PubFilter2", filter2)


        filteredPublisher = Event.ListenerPrx.uncheckedCast(prx)
        publisherTopic = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends events
        data1 = MLP.Coord(7.0, 9.0, 0.0)
        data2 = MLP.Coord(2.0, 6.0, 0.0)
        publisherTopic.sendData(data1)
        filteredPublisher.sendData(data2)
        subscriber.servant.wait(2)

        # the subscriber receives all events
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (7.0, 9.0)))
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (2.0, 6.0)))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 2)

    def test_filteredAndNotInpublisherWithFilteredTopic(self):
        # given a filtered topic of values with range (1, 5), a filtered
        # publisher of 2, a general publisher, and a subscriber

        filter2 = ["x == 2"]

        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.filter1])

        publisherTopic = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        prx = topic.getFilteredPublisher("PubFilter2", filter2)


        filteredPublisher = Event.ListenerPrx.uncheckedCast(prx)
        subscriber = self.subscribe_to_topic(topic)

        # when the filtered publisher send a event and the general publisher
        # sends a event
        data2 = MLP.Coord(2.0, 2.0, 0.0)
        publisherTopic.sendData(self.data1)
        filteredPublisher.sendData(data2)
        publisherTopic.sendData(self.invalidData)
        subscriber.servant.wait(2)

        # the subscriber receives all events
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (2.0, 2.0)))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 2)

    def test_severalFilterInTopicAndInPublisher(self):
        # given a filteredTopic with several filters, a subscriber and a
        # filtered publisher
        # filter2 = self.filter1 +" and y > 10"
        filter2 = "y > 10"

        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.filter1, filter2])

        filter1 = "x == 4"
        filter2 = "y in range(11,28)"
        prx = topic.getFilteredPublisher("X3Range1215",
                                               [filter1, filter2])

        publisher = Event.ListenerPrx.uncheckedCast(prx)

        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends several events

        # publisher.sendData(self.data1)
        publisher.sendData(self.data2)
        subscriber.servant.wait(2)

        # then the subscriptor receives one event because the event 2 is
        # invalid in the topic
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (4.0, 23.0)))
        self.assert_(not(subscriber.servant.method_was_called('send_data',
                                                          (1.0, 12.0))))
