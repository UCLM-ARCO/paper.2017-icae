#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import Ice, sys

SLICE_LS     = '/usr/share/mlp-slice/slice'
Ice.loadSlice('slices/DDS.ice slices/Listener.ice \
--all -I {0} -I{1}'.format(SLICE_LS, Ice.getSliceDir()))


import DDS, Event, subscriber as SUB

class IceDDSSubscriber(Ice.Application):
    def run(self, argv):
        ic = self.communicator()
        adapter = ic.createObjectAdapterWithEndpoints("LinkedSubscriber",
                                                      "tcp -p 9500")
        adapter.activate()

        servant = SUB.ListenerI()
        subscriber = adapter.addWithUUID(servant)

        base = ic.stringToProxy(argv[1])
        manager = DDS.TopicManagerPrx.checkedCast(base)

        x = DDS.VariableTypeCode('x', 'double')
        y = DDS.VariableTypeCode('y', 'double')
        z = DDS.VariableTypeCode('z', 'double')


        # Create a topic to link
        filter1 = 'x > 10'
        filter2 = 'y < 20'
        linkedTopic = manager.createFilteredTopic("LinkedFoo",
                                                  [x, y, z],
                                                  [filter1, filter2])
        linkedTopic = manager.createTopic("LinkedFoo", [x, y, z])


        topic = manager.retrieve("foo")
        filteredTopic = manager.retrieve("FilteredFoo")

        publisher = Event.ListenerPrx.uncheckedCast(linkedTopic.getPublisher())

        linkedTopic.subscribeAndGetPublisher(subscriber)

        topic.linkFiltered(publisher)
        filteredTopic.linkFiltered(publisher)

        self.shutdownOnInterrupt()
        ic.waitForShutdown()

        return 0


if __name__ == "__main__":
    sys.exit(IceDDSSubscriber().main(sys.argv))
