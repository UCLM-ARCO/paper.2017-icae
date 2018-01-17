package energos.icedds;

import Ice.Application;

public class TopicsBuilder extends Application {

	@Override
	public int run(String[] args) {
		
		Ice.ObjectPrx base = communicator().propertyToProxy("IceDDS.TopicManager.Proxy");
		DDS.TopicManagerPrx manager = DDS.TopicManagerPrxHelper.checkedCast(base);
		
		DDS.VariableTypeCode source = new DDS.VariableTypeCode("source", "string");
		DDS.VariableTypeCode resourceId = new DDS.VariableTypeCode("resourceId", "string");
		DDS.VariableTypeCode timestamp = new DDS.VariableTypeCode("timeStamp", "long");
		DDS.VariableTypeCode eventType = new DDS.VariableTypeCode("eventType", "int");
		DDS.VariableTypeCode svStatus = new DDS.VariableTypeCode("svStatus", "int");
		DDS.VariableTypeCode eventValueQuality = new DDS.VariableTypeCode("eventValueQuality", "string");
		
		DDS.VariableTypeCode[] typecode = {source, resourceId, timestamp, eventType, svStatus};
		
		String [] filtersControlEvent = {"method:event"};
		manager.createFilteredTopic("controlTopic", typecode, 
				filtersControlEvent);
		
		manager.createTopic("generalTopic", typecode);
		
		
		String [] filtersInMethodAndData = {"method:status", "svStatus in range(3,18)"};
		manager.createFilteredTopic("statusEventTopic", typecode, 
				filtersInMethodAndData); 
				
		
		return 0;
	}
	
	public static void main (String[] args) {
		TopicsBuilder app = new TopicsBuilder();
		app.main("Topics", args);
	} // method main

}
