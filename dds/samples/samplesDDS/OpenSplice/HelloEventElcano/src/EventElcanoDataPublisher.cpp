/*************************************************************************
 *                         OpenSplice DDS
 *
 *   This software and documentation are Copyright 2006 to 2009 PrismTech
 *   Limited and its licensees. All rights reserved. See file:
 *
 *                     $OSPL_HOME/LICENSE
 *
 *   for full copyright notice and license terms.
 *
 */

/************************************************************************
 * LOGICAL_NAME:    ListenerDataPublisher.cpp
 * FUNCTION:        OpenSplice Tutorial example code.
 * MODULE:          Tutorial for the C++ programming language.
 * DATE             September 2010.
 ************************************************************************
 *
 * This file contains the implementation for the 'ListenerDataPublisher' executable.
 *
 ***/
#include <string>
#include <sstream>
#include <iostream>
#include <fstream>
#include "DDSEntityManager.h"
#include "ccpp_EventElcanoData.h"
#include "os.h"

using namespace std;

using namespace DDS;
using namespace EventElcano;

int main(int argc, char *argv[])
{
  os_time delay_500ms = { 0, 500000000 };
  os_time delay_2ms = { 0, 2000000 };
  DDSEntityManager *mgr = new DDSEntityManager();

  // create domain participant
  char partition_name[] = "EventElcano example";
  mgr->createParticipant(partition_name);

  //create type
  BoxEventTypeSupport_var mt = new BoxEventTypeSupport();
  mgr->registerType(mt.in());

  //create Topic
  char topic_name[] = "EventElcanoData_Msg";
  mgr->createTopic(topic_name);

  //create Publisher
  mgr->createPublisher();

  // create DataWriter
  mgr->createWriter();

  // Publish Events
  DataWriter_ptr dwriter = mgr->getWriter();
  BoxEventDataWriter_var EventElcanoWriter =
    BoxEventDataWriter::_narrow(dwriter);

  BoxEvent msgInstance; /* Example on Stack */

  ReturnCode_t status;
  ifstream f;

  char linea[1000];
  char* aux[6];
  char* pch;

  f.open("src/samples/OpenSplice/HelloEventElcano/events/data", ios::in);

  if (!f.is_open())
    {
      cerr << "ERROR: no se puede abrir el fichero para leer" << endl;
      return -1;
    }

  while (!f.eof())
    {
      f.getline(linea, 1000);
      pch = strtok (linea," ");

      if (pch == NULL) break;

      for (int j = 0; (pch != NULL); j++)
        {
          aux[j] = pch;
          pch = strtok (NULL, " ");
        }

      msgInstance.msid = CORBA::string_dup(aux[0]);
      msgInstance.time = atol(aux[1]);
      msgInstance.provider = CORBA::string_dup(aux[2]);
      msgInstance.point.x = strtod(aux[3], NULL);
      msgInstance.point.y = strtod(aux[4], NULL);
      msgInstance.point.z = strtod(aux[5], NULL);
      cout << "\n=== [Publisher] writing a message containing :" << endl;
      cout << "    MSID  : " << msgInstance.msid << endl;
      cout << "    Time : " << msgInstance.time << endl;
      cout << "    Provider : " << msgInstance.provider << endl;
      cout << "    Point : (" << msgInstance.point.x << ", "
           << msgInstance.point.y << ", " << msgInstance.point.z << ")"
           << endl;


      status = EventElcanoWriter->write(msgInstance, NULL);
      checkStatus(status, "BoxEventDataWriter::write");
      os_nanoSleep(delay_500ms);
      os_nanoSleep(delay_500ms);
    }

  f.close();

  /* Remove the DataWriters */
  mgr->deleteWriter(EventElcanoWriter.in ());

  /* Remove the Publisher. */
  mgr->deletePublisher();

  /* Remove the Topics. */
  mgr->deleteTopic();

  /* Remove Participant. */
  mgr->deleteParticipant();

  delete mgr;
  return 0;
}
