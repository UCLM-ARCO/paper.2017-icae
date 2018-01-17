import sys, time
sys.path.append('IceDDS')
sys.path.append('test')

import unittest, Ice, IceDDS, IceStorm
import EventFilters as Evt
from mock import Mock
import mocks
SLICE_LS     = '/usr/share/mlp-slice/slice'
SLICE_ENERGOS = '../prj.energos-middleware/examples/icedds-java/slice'

Ice.loadSlice('slices/DDS.ice  {0}/Energos.ice \
--all -I{1} -I{2}'.format(SLICE_ENERGOS, SLICE_LS, Ice.getSliceDir()))

import DDS, MLP, Energos

class TestFiltersExceptions(unittest.TestCase):

    def setUp(self):
        argv = ["--Ice.Config=test/unit/topics.config"]
        self.ic = Ice.initialize(argv)

        self.data = MLP.Coord(1.0, 12.0, 0.0)

        self.point_typecode = [DDS.VariableTypeCode('source', 'string'),
                               DDS.VariableTypeCode('resourceId', 'string'),
                               DDS.VariableTypeCode('timeStamp', 'long'),
                               DDS.VariableTypeCode('eventType', 'int'),
                               DDS.VariableTypeCode('svStatus', 'int'),
                               DDS.VariableTypeCode('eventValueQuality', 'string')]

        self.methodFilter = "method:status"
        self.filter1 = "eventType in range(1,23)"

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

    def test_filteredInTopic(self):
        # given a filtered method topic, a publisher and subscriptor
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.methodFilter])

        subscriber = mocks.Subscriber(self.adapter)
        topic.subscribeAndGetPublisher(subscriber.proxy)

        publisher = Energos.ControlSinkPrx.uncheckedCast(topic.getPublisher())

        # when the publisher sends a event
        publisher.status(self.data1)
        publisher.event(self.data1)
        subscriber.servant.wait(2)

        # then the subscriber receives the event
        self.assert_(subscriber.servant.method_was_called('status', ("101", 12)))
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)


    def test_receivedMsgWithBothFilterType(self):
        # given a filtered method topic, a publisher and subscriptor
        dataFilter = "svStatus in range(6,15)"
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.methodFilter,
                                                       dataFilter])

        subscriber = mocks.Subscriber(self.adapter)
        topic.subscribeAndGetPublisher(subscriber.proxy)

        publisher = Energos.ControlSinkPrx.uncheckedCast(topic.getPublisher())

        # when the publisher sends a event
        publisher.status(self.data1)
        publisher.event(self.data1)
        subscriber.servant.wait(2)

        # then the subscriber receives the event
        self.assert_(subscriber.servant.method_was_called('status',
                                                          ("101", 12)))
        self.assert_(not(subscriber.servant.method_was_called('eventMsg',
                                                              ("101", "HUJE345"))))

        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)

    def test_receivedMsgWithDataNotMatch(self):
        # given a filtered method topic, a publisher and subscriptor
        dataFilter = "eventType in range(6,15)"
        topic = self.topicManager.createFilteredTopic("foo",
                                                      self.point_typecode,
                                                      [self.methodFilter,
                                                       "method:status",
                                                       dataFilter])

        subscriber = mocks.Subscriber(self.adapter)
        topic.subscribeAndGetPublisher(subscriber.proxy)

        publisher = Energos.ControlSinkPrx.uncheckedCast(topic.getPublisher())

        # when the publisher sends a event
        publisher.status(self.data1)
        publisher.status(self.data2)
        subscriber.servant.wait(2)

        # then the subscriber doesn't receive the event from sendData because
        # data doesn't match with filter
        self.assert_(subscriber.servant.method_was_called('status',
                                                          ("101", 12)))
        self.assert_(not(subscriber.servant.method_was_called('status',
                                                          ("102", 3))))

        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)


    def test_filteredInPublisher_Success(self):
        # given a topic, a filtered publisher and a subcriptor
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        prx = topic.getFilteredPublisher("Filter1",
                                         [self.methodFilter])

        filteredPublisher = Energos.ControlSinkPrx.uncheckedCast(prx)
        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends several events
        filteredPublisher.status(self.data1)
        subscriber.servant.wait(2)

        # the subscriber receives events
        self.assert_(subscriber.servant.method_was_called('status',
                                                          ("101", 12)))

        self.assertEqual(len(subscriber.servant.get_registered_calls()), 1)

    def test_notMethodInServantWithFilteredPublisher(self):
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        prx = topic.getFilteredPublisher("Filter1",
                                         [self.methodFilter])


        filteredPublisher = Energos.ControlSinkPrx.uncheckedCast(prx)
        subscriber = self.subscribe_to_topic(topic)

        # when the publisher sends several events
        filteredPublisher.event(self.data1)
        subscriber.servant.wait(2)

        # the subscriber receives events
        self.assertEqual(len(subscriber.servant.get_registered_calls()), 0)

    def test_filteredInSubscriberSuccess(self):

        # given a general topic, a general publisher and a filtered subscriber
        topic = self.topicManager.createTopic("foo", self.point_typecode)

        publisher = Energos.ControlSinkPrx.uncheckedCast(topic.getPublisher())

        subscriber1 = mocks.Subscriber(self.adapter)

        topic.subscribeWithFilters(subscriber1.proxy, [self.methodFilter])

        # when the publisher sends several events
        publisher.event(self.data1)
        publisher.status(self.data1)
        subscriber1.servant.wait(2)

        # the subscriber receives the events matched with its filters
        self.assert_(subscriber1.servant.method_was_called('status',
                                                          ("101", 12)))
        self.assertEqual(len(subscriber1.servant.get_registered_calls()), 1)
