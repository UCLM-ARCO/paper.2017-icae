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


        x = DDS.VariableTypeCode('x', 'double')
        y = DDS.VariableTypeCode('y', 'double')
        z = DDS.VariableTypeCode('z', 'double')

        topic = manager.retrieve("foo")
        filteredTopic = manager.retrieve("FilteredFoo")

        pubFilter = "x in range(10,20)"
        prx1 = topic.getFilteredPublisher('pub', [pubFilter])
        prx2 = filteredTopic.getFilteredPublisher('pub', [pubFilter])

        filteredPublisher1 = Event.ListenerPrx.uncheckedCast(prx1)
        filteredPublisher2 = Event.ListenerPrx.uncheckedCast(prx2)

        print "Send data to general topic"
        data1 = MLP.Coord(1.0, 2.0, 3.0)
        data2 = MLP.Coord(13.0, 13.0, 20.0)
        data3 = MLP.Coord(17.0, 23.0, 44.0)

        filteredPublisher1.sendData(data1)
        time.sleep(1.5)
        filteredPublisher1.sendData(data2)
        time.sleep(1.5)
        filteredPublisher1.sendData(data3)
        time.sleep(1.5)


        print "Send data to filtered topic"
        data4 = MLP.Coord(10.0, 18.0, 23.0)
        data5 = MLP.Coord(11.0, 8.0, 42.0)

        filteredPublisher2.sendData(data4)
        time.sleep(1.5)
        filteredPublisher2.sendData(data5)

        return 0

if __name__== "__main__":
     sys.exit(IceDDSPublisher().main(sys.argv))
