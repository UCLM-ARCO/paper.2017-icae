#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import Ice, sys
sys.path.append('src')

Ice.loadSlice('src/DDS.ice -I. --all -I {0}'.format(Ice.getSliceDir()))
Ice.loadSlice('hello.ice')


import DDS, Example

class ListenerI(Example.Listener):

    def sendData(self, event, current=None):
        print "Received Event (%i)" % (event.x)

class IceDDSSubscriber(Ice.Application):
    def run(self, argv):
        ic = self.communicator()
        adapter = ic.createObjectAdapter("Subscriber.Adapter")
        adapter.activate()

        servant = ListenerI()
        subscriber = adapter.addWithUUID(servant)

        base = ic.stringToProxy(argv[1])
        manager = DDS.TopicManagerPrx.checkedCast(base)


        filter_ = DDS.Filter('x in [2,65]')
        x = DDS.VariableTypeCode('x', 'int')
        topic = manager.createFilteredTopic("foo", [filter_], (x,))

        topic.subscribeAndGetPublisher(subscriber)

        self.shutdownOnInterrupt()
        ic.waitForShutdown()



if __name__ == "__main__":
    sys.exit(IceDDSSubscriber().main(sys.argv))
