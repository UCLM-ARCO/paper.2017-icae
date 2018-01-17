#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

import os
import threading
import time

import Ice
path = os.path.abspath(os.path.dirname(__file__))
SLICE_LS     = '/usr/share/mlp-slice/slice'
Ice.loadSlice(os.path.join(path, './TestDoubles.ice'))

import TestDoubles


class Invocation:
    def __init__(self, name, *args, **kargs):
        self.name = name
        self.args = args
        self.kargs = kargs

    def __eq__(self, other):
        return self.name == other.name and \
            self.args == other.args and \
            self.kargs == other.kargs

    def __repr__(self):
        return "<Invocation(%s, %s, %s)>" % (self.name, self.args, self.kargs)


class Spy(TestDoubles.Spy):
    def __init__(self):
        self.registered_calls = []
        self.event = threading.Event()

    def wait(self, seconds=None):
        self.event.wait(seconds)

    def method_was_called(self, name, args=(), kargs={}):
        invocation = Invocation(name, *args, **kargs)
        return  invocation in self.registered_calls

    def ice_ping(self, current=None):
        self.registered_calls.append(Invocation('ice_ping'))
        self.event.set()

    def get_registered_calls(self):
        return self.registered_calls

    def singleIntArg(self, n, current=None):
        self.registered_calls.append(Invocation('single_int_arg', n))
        self.event.set()

    def sendData(self, n, current=None):
        self.registered_calls.append(Invocation('send_data', n.x, n.y))
        self.event.set()

    def notice(self, msg, current=None):
        self.registered_calls.append(Invocation('notice', msg.x, msg.y))
        self.event.set()

    def event(self, msg, current=None):
        print "hola"
        self.registered_calls.append(Invocation('eventMsg', msg.source, msg.resourceId))
        self.event.set()

    def status(self, msg, current=None):
        self.registered_calls.append(Invocation('status', msg.source, msg.svStatus))
        self.event.set()
