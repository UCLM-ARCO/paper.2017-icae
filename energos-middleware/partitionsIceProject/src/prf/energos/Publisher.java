package prf.energos;
import Ice.*;
import IceStorm.*;
import Energos.*;
import java.util.Date;
import java.util.HashMap;
import java.util.StringTokenizer;

public class Publisher extends Application {
    public int run(String[] args) {
		String key = "IceStorm.TopicManager.Proxy";
		ObjectPrx prx = communicator().propertyToProxy(key);
		TopicManagerPrx manager = TopicManagerPrxHelper.checkedCast(prx);
	    if (manager == null) {
	    	System.err.println("invalid proxy");
	        return 1;
	    }
	    EnergosManager energos = new EnergosManager(manager);
	
        String topic_name = "VOLTAGE_REAL_INSTANT";
        TopicPrx topic;
        topic = energos.get_topic(topic_name);


        ObjectPrx publisher = topic.getPublisher().ice_oneway();
		ControlSinkPrx sink = ControlSinkPrxHelper.uncheckedCast(publisher);
	
		ControlMsg event = new ControlMsg();
		event.resourceId = "AGCAGCNIP";
		event.timestamp = new Date().getTime();
		event.eventType = 0;
		event.svStatus = 0;
	
		HashMap<String, String> ctx = new HashMap<String, String>();
		ctx.put("cost", "5");
	
		while (true) {
		    sink.event(event, ctx);
		    try {
	                System.out.println("Send Event");
			Thread.sleep(1000);
		    } catch (Exception e) {
			System.err.println(e.getMessage());
		    }
		}
    }

    public static void main(String[] args) {
        Publisher app = new Publisher();
        int status = app.main("Publisher", args);
        System.exit(status);
    }
}