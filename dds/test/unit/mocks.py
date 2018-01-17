#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import sys, Ice
sys.path.append('test')
SLICE_LS     = '/usr/share/mlp-slice/slice'
Ice.loadSlice('slices/Listener.ice --all \
-I{0} -I{1}'.format(SLICE_LS, Ice.getSliceDir()))

import Event

import IceDoubles

class ListenerI(Event.Listener):
    def sendData(self, n, current=None):
        print n


class Subscriber(object):
    def __init__(self, adapter, identity='sub'):
        ic = adapter.getCommunicator()
        self.servant = IceDoubles.Spy()
        # self.servant = ListenerI()
        # self.proxy = adapter.add(
        #     self.servant, ic.stringToIdentity(identity))
        self.proxy = adapter.addWithUUID(self.servant)

    def unsubscribe_from_topic(self,topic):
        topic.unsubscribe(self.proxy)

    def setFilter(self, f):
        self.servant.set_filter(f)
