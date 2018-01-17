#include <string>
#include <sstream>
#include <iostream>
#include <fstream>
#include "DDSEntityManager.h"
#include "ccpp_EventElcanoFilter.h"
#include "os.h"


using namespace DDS;
using namespace EventElcanoFilter;

LocEvent setDataEvent(char* data[6])
{
  LocEvent dataEvent;
  dataEvent.provider = CORBA::string_dup(data[0]);
  dataEvent.msid = CORBA::string_dup(data[1]);
  dataEvent.time = atol(data[2]);
  dataEvent.point.x = strtod(data[3], NULL);
  dataEvent.point.y = strtod(data[4], NULL);
  dataEvent.point.z = strtod(data[5], NULL);

  return dataEvent;
}
int main(int argc, char *argv[])
{

  if (argc < 2)
    {
      cerr << "Debe introducir la ruta del fichero donde se encuentran los "
        "eventos de localización" << endl;
      return -1;
    }
  os_time delay_100ms = { 0, 100000000 };
  DDSEntityManager *mgr = new DDSEntityManager();

  // create domain participant
  char partition_name[] = "EventElcanoFilterTopic example";
  mgr->createParticipant(partition_name);

  LocEventTypeSupport_var st = new LocEventTypeSupport();
  mgr->registerType(st.in());

  //create Topic
  char topic_name[] = "LocEventTrackerExclusive";
  mgr->createTopic(topic_name);

  //create Publisher
  mgr->createPublisher();

  // create DataWriter
  mgr->createWriter();
  DataWriter_ptr dWriter = mgr->getWriter();
  LocEventDataWriter_var EventElcanoFilterWriter =
    LocEventDataWriter::_narrow(dWriter);

  LocEvent event;
  LocEvent rfidEvent;
  LocEvent wifiEvent;
  LocEvent blueEvent;

  char linea[1000];
  char* aux[6];
  char* pch;
  ifstream f;

  f.open(argv[1], ios::in);

  if (!f.is_open())
    {
      cerr << "ERROR: no se puede abrir el fichero para leer" << endl;
      return -1;
    }

  InstanceHandle_t rfidHandle = NULL;
  InstanceHandle_t blueHandle = NULL;
  InstanceHandle_t wifiHandle = NULL;

  ReturnCode_t status;

  bool closed = false;
  while (!f.eof())// && !closed)
    {
      f.getline(linea, 1000);
      pch = strtok (linea," ");

      if (pch == NULL)
        {
          break;
        }

      for (int j = 0; (pch != NULL); j++)
        {
          aux[j] = pch;
          pch = strtok (NULL, " ");
        }

      event = setDataEvent(aux);

      cout << "\n=== [EventElcanoFilterPublisher] send a event :" << endl;
      cout << "    Provider : " << event.provider << endl;
      cout << "    MSID  : " << event.msid << endl;
      cout << "    Time : " << event.time << endl;

      if (strcmp(CORBA::string_dup(aux[0]),"RFID") == 0)
        {
          rfidEvent = event;
          if(rfidHandle == NULL)
            {
              rfidHandle = EventElcanoFilterWriter->
                register_instance(rfidEvent);
            }

          status = EventElcanoFilterWriter->write(rfidEvent, rfidHandle);
          checkStatus(status, "LocEventDataWriter::write");

        }

      if (strcmp(CORBA::string_dup(aux[0]),"WIFI") == 0)
        {
          wifiEvent = event;
          if(wifiHandle == NULL)
            {
              wifiHandle = EventElcanoFilterWriter->
                register_instance(wifiEvent);

            }

          status = EventElcanoFilterWriter->write(wifiEvent, wifiHandle);
          checkStatus(status, "LocEventDataWriter::write");

        }

      if (strcmp(CORBA::string_dup(aux[0]),"BLUETOOTH") == 0)
        {
          blueEvent = event;
          if(blueHandle == NULL)
            {
              blueHandle = EventElcanoFilterWriter->
                register_instance(blueEvent);

            }

          status = EventElcanoFilterWriter->write(blueEvent, blueHandle);
          checkStatus(status, "LocEventDataWriter::write");

        }
      os_nanoSleep(delay_100ms);
      os_nanoSleep(delay_100ms);
    }

  f.close();


  // signal to terminate
  rfidEvent.time =  - 1;
  wifiEvent.time =  - 1;
  blueEvent.time =  - 1;
  EventElcanoFilterWriter->write(rfidEvent, rfidHandle);
  os_nanoSleep(delay_100ms);
  EventElcanoFilterWriter->write(wifiEvent, wifiHandle);
  os_nanoSleep(delay_100ms);
  os_nanoSleep(delay_100ms);
  os_nanoSleep(delay_100ms);
  EventElcanoFilterWriter->write(blueEvent, blueHandle);
  cout << "Market Closed" << endl;

  /* Unregister the instances */
  EventElcanoFilterWriter->unregister_instance(rfidEvent, rfidHandle);
  EventElcanoFilterWriter->unregister_instance(wifiEvent, wifiHandle);
  EventElcanoFilterWriter->unregister_instance(blueEvent, blueHandle);

  /* Remove the DataWriters */
  mgr->deleteWriter(EventElcanoFilterWriter.in ());

  /* Remove the Publisher. */
  mgr->deletePublisher();

  /* Remove the Topics. */
  mgr->deleteTopic();

  /* Remove Participant. */
  mgr->deleteParticipant();

  delete mgr;
  return 0;
}
