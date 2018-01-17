#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import Ice, IceStorm
import sys, time
sys.path.append('IceDDS')

import EventFilters as Evt
SLICE_LS     = '/usr/share/mlp-slice/slice'
Ice.loadSlice('slices/DDS.ice slices/Listener.ice \
--all -I {0} -I{1}'.format(SLICE_LS, Ice.getSliceDir()))


import DDS, MLP, Event

class IceDDSPublisher(Ice.Application):

    def run(self, argv):
        ic = self.communicator()

        base = ic.stringToProxy(argv[1])
        manager = DDS.TopicManagerPrx.checkedCast(base)

        topic = manager.retrieve("foo")
        prx1 = topic.getPublisher()
        publisher1 = Event.ListenerPrx.uncheckedCast(prx1)

        filteredTopic = manager.retrieve("FilteredFoo")

        prx2 = filteredTopic.getPublisher()
        publisher2 = Event.ListenerPrx.uncheckedCast(prx2)

        print "Send data to general topic"
        data1 = MLP.Coord(2.0, 3.0, 4.0)
        data2 = MLP.Coord(5.0, 14.0, 20.0)

        i = 1
        while(True):
                    print i
                    publisher1.sendData(data1)
                    time.sleep(1)
                    i = i + 1

        # publisher1.sendData(data2)
        # time.sleep(1.5)

        # print "Send data to filtered topic"
        # data3 = MLP.Coord(12.0, 16.0, 3.0)
        # data4 = MLP.Coord(15.0, 20.0, 8.0)
        # data5 = MLP.Coord(2.0, 23.0, 42.0)

        # publisher2.sendData(data3)
        # time.sleep(1.5)
        # publisher2.sendData(data4)
        # time.sleep(1.5)
        # publisher2.sendData(data5)

        return 0

if __name__== "__main__":
     sys.exit(IceDDSPublisher().main(sys.argv))
