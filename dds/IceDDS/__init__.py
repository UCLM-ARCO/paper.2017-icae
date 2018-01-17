#!/usr/bin/python
# -*- mode:python; coding:utf-8; tab-width:4 -*-

import Ice, IceStorm
import sys, warnings, threading
import filtersUtils as FU

if __file__.startswith('/usr'):
    SLICE_DIR = '/usr/share/slice/icedds'
else:
    SLICE_DIR = 'slices'


Ice.loadSlice('{0}/DDS.ice --all -I {1}'.format(
        SLICE_DIR, Ice.getSliceDir()))


import DDS, logging

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

class TopicManager(DDS.TopicManager):
    def __init__(self, adapter):
        self.ic = adapter.getCommunicator()
        self.manager_adapter = adapter
        proxy = self.ic.propertyToProxy('IceStorm.TopicManager.Proxy')
        self.delegate = IceStorm.TopicManagerPrx.checkedCast(proxy)
        self._logger = logging.getLogger("TopicManager")

        self._logger.setLevel(logging.INFO)
        # add the handlers to the logger
        self._logger.addHandler(ch)

    def getTopicProxy(self, name, topic):
        try:
            proxy = self.manager_adapter.add(topic,
                                            self.ic.stringToIdentity(name))

            self._logger.info("Created topic '" + name + "'")
            return proxy
        except Ice.AlreadyRegisteredException:
            self._logger.info("Registered topic '" + name + "'")
            return self.manager_adapter.createProxy(
                self.ic.stringToIdentity(name))

    def createTopic(self, name, typecode=None, current=None):

        topic = Topic(self.delegate, name, self.manager_adapter, typecode,
                      None)

        proxy = self.getTopicProxy(name, topic)

        return DDS.TopicPrx.uncheckedCast(proxy)

    def createFilteredTopic(self, name, eventTypecode, filters,
                            current=None):

        filteredTopic = Topic(self.delegate, name, self.manager_adapter,
                              eventTypecode, filters)

        proxy = self.getTopicProxy(name, filteredTopic)

        return DDS.TopicPrx.uncheckedCast(proxy)

    def retrieve(self, name, current=None):
        oid = self.ic.stringToIdentity(name)
        object = self.manager_adapter.find(oid)
        if object is None:
            raise IceStorm.NoSuchTopic(name)

        proxy = self.manager_adapter.createProxy(oid)

        return DDS.TopicPrx.uncheckedCast(proxy)

    def retrieveAll(self, current=None):
        topicList = {}
        for nameTopic, topic  in self.delegate.retrieveAll().iteritems():
            oid = self.ic.stringToIdentity(nameTopic)
            if self.manager_adapter.find(oid) is not None:
                topicList[nameTopic] = self.retrieve(nameTopic)

        return topicList
        # return self.delegate.retrieveAll


