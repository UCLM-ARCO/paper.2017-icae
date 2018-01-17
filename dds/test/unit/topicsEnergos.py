#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import sys, time
sys.path.append('test')
sys.path.append('IceDDS')

import unittest, Ice, IceStorm
import IceDoubles
import IceDDS
import mocks

SLICE_LS     = '/usr/share/mlp-slice/slice'
SLICE_ENERGOS = '../prj.energos-middleware/examples/icedds-java/slice'

Ice.loadSlice('slices/DDS.ice  {0}/Energos.ice \
--all -I{1} -I{2}'.format(SLICE_ENERGOS, SLICE_LS, Ice.getSliceDir()))

import DDS, Energos

class TestTopic(unittest.TestCase):
    def setUp(self):
        argv = ["--Ice.Config=test/unit/topics.config"]
        self.ic = Ice.initialize(argv)

        self.adapter = self.ic.createObjectAdapter("OA")
        self.adapter.activate()
        self.topicManager = IceDDS.TopicManager(self.adapter)

    def tearDown(self):
        for topic in self.topicManager.retrieveAll().values():
            topic.destroy()

        self.ic.destroy()

    def subscribe_to_topic(self, tp, name='foo'):
        return mocks.Subscriber(self.adapter,name).subscribe_to_topic(tp)

    def test_msgReceived(self):
        # given a topic, a publisher and a subscriptor
        topic = self.topicManager.createTopic("foo")
        publisher = topic.getPublisher()
        subscriber = mocks.Subscriber(self.adapter)
        topic.subscribeAndGetPublisher(subscriber.proxy)

        prx = Energos.ControlSinkPrx.uncheckedCast(publisher)

        # when the publisher sends a event
        prx.ice_ping()
        subscriber.servant.wait(2)

        # then the subscriptor receives the event
        self.assert_(subscriber.servant.method_was_called('ice_ping'))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)


    def test_notMsgReceiveWithoutSubscribe(self):
        # given a topic1, a topic2, a publisher of the topic1 and a subscriptor
        # to the topic2

        topic1 = self.topicManager.createTopic("topic1")
        topic2 = self.topicManager.createTopic("topic2")

        subscriber2 = mocks.Subscriber(self.adapter)
        topic2.subscribeAndGetPublisher(subscriber2.proxy)

        publisher = topic1.getPublisher()
        prx = Energos.ControlSinkPrx.uncheckedCast(publisher)

        # when the publisher of topic1 sends a event
        prx.ice_ping()
        subscriber2.servant.wait(2)

        # then the subscriptor of the topic2 doesn't receive the event
        self.assert_(not(subscriber2.servant.method_was_called('ice_ping')))


    def test_msgReceiveInSeveralSubscribers(self):
        # given a topic, a publisher and two subscriptors
        topic = self.topicManager.createTopic("foo")

        subscriber1 = mocks.Subscriber(self.adapter, 'sub1')
        topic.subscribeAndGetPublisher(subscriber1.proxy)
        subscriber2 = mocks.Subscriber(self.adapter, 'sub2')
        topic.subscribeAndGetPublisher(subscriber2.proxy)

        publisher = topic.getPublisher()
        prx = Energos.ControlSinkPrx.uncheckedCast(publisher)

        # when the publisher sends a event
        prx.ice_ping()
        subscriber1.servant.wait(2)
        subscriber2.servant.wait(2)

        # then the two subscriptors receive the event
        self.assert_(subscriber1.servant.method_was_called('ice_ping'))
        self.assert_(subscriber2.servant.method_was_called('ice_ping'))


    def test_severalPublishersInATopic(self):
        # given a topic, two publisher of the topic and a subscriptor to the
        # topic
        topic = self.topicManager.createTopic("topic1")

        subscriber = mocks.Subscriber(self.adapter)
        topic.subscribeAndGetPublisher(subscriber.proxy)

        publisher1 = topic.getPublisher()
        publisher2 = topic.getPublisher()

        prx1 = Energos.ControlSinkPrx.uncheckedCast(publisher1)
        prx2 = Energos.ControlSinkPrx.uncheckedCast(publisher2)

        # when the publishers send an event each
        prx1.ice_ping()
        prx2.ice_ping()
        subscriber.servant.wait(2)

        # then the subscriptor receives the two events
        self.assert_(subscriber.servant.method_was_called('ice_ping'))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 2)

    def test_twoTopicsTwoPublishersOneSubscriber(self):
        # given a topic1, a topic2, a publisher of the topic1, other of the
        # topic2 and a subscriptor to the two topics
        topic1 = self.topicManager.createTopic("topic1")
        topic2 = self.topicManager.createTopic("topic2")

        subscriber = mocks.Subscriber(self.adapter)
        topic1.subscribeAndGetPublisher(subscriber.proxy)
        topic2.subscribeAndGetPublisher(subscriber.proxy)

        publisher1 = topic1.getPublisher()
        publisher2 = topic2.getPublisher()

        prx1 = Energos.ControlSinkPrx.uncheckedCast(publisher1)
        prx2 = Energos.ControlSinkPrx.uncheckedCast(publisher2)

        # when the publishers send an event each
        prx1.ice_ping()
        prx2.ice_ping()
        subscriber.servant.wait(2)

        # then the subscriptor receives the two events
        self.assert_(subscriber.servant.method_was_called('ice_ping'))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 2)
