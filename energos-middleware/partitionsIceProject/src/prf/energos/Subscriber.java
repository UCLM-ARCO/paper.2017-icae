package prf.energos;
import Ice.*;
import IceStorm.*;
import Energos.*;

public class Subscriber extends Application {
	private EnergosManager manager;
	
    public class ControlSinkI extends _ControlSinkDisp {
  
		@Override
		public void event(ControlMsg msg, Current __current) {
			 System.out.println(msg);

		}

		@Override
		public void status(ControlMsg msg, Current __current) {
		}

		@Override
		public ControlMsg[] getList(Current __current) {
			return null;
		}
    }

    TopicPrx create_topic(String topic_name) {
        TopicPrx topic;
        try {
            topic = topicManager.retrieve(topic_name);
        } catch(NoSuchTopic e) {
            try {
                topic = topicManager.create(topic_name);
            } catch(TopicExists ex) {
                System.err.println("Temporary failure, try again.");
                return null;
            }
        }

        return topic;
    }

    public int run(String[] args) {
    	String key = "IceStorm.TopicManager.Proxy";
    	ObjectPrx prx = communicator().propertyToProxy(key);
    	topicManager = TopicManagerPrxHelper.checkedCast(prx);

    	manager = new EnergosManager(topicManager);
    	
        if(topicManager == null) {
            System.err.println("invalid proxy");
            return 1;
        }

        ControlSinkI servant = new ControlSinkI();
        ObjectAdapter adapter =
	    communicator().createObjectAdapter("SubscriberAdapter");
        ObjectPrx subscriber = adapter.addWithUUID(servant);

        String [] partitions = new String[2];
        partitions[0] = "REAL";
        partitions[1] = "*";
        
        manager.subscribe_to_partition(partitions, "VOLTAGE", subscriber);

        adapter.activate();
        shutdownOnInterrupt();
        communicator().waitForShutdown();

//        event_topic.unsubscribe(subscriber);

        return 0;
    }

    public static void main(String[] args) {
        Subscriber app = new Subscriber();
        int status = app.main("Subscriber", args);
        System.exit(status);
    }

    private TopicManagerPrx topicManager;
}
