package prf.energos;

import java.util.ArrayList;

import Energos.ControlSinkPrx;
import Energos.ControlSinkPrxHelper;
import Ice.ObjectPrx;
import IceStorm.AlreadySubscribed;
import IceStorm.BadQoS;
import IceStorm.LinkExists;
import IceStorm.NoSuchTopic;
import IceStorm.TopicExists;
import IceStorm.TopicManagerPrx;
import IceStorm.TopicPrx;

public class EnergosManager {

	private TopicManagerPrx manager;
	
	public EnergosManager(TopicManagerPrx manager) {
		this.manager = manager;
	}
	
	public TopicPrx get_topic(String name) {
        TopicPrx topic = null;
        try {
            topic = manager.retrieve(name);
        } catch(NoSuchTopic e) {
            try {
                topic = manager.create(name);
            } catch(TopicExists ex) {
                System.err.println("Temporary failure, try again.");
            }
        }

        return topic;
    }
	
	public void subscribe_to_partition(String [] partitions, String topic, 
			ObjectPrx subscriber) {
		String scope = null;
		String temp = null;
		String topicsPart = topic;
		
		TopicPrx topicToSubscribe = null;
		
		if (partitions.length != 0) { 
			scope = partitions[0];
			temp = partitions[1];
			
			topicsPart += "_" + scope + "_" + temp;
				
			topicToSubscribe = get_topic(topicsPart);
			try {
				topicToSubscribe.subscribeAndGetPublisher(null, subscriber);
			} catch (AlreadySubscribed e) {
				e.printStackTrace();
			} catch (BadQoS e) {
				e.printStackTrace();
			}
		}
		
		ArrayList<String> listScope = new ArrayList<String>();
		if (partitions[0] == "*") {
			listScope = get_parents("scope");
		}
		else
			listScope.add(scope);
		
		ArrayList<String> listTemp = new ArrayList<String>();
		if (partitions[1] == "*") {
			listTemp = get_parents("temporality");
		}
		else
			listTemp.add(temp);
		
		for (String scopePart: listScope) {
			for (String tempPart: listTemp) {
				TopicPrx auxtopic = get_topic(topic + "_" + scopePart + "_" + tempPart);
				if (!auxtopic.equals(topicToSubscribe)) {
					try {
						auxtopic.link(topicToSubscribe, 0);
					} catch (LinkExists e) {
						System.out.println("Link already exists");
//						e.printStackTrace();
					}
				}
			}
		}
	}
	
	public ArrayList<String> get_parents(String partition) {
		ArrayList<String> list = new ArrayList<String>();
		
		if (partition == "scope") {
			list.add("REAL");
			list.add("SIMULATED");
			list.add("VERIFIED");
		}
		else {
			if (partition == "temporality") {
				list.add("HOURLY");
				list.add("INSTANT");
				list.add("QUARTLY");
			}
				
		}
		return list;
	}

}
