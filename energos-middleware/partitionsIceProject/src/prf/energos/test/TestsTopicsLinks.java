package prf.energos.test;

import java.util.ArrayList;
import java.util.Date;

import prf.energos.EnergosManager;

import Energos.ControlMsg;
import Energos.ControlSinkPrx;
import Energos.ControlSinkPrxHelper;
import Energos._ControlSinkDisp;
import Ice.*;
import IceStorm.AlreadySubscribed;
import IceStorm.BadQoS;
import IceStorm.NoSuchTopic;
import IceStorm.TopicExists;
import IceStorm.TopicManagerPrx;
import IceStorm.TopicManagerPrxHelper;
import IceStorm.TopicPrx;

import junit.framework.TestCase;

public class TestsTopicsLinks extends TestCase {

	public class MockControlSink extends _ControlSinkDisp {

		private ArrayList<ControlMsg> msgList;
		public MockControlSink () {
			msgList = new ArrayList<ControlMsg>();
		}
		
		@Override	
		public void event(ControlMsg msg, Current __current) {
			synchronized (msgList) {
				msgList.add(msg);
				System.out.println(msg);
				msgList.notify();	
			}
			
		}

		@Override
		public void status(ControlMsg msg, Current __current) {
			
		}

		@Override
		public ControlMsg[] getList(Current __current) {
			ControlMsg[] list = new ControlMsg[msgList.size()];

			int i = 0;
					
			for(ControlMsg msg: msgList) {
				list[i] = msg;
				i++;
			}
		
			return list;
		}
		
