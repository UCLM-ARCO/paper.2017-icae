#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import sys, time
sys.path.append('IceDDS')

import Ice
import IceDDS


class IceDDSManager(Ice.Application):

    def run(self, args):
        ic = self.communicator()

        manager_adapter = ic.createObjectAdapter("adapter")
        manager_adapter.activate()

        manager = IceDDS.TopicManager(manager_adapter)

        proxy = manager_adapter.add(manager,
                            ic.stringToIdentity("IceDDS/TopicManager"))

        print proxy

        ic.waitForShutdown()

        return 0


if __name__ == "__main__":
    sys.exit(IceDDSManager().main(sys.argv))
