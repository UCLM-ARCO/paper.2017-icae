#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import Ice, sys
sys.path.append('IceDDS')

SLICE_LS     = '/usr/share/mlp-slice/slice'
Ice.loadSlice('slices/DDS.ice -I {0} \
-I{1}'.format(SLICE_LS, Ice.getSliceDir()))


import DDS

class CreateTopics(Ice.Application):
    def run(self, argv):
        ic = self.communicator()

        base = ic.stringToProxy(argv[1])
        manager = DDS.TopicManagerPrx.checkedCast(base)

        x = DDS.VariableTypeCode('x', 'double')
        y = DDS.VariableTypeCode('y', 'double')
        z = DDS.VariableTypeCode('z', 'double')

        # Create general topic
        manager.createTopic("foo", [x,y,z])
        manager.createTopic("FilteredFoo", [x,y,z])
        # manager.createTopic("Mapa")
        # manager.createTopic("MapaArea1")
        # manager.createTopic("MapaArea2")
        # manager.createTopic("MapaArea3")

        # # Create a filtered topic
        # filters = 'x in range(1,14) and y in range(15,40)'


        # manager.createFilteredTopic("MapaArea1", [filters],
        #                             [x, y, z])
        # manager.createFilteredTopic("MapaArea2", [filters],
        #                             [x, y, z])
        # manager.createFilteredTopic("MapaArea3", [filters],
        #                             [x, y, z])

        # self.shutdownOnInterrupt()
        # ic.waitForShutdown()



if __name__ == "__main__":
    sys.exit(CreateTopics().main(sys.argv))