		public void onWait() {
			synchronized (msgList) {
				try {
					msgList.wait();
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
		}
	}
	
	public class Subscriber {
		private ObjectPrx proxy;
		public Subscriber(ObjectAdapter adapter) {
			MockControlSink servant = new MockControlSink();
			proxy = adapter.addWithUUID(servant);
		}
	}

        
	private TopicManagerPrx manager;
	private ObjectAdapter adapter;
	private ControlMsg event;
	private EnergosManager energosManager;
	private String topicName;
	
	@Override
	protected void setUp() throws Exception {
		super.setUp();
		Ice.Communicator communicator = Ice.Util.initialize();
		ObjectPrx prx = communicator.stringToProxy("IceStorm/TopicManager:tcp -p 10000");
		manager = TopicManagerPrxHelper.checkedCast(prx);
		
		if(manager == null) {
            System.err.println("invalid proxy");
            return;
        }
		
		topicName = "VOLTAGE";
		
		energosManager = new EnergosManager(manager);
		event = new ControlMsg();
		event.resourceId = "EventSample";
		event.timestamp = new Date().getTime();
		event.eventType = 0;
		event.svStatus = 0;
		
		adapter = 
			communicator.createObjectAdapterWithEndpoints("Adapter", "tcp");
		
		adapter.activate();

	}
	
	@Override
	protected void tearDown() throws Exception {
		super.tearDown();
		for (TopicPrx topic: manager.retrieveAll().values()) {
			topic.destroy();
		}
	}
	
	public void test_getUniqueTopic() {
		String[] partitions = {"REAL", "INSTANT"};
		
		// topic
		TopicPrx topic = energosManager.get_topic("VOLTAGE_REAL_INSTANT");
		
		// subscriber
		MockControlSink servant = new MockControlSink();
		ObjectPrx subscriber = adapter.addWithUUID(servant);
		energosManager.subscribe_to_partition(partitions, topicName, subscriber);
		
		// publisher
		ObjectPrx publisher = topic.getPublisher();
		ControlSinkPrx sink = ControlSinkPrxHelper.uncheckedCast(publisher);
		
		// send event
		sink.event(event);
		servant.onWait();

		assertEquals(1, servant.getList().length);
		
	}
	
	public void test_getAllScopeTopics() {
		String[] partitions = {"*", "INSTANT"};
		
		// topic
		TopicPrx topic1 = energosManager.get_topic("VOLTAGE_REAL_INSTANT");
		TopicPrx topic2 = energosManager.get_topic("VOLTAGE_SIMULATED_INSTANT");
		TopicPrx topic3 = energosManager.get_topic("VOLTAGE_SIMULATED_HOURLY");
		
		
		// subscriber
		MockControlSink servant = new MockControlSink();
		ObjectPrx subscriber = adapter.addWithUUID(servant);
		energosManager.subscribe_to_partition(partitions, topicName, subscriber);

		// publishers
		ObjectPrx publisher1 = topic1.getPublisher();
		ControlSinkPrx sink1 = ControlSinkPrxHelper.uncheckedCast(publisher1);
		ObjectPrx publisher2 = topic2.getPublisher();
		ControlSinkPrx sink2 = ControlSinkPrxHelper.uncheckedCast(publisher2);
		ObjectPrx publisher3 = topic3.getPublisher();
		ControlSinkPrx sink3 = ControlSinkPrxHelper.uncheckedCast(publisher3);
		
		// send events
		sink1.event(event);
		servant.onWait();
		sink2.event(event);
		servant.onWait();
		sink3.event(event);

		assertEquals(2, servant.getList().length);
		
	}
	
	public void test_getAllTemporalityTopics() {
		String[] partitions = {"REAL", "*"};
		
		// topic
		TopicPrx topic1 = energosManager.get_topic("VOLTAGE_REAL_INSTANT");
		TopicPrx topic2 = energosManager.get_topic("VOLTAGE_REAL_HOURLY");
		TopicPrx topic3 = energosManager.get_topic("VOLTAGE_REAL_QUARTLY");
		TopicPrx topic4 = energosManager.get_topic("VOLTAGE_VERIFIED_HOURLY");
		
		// subscriber
		MockControlSink servant = new MockControlSink();
		ObjectPrx subscriber = adapter.addWithUUID(servant);
		energosManager.subscribe_to_partition(partitions, topicName, subscriber);

		// publishers
		ObjectPrx publisher1 = topic1.getPublisher();
		ControlSinkPrx sink1 = ControlSinkPrxHelper.uncheckedCast(publisher1);
		ObjectPrx publisher2 = topic2.getPublisher();
		ControlSinkPrx sink2 = ControlSinkPrxHelper.uncheckedCast(publisher2);
		ObjectPrx publisher3 = topic3.getPublisher();
		ControlSinkPrx sink3 = ControlSinkPrxHelper.uncheckedCast(publisher3);
		ObjectPrx publisher4 = topic4.getPublisher();
		ControlSinkPrx sink4 = ControlSinkPrxHelper.uncheckedCast(publisher4);
		
		// send events
		sink1.event(event);
		servant.onWait();
		sink2.event(event);
		servant.onWait();
		sink3.event(event);
		servant.onWait();
		sink4.event(event);

		assertEquals(3, servant.getList().length);
	}
	
	public void test_getAll() {
		String[] partitions = {"*", "*"};
		
		// topic
		TopicPrx topic1 = energosManager.get_topic("VOLTAGE_REAL_INSTANT");
		TopicPrx topic2 = energosManager.get_topic("VOLTAGE_VERIFIED_HOURLY");
		TopicPrx topic3 = energosManager.get_topic("VOLTAGE_REAL_QUARTLY");
		TopicPrx topic4 = energosManager.get_topic("VOLTAGE_SIMULATED_HOURLY");
		
		// subscriber
		MockControlSink servant = new MockControlSink();
		ObjectPrx subscriber = adapter.addWithUUID(servant);
		energosManager.subscribe_to_partition(partitions, topicName, subscriber);

		// publishers
		ObjectPrx publisher1 = topic1.getPublisher();
		ControlSinkPrx sink1 = ControlSinkPrxHelper.uncheckedCast(publisher1);
		ObjectPrx publisher2 = topic2.getPublisher();
		ControlSinkPrx sink2 = ControlSinkPrxHelper.uncheckedCast(publisher2);
		ObjectPrx publisher3 = topic3.getPublisher();
		ControlSinkPrx sink3 = ControlSinkPrxHelper.uncheckedCast(publisher3);
		ObjectPrx publisher4 = topic4.getPublisher();
		ControlSinkPrx sink4 = ControlSinkPrxHelper.uncheckedCast(publisher4);
		
		// send events
		sink1.event(event);
		servant.onWait();
		sink2.event(event);
		servant.onWait();
		sink3.event(event);
		servant.onWait();
		sink4.event(event);
		servant.onWait();

		
		assertEquals(4, servant.getList().length);
	}

}
