#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import Ice, sys
sys.path.append('src')

SLICE_LS     = '/usr/share/mlp-slice/slice'
Ice.loadSlice('slices/DDS.ice -I{0} \
-I{1}'.format(SLICE_LS, Ice.getSliceDir()))


import DDS, subscriber as SUB

class IceDDSSubscriber(Ice.Application):
    def run(self, argv):
        ic = self.communicator()
        adapter = ic.createObjectAdapterWithEndpoints("FilteredSubscriber",
                                                       "tcp -p 9000")
        adapter.activate()

        servant = SUB.ListenerI()
        subscriber = adapter.addWithUUID(servant)

        base = ic.stringToProxy(argv[1])
        manager = DDS.TopicManagerPrx.checkedCast(base)

        filters1 = 'x in range(5,20)'
        filters2 = 'y > 13'

        x = DDS.VariableTypeCode('x', 'double')
        y = DDS.VariableTypeCode('y', 'double')
        z = DDS.VariableTypeCode('z', 'double')

        topic = manager.retrieve("foo")

        filteredTopic = manager.retrieve("FilteredFoo")

        topic.subscribeWithFilters(subscriber, [filters1, filters2])

        filteredTopic.subscribeWithFilters(subscriber, [filters1, filters2])

        self.shutdownOnInterrupt()
        ic.waitForShutdown()



if __name__ == "__main__":
    sys.exit(IceDDSSubscriber().main(sys.argv))
