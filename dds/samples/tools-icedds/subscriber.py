#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import Ice, sys
sys.path.append('icedds')

SLICE_LS     = '/usr/share/mlp-slice/slice'
Ice.loadSlice('slices/DDS.ice slices/Listener.ice \
--all -I {0} -I{1}'.format(SLICE_LS, Ice.getSliceDir()))


import DDS, Event

class ListenerI(Event.Listener):

    def sendData(self, n, current=None):
        print "Received Event (%i, %i, %i)" % (n.x, n.y, n.z)

class IceDDSSubscriber(Ice.Application):
    def run(self, argv):
        ic = self.communicator()
        adapter = ic.createObjectAdapter("IceDDSSubscriber.Adapter")
        adapter.activate()

        servant = ListenerI()
        subscriber = adapter.addWithUUID(servant)

        base = ic.stringToProxy(argv[1])
        manager = DDS.TopicManagerPrx.checkedCast(base)

        # Retrive topics
        topic = manager.retrieve("foo")
        filteredTopic = manager.retrieve("FilteredFoo")


        topic.subscribeAndGetPublisher(subscriber)
        filteredTopic.subscribeAndGetPublisher(subscriber)

        self.shutdownOnInterrupt()
        ic.waitForShutdown()



if __name__ == "__main__":
    sys.exit(IceDDSSubscriber().main(sys.argv))
