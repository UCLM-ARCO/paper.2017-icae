#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import Ice, IceStorm
import sys, time
sys.path.append('src')

Ice.loadSlice('src/DDS.ice -I. --all -I {0}'.format(Ice.getSliceDir()))
Ice.loadSlice('hello.ice')


import DDS, Example

class IceDDSPublisher(Ice.Application):

    def run(self, argv):
        ic = self.communicator()

        base = ic.stringToProxy(argv[1])
        manager = DDS.TopicManagerPrx.checkedCast(base)

        topic = manager.retrieve("foo")

        publisher = Example.ListenerPrx.uncheckedCast(topic.getPublisher())


        publisher.sendData(Example.Event(1))
        publisher.sendData(Example.Event(5))

        return 0

if __name__== "__main__":
     sys.exit(IceDDSPublisher().main(sys.argv))
