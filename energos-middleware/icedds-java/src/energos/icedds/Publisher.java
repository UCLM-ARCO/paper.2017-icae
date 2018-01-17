package energos.icedds;

import java.util.Date;
import java.util.HashMap;

import Ice.Application;

public class Publisher extends Application {

	@Override
	public int run(String[] args) {
		
		Ice.ObjectPrx base = communicator().propertyToProxy("IceDDS.TopicManager.Proxy");
		DDS.TopicManagerPrx manager = DDS.TopicManagerPrxHelper.checkedCast(base);
		
		Energos.ControlMsg data1 = new Energos.ControlMsg("111","AGCAGCNIP", 
				new Date().getTime(), 5, 8, "GOOD");
		Energos.ControlMsg data2 = new Energos.ControlMsg("123", "AGCAGCNIP", 
				new Date().getTime(), 10, 23, "REGULAR");
		
		
		// Topic 1: one filtered method (event)
		DDS.TopicPrx controlTopic = manager.retrieve("controlTopic");
		
		HashMap<String, String> ctx = new HashMap<String, String>();
		ctx.put("cost", "5");
		
		Energos.ControlSinkPrx controlPublisher = Energos.ControlSinkPrxHelper.uncheckedCast(
				controlTopic.getPublisher());
	
		// Topic 2: one filtered method (event) and filtered data (svStatus in range(3,18)
		DDS.TopicPrx statusEventTopic = manager.retrieve("statusEventTopic");
		
		Energos.ControlSinkPrx statusEventPublisher = Energos.ControlSinkPrxHelper.uncheckedCast(
				statusEventTopic.getPublisher());

		// Topic 3: filtered data (eventType < 7)
		DDS.TopicPrx generalTopic = manager.retrieve("generalTopic");
		
		Energos.ControlSinkPrx generalPublisher = Energos.ControlSinkPrxHelper.uncheckedCast(
				generalTopic.getPublisher());
		
		
		
		try {
			// publishing in controlTopic
			// --> Event right
			controlPublisher.event(data1);
			// --> Event wrong (filter in method "event"
			controlPublisher.status(data1);
		
		} catch (Ice.EncapsulationException e) {
//			e.printStackTrace();
		}	
		try {
			// publishing in statusEventTopic
			// --> Event right
			statusEventPublisher.status(data1);
			// --> Event wrong (not match with filter "svStatus in range(3,18)"
			statusEventPublisher.status(data2);
		} catch (Ice.EncapsulationException e) {
//			e.printStackTrace();
		}
//		
		try {
			// publishing in generalTopic
			generalPublisher.event(data1);
			generalPublisher.status(data2);
		} catch (Ice.EncapsulationException e) {
//			e.printStackTrace();
		}

		
		return 0;
	}
	
	public static void main (String[] args) {
		Publisher app = new Publisher();
		app.main("Publisher", args);
	} // method main

}	
