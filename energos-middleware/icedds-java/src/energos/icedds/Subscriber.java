package energos.icedds;

import java.util.List;

import DDS.FilterError;
import Energos.ControlMsg;
import Ice.Application;
import Ice.Current;

public class Subscriber extends Application {
	
	@Override
	public int run(String[] args) {
		
		Ice.ObjectPrx base = communicator().propertyToProxy("IceDDS.TopicManager.Proxy");
		DDS.TopicManagerPrx manager = DDS.TopicManagerPrxHelper.checkedCast(base);
		
		Ice.ObjectAdapter adapter = communicator().createObjectAdapter("IceDDSSubscriber.Adapter");
		adapter.activate();
		
		DDS.VariableTypeCode source = new DDS.VariableTypeCode("source", "string");
		DDS.VariableTypeCode resourceId = new DDS.VariableTypeCode("resourceId", "string");
		DDS.VariableTypeCode timestamp = new DDS.VariableTypeCode("timeStamp", "long");
		DDS.VariableTypeCode eventType = new DDS.VariableTypeCode("eventType", "int");
		DDS.VariableTypeCode svStatus = new DDS.VariableTypeCode("svStatus", "int");
		DDS.VariableTypeCode eventValueQuality = new DDS.VariableTypeCode("eventValueQuality", "string");
		
		DDS.VariableTypeCode[] typecode = {source, resourceId, timestamp, eventType, svStatus};
		
		
		// Declaration subscribers
		ListenerI listener1 = new ListenerI("subscriber of controlTopic");
		Ice.ObjectPrx subscriber1 = adapter.addWithUUID(listener1);
		
		ListenerI listener2 = new ListenerI("subscriber of statusEventTopic");
		Ice.ObjectPrx subscriber2 = adapter.addWithUUID(listener2);

		ListenerI listener3 = new ListenerI("subscriber of generalTopic");
		Ice.ObjectPrx subscriber3 = adapter.addWithUUID(listener3);
		
		
		// Subscribe to topics
		
		DDS.TopicPrx controlTopic = manager.retrieve("controlTopic");
		controlTopic.subscribeAndGetPublisher(subscriber1);
		
		DDS.TopicPrx statusEventTopic = manager.retrieve("statusEventTopic");
		statusEventTopic.subscribeAndGetPublisher(subscriber2);
//		
		DDS.TopicPrx generalTopic = manager.retrieve("generalTopic");
		String [] filterinEventType = {"eventType < 7"};
		try {
			generalTopic.subscribeWithFilters(subscriber3, filterinEventType);
		} catch (FilterError e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		communicator().waitForShutdown();
		
		return 0;
	}
	
	public static void main (String[] args) {
		Subscriber app = new Subscriber();
		app.main("Subscriber", args);
	} // method main
	
	class ListenerI extends Energos._ControlSinkDisp {

		private String name;
		
		public ListenerI (String name) {
			this.name = name;
		}

		@Override
		public void event(ControlMsg msg, Current __current) {
			System.out.println("Received Data: " + msg.resourceId + " in " + name);
		}

		@Override
		public void status(ControlMsg msg, Current __current) {
			System.out.println("Received Status: " + msg.svStatus + " in " + name);
			
		}
		
	}
}