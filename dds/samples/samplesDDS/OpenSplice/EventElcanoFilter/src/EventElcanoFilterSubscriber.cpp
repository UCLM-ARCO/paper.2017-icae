#include <string>
#include <sstream>
#include <iostream>
#include "DDSEntityManager.h"
#include "ccpp_EventElcanoFilter.h"


using namespace DDS;
using namespace EventElcanoFilter;

int main(int argc, char *argv[])
{
  // usage : EventElcanoFilterSubscriber <subscription_string>
  const char *filter;
  os_time delay_200ms = { 0, 200000000 };

  if (argc > 1)
  {
    filter = argv[1];
  }
  else
  {
    cerr <<
      "*** [EventElcanoFilterSubscriber] Provider not specified" <<
      endl;
    cerr << "*** usage : EventElcanoFilterSubscriber <provider_name>"
         << endl;
    return  - 1;
  }

  LocEventSeq msgList;
  SampleInfoSeq infoSeq;

  DDSEntityManager *mgr = new DDSEntityManager();

  // create domain participant
  char partition_name[] = "EventElcanoFilterTopic example";
  mgr->createParticipant(partition_name);

  //create type
  LocEventTypeSupport_var st = new LocEventTypeSupport();
  mgr->registerType(st.in());

  //create Topic
  char topic_name[] = "LocEventTrackerExclusive";
  mgr->createTopic(topic_name);

  //create Subscriber
  mgr->createSubscriber();

  char sTopicName[] = "MyLocEventTopic";
  // create subscription filter
  ostringstream buf;
  buf << "provider = '" << filter << "'";
  CORBA::String_var sFilter = CORBA::string_dup(buf.str().c_str());
  // Filter expr
  StringSeq sSeqExpr;
  sSeqExpr.length(0);
  // create topic
  mgr->createContentFilteredTopic(sTopicName, sFilter.in(), sSeqExpr);
  // create Filtered DataReader
  cout << "=== [EventElcanoFilterSubscriber] Subscription filter : "
       << sFilter << endl;
  mgr->createReader(true);

  DataReader_ptr dreader = mgr->getReader();
  LocEventDataReader_var EventElcanoFilterReader =
    LocEventDataReader::_narrow(dreader);
  checkHandle(EventElcanoFilterReader, "LocEventDataReader::_narrow");

  cout << "=== [EventElcanoFilterSubscriber] Ready ..." << endl;

  bool closed = false;
  ReturnCode_t status =  - 1;
  int count = 0;
  while (!closed && count < 1500)
  {
    status = EventElcanoFilterReader->take(msgList, infoSeq, LENGTH_UNLIMITED,
      ANY_SAMPLE_STATE, ANY_VIEW_STATE, ANY_INSTANCE_STATE);
    checkStatus(status, "EventElcanoFilterDataReader::take");
    for (CORBA::ULong i = 0; i < msgList.length(); i++)
    {
       if(infoSeq[i].valid_data)
         {
           if (msgList[i].time ==  - 1)
             {
               closed = true;
               break;
             }
         }
       cout << "\n=== [EventElcanoFilterSubscriber] Event received :"
            << endl;
       cout << "    Provider : " << msgList[i].provider << endl;
       cout << "    MSID  : " << msgList[i].msid << endl;
       cout << "    Time : " << msgList[i].time << endl;

    }

    status = EventElcanoFilterReader->return_loan(msgList, infoSeq);
    checkStatus(status, "LocEventDataReader::return_loan");
    os_nanoSleep(delay_200ms);
    ++count;
  }

  cout << "=== [EventElcanoFilterSubscriber] Market Closed" << endl;

  //cleanup
  mgr->deleteReader(EventElcanoFilterReader.in ());
  mgr->deleteSubscriber();
  mgr->deleteFilteredTopic();
  mgr->deleteTopic();
  mgr->deleteParticipant();

  delete mgr;
  return 0;
}