class DDSPublisher(Ice.BlobjectAsync):

    def __init__(self, peerPublisher, topic, adapter, topicDissector,
    pubDissector, subPub=""):
        self.cnt_35 = 0
        ic = adapter.getCommunicator()
        self.peerPublisher = peerPublisher
        self.adapter = adapter
        self.topicDissector = topicDissector
        self.pubDissector = pubDissector
        self.topicName = topic.getName()
        self._logger = logging.getLogger("PublisherDDS")

        self._logger.setLevel(logging.INFO)
        # add the handlers to the logger
        self._logger.addHandler(ch)


        self.namePublisher = topic.getName() + ".publish" + subPub

        self.oid = ic.stringToIdentity(self.namePublisher)

        try:
            self.adapter.add(self, self.oid)
            self._logger.info("Got publisher '" +
                               self.namePublisher + "' of Topic '" +
                               self.topicName + "'")


        except Ice.AlreadyRegisteredException:
            self._logger.info("Registered publisher of " +
                               self.namePublisher + " Topic")
            pass


    def setTopicDissector(self, topicDissector):
        self.topicDissector = topicDissector

    def ice_invoke_async(self, callback, bytes, current):
        validMethod = False

        # self.peerPublisher.ice_flushBatchRequests();
        out = chr(True)
        outParams = buffer(out)
        if (self.checkMethodNames(current.operation)):
            if self.checkFiltersData(bytes):
                self._logger.info("Sent Data " +
                                  # str(self.dissector.get_field(bytes)) +
                                  " from "+ self.namePublisher)


                ret = self.peerPublisher.ice_invoke_async(None, current.operation,
                                                 current.mode, bytes)



                callback.ice_response(True, outParams)

                return True

            else:
                msg = "The sent data is invalid in " + self.namePublisher
        else:
            msg = "This publisher cannot send data by invoking '" \
                    + current.operation + "'"
            # str(self.dissector.get_field(bytes))
            # + "' isn't valid for publisher '"
            # + self.namePublisher + "' in topic '"
            # + self.topicName + "'")


        self._logger.warning(msg)

        callback.ice_response(True, outParams)

        return True

    def checkMethodNames(self, operation):
        validMethodInTopic = False
        validMethodInPub = False

        # Check method in topic's filter

        if (self.topicDissector):
            if (self.topicDissector.getMethodName()):
                for method in self.topicDissector.getMethodName():
                    validMethodInTopic = validMethodInTopic or (method ==
                                                                operation)
        if (not self.topicDissector or
            (self.topicDissector and not self.topicDissector.getMethodName())):

            validMethodInTopic = True


        # Check method in publisher's filter

        if (self.pubDissector):
            if (self.pubDissector.getMethodName()):
                for method in self.pubDissector.getMethodName():
                    validMethodInPub = validMethodInPub or (method ==
                                                            operation)
        if (not self.pubDissector or
            (self.pubDissector and not self.pubDissector.getMethodName())):

            validMethodInPub = True


        return validMethodInTopic and validMethodInPub


    def checkFiltersData(self, bytes):
        matched = True
        if (self.topicDissector and self.topicDissector.filterSeq):
            # matched = matched and self.topicDissector.dissector_match_with_filter_classes(bytes)
            matched = matched and self.topicDissector.dissector_match(bytes)

        if (self.pubDissector and self.pubDissector.filterSeq):
            # matched = matched and self.pubDissector.dissector_match_with_filter_classes(bytes)
            matched = matched and self.pubDissector.dissector_match(bytes)

        return matched

    def destroy(self):
        self.adapter.remove(self.oid)

    def getProxy(self):
        return self.adapter.createProxy(self.oid)

