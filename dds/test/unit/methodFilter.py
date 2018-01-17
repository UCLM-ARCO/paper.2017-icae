import sys, time
sys.path.append('IceDDS')
sys.path.append('test')

import unittest, Ice, IceDDS, IceStorm
import EventFilters as Evt
from mock import Mock
import mocks
SLICE_LS     = '/usr/share/mlp-slice/slice'

Ice.loadSlice('slices/DDS.ice slices/Listener.ice \
--all -I{0} -I{1}'.format(SLICE_LS, Ice.getSliceDir()))

import DDS, MLP, Event

class TestFiltersExceptions(unittest.TestCase):

    def setUp(self):
        argv = ["--Ice.Config=test/unit/topics.config"]
        self.ic = Ice.initialize(argv)

        self.methodFilter = "method:sendData"
        self.data = MLP.Coord(1.0, 12.0, 0.0)

        self.adapter = self.ic.createObjectAdapter("OA")
        self.adapter.activate()

        self.point_typecode = [DDS.VariableTypeCode('x', 'double'),
                               DDS.VariableTypeCode('y', 'double'),
                               DDS.VariableTypeCode('z', 'double')]

        self.topicManager = IceDDS.TopicManager(self.adapter)

    def tearDown(self):
        for topic in self.topicManager.retrieveAll().values():
            topic.destroy()

        self.ic.destroy()

    def subscribe_to_topic(self, tp):
        subscriber = mocks.Subscriber(self.adapter)
        tp.subscribeAndGetPublisher(subscriber.proxy)
        return subscriber

    def test_filteredInTopic(self):
        # given a filtered method topic, a publisher and subscriptor
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      ["method:notice"])

        subscriber = mocks.Subscriber(self.adapter)
        topic.subscribeAndGetPublisher(subscriber.proxy)

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        # when the publisher sends a event
        publisher.sendData(self.data)
        publisher.notice(self.data)
        subscriber.servant.wait(2)

        # then the subscriber receives the event
        self.assert_(subscriber.servant.method_was_called('notice', (1.0, 12.0)))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)

    def test_filteredInTopic2(self):
        # given a filtered method topic, a publisher and subscriptor
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.methodFilter])

        subscriber = mocks.Subscriber(self.adapter)
        topic.subscribeAndGetPublisher(subscriber.proxy)

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        # when the publisher sends a event
        publisher.sendData(self.data)
        publisher.notice(self.data)
        subscriber.servant.wait(2)

        # then the subscriber receives the event
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))
        self.assert_(not(subscriber.servant.method_was_called('notice', (1.0, 12.0))))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)

    def test_receivedMsgWithBothFilterType(self):
        # given a filtered method topic, a publisher and subscriptor
        dataFilter = "x in range(1,5)"
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.methodFilter,
                                                       dataFilter])

        subscriber = mocks.Subscriber(self.adapter)
        topic.subscribeAndGetPublisher(subscriber.proxy)

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        # when the publisher sends a event
        publisher.sendData(self.data)
        publisher.notice(self.data)
        subscriber.servant.wait(2)

        # then the subscriber receives the event
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))
        self.assert_(not(subscriber.servant.method_was_called('notice',
                                                              (1.0, 12.0))))

        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)

    def test_receivedMsgWithDataNotMatch(self):
        # given a filtered method topic, a publisher and subscriptor
        dataFilter = "x in range(1,5)"
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.methodFilter,
                                                       "method:notice",
                                                       dataFilter])

        subscriber = mocks.Subscriber(self.adapter)
        topic.subscribeAndGetPublisher(subscriber.proxy)

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        # when the publisher sends a event
        data = MLP.Coord(6.0, 7.0, 0.0)
        publisher.sendData(self.data)
        publisher.notice(data)
        subscriber.servant.wait(2)

        # then the subscriber doesn't receive the event from sendData because
        # data doesn't match with filter
        self.assert_(not(subscriber.servant.method_was_called('notice',
                                                          (6.0, 7.0))))
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))

        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)


    def test_receivedMsgWithSeveralDataFilters(self):
        # given a filtered method topic, a publisher and subscriptor
        dataFilter = "x in range(1,5) or x > 10"
        dataFilter2 = "y > 3"
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.methodFilter,
                                                       "method:notice",
                                                       dataFilter,
                                                       dataFilter2])

        subscriber = mocks.Subscriber(self.adapter)
        topic.subscribeAndGetPublisher(subscriber.proxy)

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        # when the publisher sends a event
        data = MLP.Coord(16.0, 7.0, 0.0)
        data1 = MLP.Coord(3.0, 2.0, 0.0)
        publisher.sendData(data)
        publisher.notice(data)
        subscriber.servant.wait(2)
        publisher.sendData(self.data)
        publisher.sendData(data1)
        subscriber.servant.wait(2)

        # then the subscriber receives two events
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (1.0, 12.0)))
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (16.0, 7.0)))
        self.assert_(subscriber.servant.method_was_called('notice',
                                                          (16.0, 7.0)))
        self.assert_(not(subscriber.servant.method_was_called('send_data',
                                                          (3.0, 2.0))))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 3)

    def test_filteredInPublisher_Success(self):
        # given a topic, a filtered publisher and a subcriptor
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        prx = topic.getFilteredPublisher("Filter1",
                                         [self.methodFilter])

        filteredPublisher = Event.ListenerPrx.uncheckedCast(prx)
        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends several events
        data = MLP.Coord(16.0, 7.0, 0.0)
        filteredPublisher.sendData(data)
        filteredPublisher.notice(data)
        subscriber.servant.wait(2)

        # the subscriber receives events
        self.assert_(subscriber.servant.method_was_called('send_data',
                                                          (16.0, 7.0)))

        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)

    def test_notMethodInServantWithFilteredPublisher(self):
        topic = self.topicManager.createTopic("foo", self.point_typecode)
        methodFilter = "method:notice"

        prx = topic.getFilteredPublisher("Filter1",
                                         [methodFilter])

        filteredPublisher = Event.ListenerPrx.uncheckedCast(prx)
        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends several events
        data = MLP.Coord(16.0, 7.0, 0.0)
        filteredPublisher.sendData(data)
        subscriber.servant.wait(2)

        # the subscriber receives events
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 0)

    def test_filteredInSubscriberSuccess(self):

        # given a general topic, a general publisher and a filtered subscriber
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber1 = mocks.Subscriber(self.adapter)

        topic.subscribeWithFilters(subscriber1.proxy, [self.methodFilter])

        # when the publisher sends several events
        data = MLP.Coord(7.0, 2.0, 0.0)
        publisher.sendData(data)
        publisher.notice(data)
        subscriber1.servant.wait(2)

        # the subscriber receives the events matched with its filters
        self.assert_(subscriber1.servant.method_was_called('send_data',
                                                          (7.0, 2.0)))
        self.assertEqual(len(subscriber1.servant.get_registered_calls()), 1)

    def test_filteredInSubscriberFail(self):

        # given a general topic, a general publisher and a filtered subscriber
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        publisher = Event.ListenerPrx.uncheckedCast(topic.getPublisher())

        subscriber1 = mocks.Subscriber(self.adapter)

        topic.subscribeWithFilters(subscriber1.proxy, ["method:notice"])


        # when the publisher sends several events
        data = MLP.Coord(7.0, 2.0, 0.0)
        publisher.notice(data)
        publisher.sendData(data)
        subscriber1.servant.wait(2)

        # the subscriber receives the events matched with its filters
        self.assert_(subscriber1.servant.method_was_called('notice',
                                                          (7.0, 2.0)))
        self.assertEqual(len(subscriber1.servant.get_registered_calls()), 1)