class Topic(DDS.Topic, IceStorm.Topic):
    def __init__(self, delegateTM, name, manager_adapter,
                 typecode=None, topicFilterDef=None):
        try:
            self.ic = manager_adapter.getCommunicator()
            self.delegateTM = delegateTM
            self.name = name
            self.manager_adapter = manager_adapter
            self.topicFilterData = []
            self.topicFilterMethod = []
            self.typecode = typecode
            self.dissector = None

            self._logger = logging.getLogger("Topic")

            self._logger.setLevel(logging.INFO)
            # add the handlers to the logger
            self._logger.addHandler(ch)

            if topicFilterDef:
                for filter_ in topicFilterDef:
                    if (filter_.split(":")[0] == "method"):
                        self.topicFilterMethod.append(filter_.split(":")[1])
                    else:
                        self.topicFilterData.append(filter_)

                self.setDissector()

            self.delegate = delegateTM.create(name)
            self.setPublisher()

        except IceStorm.TopicExists:
            self.delegate = delegateTM.retrieve(name)


    def validateFilters(self, filters):
        try:
            # FU.validateExpressions(filters) // validate Expressions
            # MLP.Coord(Elcano)
            FU.validateTypeCodeAndFilter(filters, self.typecode)

        except Exception, ex:
            raise DDS.FilterError(ex.message)


    def setPublisher(self):
        self.defaultPublisher = DDSPublisher(self.delegate.getPublisher().ice_oneway(),
                                             self,
                                             self.manager_adapter,
                                             self.dissector, None)


    def setDissector(self):
        self.validateFilters(self.topicFilterData)

        self.dissector = FU.DataDissector(self.topicFilterData,
                                          self.typecode)

        # #### With object EventFilter
        # topicFilterData = FU.getFilter(self.topicFilterData)
        # self.dissector = FU.DataDissector(topicFilterData,
        #                                   self.typecode)

        if self.topicFilterMethod:
            self.dissector.setMethodName(self.topicFilterMethod)

    def setFilters(self, filters, current=None):
        self.topicFilterData = filters

        self.topicFilterData = []
        self.topicFilterMethod = []

        for filter_ in filters:
            if (filter_.split(":")[0] == "method"):
                self.topicFilterMethod.append(filter_.split(":")[1])
            else:
                self.topicFilterData.append(filter_)

        # self.dissector = FU.DataDissector(filters, self.typecode)

        #### With object EventFilter
        self.setDissector()

        self.defaultPublisher.setTopicDissector(self.dissector)



    def getName(self, current=None):
        return self.name

    def subscribeAndGetPublisher(self, subscriber, current=None):
        try:
            self.delegate.subscribeAndGetPublisher({}, subscriber)
            self._logger.info("Subscriber to " + self.name + " Topic")
        except IceStorm.AlreadySubscribed:
            self._logger.info("Already subscribed to topic " +
                               self.name)

        return self.getPublisher().ice_oneway()

    def subscribeWithFilters(self, subscriber, filters, current=None):

        # self.validateFilters(filters)

        nameSubscribeTopic = self.name + "=>" + \
                             self.ic.proxyToString(subscriber)


        # Create FilteredTopic
        filteredTopic = Topic(self.delegateTM, nameSubscribeTopic,
                                  self.manager_adapter, self.typecode, filters)

        try:
            proxy = self.manager_adapter.add(filteredTopic,
                                         self.ic.stringToIdentity(
                                                      nameSubscribeTopic))
        except Ice.AlreadyRegisteredException:
            proxy = self.manager_adapter.createProxy(
                self.ic.stringToIdentity(nameSubscribeTopic))



        # Subscribe to created Topic
        filteredTopic.delegate.subscribeAndGetPublisher({}, subscriber)

        publisher = DDSPublisher(filteredTopic.delegate.getPublisher().ice_oneway(),
                                 filteredTopic, self.manager_adapter,
                                 filteredTopic.dissector, None).getProxy()

        # Link the publisher of create Topic
        self.linkFiltered(publisher)

        return DDS.TopicPrx.uncheckedCast(proxy)


    def getPublisher(self, current=None):
        self.defaultPublisher = DDSPublisher(self.delegate.getPublisher().ice_oneway(),
                                             self,
                                             self.manager_adapter,
                                             self.dissector, None)
        return self.defaultPublisher.getProxy().ice_oneway()

    def getFilteredPublisher(self, publisherName, filters, current=None):

        filtersDataDef = []
        filtersMethodNames = []
        for filter_ in filters:
            if (filter_.split(":")[0] == "method"):
                filtersMethodNames.append(filter_.split(":")[1])
            else:
                filtersDataDef.append(filter_)


        # self.setDissector()

        self.validateFilters(filtersDataDef)

        # ### With object EventFilter
        # filtersSeq = []
        # for filter_ in filters:
        #     filtersSeq.append(filter_)

        # filtersPub = FU.getFilter(filtersDataDef)
        # pubDissector = FU.DataDissector(filtersPub, self.typecode)
        pubDissector = FU.DataDissector(filtersDataDef, self.typecode)
        if filtersMethodNames:
            pubDissector.setMethodName(filtersMethodNames)


        publisher = DDSPublisher(self.delegate.getPublisher().ice_oneway(), self,
                                 self.manager_adapter,
                                 self.dissector,
                                 pubDissector,
                                 publisherName).getProxy()



        # publisher = DDSPublisher(self.delegate.getPublisher(), self,
        #                          self.manager_adapter,
        #                          self.dissector,
        #                          FU.DataDissector(filters,
        #                          eventTypecode),
        #                          publisherName).getProxy()

        self._logger.info("Got filtered publisher of " + self.name +
                           " Topic")

        return publisher

    def getFilters(self, current=None):
        return self.topicFilterData

    def link(self, linkTo, cost, current=None):
        self.delegate.link(linkTo, cost)

    def unlink(self, linkTo, current=None):
        self.delegate.unlink(linkTo)

    def linkFiltered(self, publisher, current=None):
        try:
            self.delegate.subscribeAndGetPublisher({}, publisher)
        except IceStorm.AlreadySubscribed:
            self._logger.info("Already subscribed to topic " +
                               self.name)

    def unlinkFiltered(self, publisher, current=None):
        self.delegate.unsubscribe(publisher)

    def unsubscribe(self, subscriber, current=None):
        self.delegate.unsubscribe(subscriber)
        self._logger.info("Unsubscribed Subscriber")

    def destroy(self, current=None):
        self.delegate.destroy()
        self._logger.info("Topic '" + self.name + "' destroyed")
