package arco.icedds.services;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;
import java.util.Vector;

import DDS.FilterError;
import DDS.TopicPrx;
import Event._ListenerDisp;
import Ice.Current;
import Ice.ObjectPrx;
import MLP.Coord;
import android.app.Service;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.graphics.Color;
import android.os.Binder;
import android.os.IBinder;
import android.util.Log;
import arco.icedds.services.IceCoreService.IceCoreServiceBinder;

public class ListenerService extends Service {
	private final String TAG = "ListenerService";
	private IceCoreServiceBinder _iceservice;
	
	private Ice.Communicator communicator;
	private DDS.TopicPrx topic = null;
	private Ice.ObjectPrx subscriber = null;
	private DDS.TopicManagerPrx manager = null;
	private HashMap<String, String[]> topicsNames = new HashMap<String, String[]>();
	private ArrayList<String> topicsNamesList = new ArrayList<String>();
	private ArrayList<String[]> filters = new ArrayList<String[]>();
	
	private DDS.TopicPrx topicOfSubscriber = null;
	private DDS.TopicPrx topicToSetFilters = null;
	
	private DDS.VariableTypeCode x = new DDS.VariableTypeCode("x", "double");
	private DDS.VariableTypeCode y = new DDS.VariableTypeCode("y", "double");
	private DDS.VariableTypeCode z = new DDS.VariableTypeCode("z", "double");
	
	private DDS.VariableTypeCode[] typecode = {x, y , z};
	
	public interface ListenerServant {
		public void sendData(Coord n, int color);
	}
	
	private Vector<ListenerServant> _listeners = new Vector<ListenerServant>();
	
	private ServiceConnection _serviceConn = new ServiceConnection() {
		@Override
		public void onServiceDisconnected(ComponentName arg0) {}

		@Override
		public void onServiceConnected(ComponentName arg0, IBinder binder) {
			_iceservice = (IceCoreServiceBinder) binder;
			_initialization = new InitializationThread();
			_initialization.start();
			Log.d(TAG, "(onServiceConnected) IceCoreServiceBinder");

		}
	};
	
	public class ListenerServiceBinder extends Binder {
		
		public void attach(ListenerServant listener) {
			if(_listeners.contains(listener))
				return;
			_listeners.add(listener);
			Log.d(TAG, "(ListenerServiceBinder) attach listener "+listener.toString());
		}

		public void deattach(ListenerServant listener) {
			if(!_listeners.contains(listener))
				return;
			_listeners.remove(listener);
			Log.d(TAG, "(ListenerServiceBinder) DEattach listener");
		}
		
		public void subscribeToTopic(final String topicName, final String[] topicFilters){
			Thread d = new Thread(new Runnable() {
				@Override
				public void run() {		
//					subscriber = _iceservice.add(new ListenerI());
					topic = manager.createFilteredTopic(topicName, topicFilters, typecode);
					topic.subscribeAndGetPublisher(_iceservice.add(new ListenerI()));
					Log.d(TAG, "Created Topic");
				}
			});
			d.start();
		}
		
		public DDS.TopicPrx subscribeWithFilters(final String topicName, 
										 final String[] topicFilters,
										 final String[] subscriberFilters){
			
			
			Thread d = new Thread(new Runnable() {
				@Override
				public void run() {
								
					topic = manager.createFilteredTopic(topicName, topicFilters, typecode);
					try {
						topicOfSubscriber = topic.subscribeWithFilters(_iceservice.add(new ListenerI()), subscriberFilters, typecode);
					} catch (FilterError e) {
						e.printStackTrace();
					}

					Log.d(TAG, "Created Topic");
				}
			});
			d.start();
			
			try {
				d.join();
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			
			return topicOfSubscriber;
		}
		
		public void createSubscriberWithFilters(final String[] subscriberFilters){


			Thread d = new Thread(new Runnable() {	
				@Override
				public void run() {
		
					topic = manager.retrieve("foo");
					try {
						topicToSetFilters = topic.subscribeWithFilters(sub, subscriberFilters, typecode);
					} catch (FilterError e) {
						e.printStackTrace();
					}

					Log.d(TAG, "Created Topic To Set Filters");
				}
			});
			d.start();

			try {
				d.join();
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
		
		public void setFiltersInTopic(final String[] filters) {
			Thread a = new Thread(new Runnable() {
				@Override
				public void run() {
					topicToSetFilters.setFilters(filters, typecode);
					Log.d(TAG, "Changed filters");
				}
			});
			a.start();
		}
		
		public ArrayList<String> getTopicsNamesList() {
			
			Thread a = new Thread(new Runnable() {
				@Override
				public void run() {
					topicsNamesList.clear();
					for (String nameTopic: manager.retrieveAll().keySet()) {
						topicsNamesList.add(nameTopic);
					}	
					
					
					
					
				}
			});
			a.start();		
			
			try {
				a.join();
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			
			return topicsNamesList;

		}
		
		public Map<String, String[]> getTopicsNamesList2() {
			
			Thread a = new Thread(new Runnable() {
				@Override
				public void run() {
					topicsNames.clear();
					Map<String, TopicPrx> topics = manager.retrieveAll();
					for (String nameTopic: topics.keySet()) {
				        if (!nameTopic.contains("=>")){
				        	DDS.TopicPrx t = topics.get(nameTopic);
				        	topicsNames.put(nameTopic, t.getFilters());
						}
					}	
					
				}
			});
			a.start();
			
			try {
				a.join();
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			
			return topicsNames;

		}
		
		public ArrayList<String[]> getTopicsFiltersList() {
			
			Thread a = new Thread(new Runnable() {
				@Override
				public void run() {
					filters.clear();
					for (DDS.TopicPrx topic : manager.retrieveAll().values()) {
						topic.getFilters();	
						filters.add(topic.getFilters());
					}
				}
			});
			a.start();
			
			try {
				a.join();
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
			
			return filters;			
		}

		public void setFilters(final DDS.TopicPrx topic, final String[] filters) {
			Thread a = new Thread(new Runnable() {
				@Override
				public void run() {
					topic.setFilters(filters, typecode);
				}
			});
			a.start();
		}
	}
	
	private ListenerServiceBinder _binder = new ListenerServiceBinder();
	
	public class ListenerI extends _ListenerDisp {
		
		private static final String TAG = "ListenerServant";
		private int color;
		
		public ListenerI() {
//			this.color = Color.rgb(new Random().nextInt(256)*2, 
//					new Random().nextInt(256)*5,new Random().nextInt(256)*20);
			int selectedColor = new Random().nextInt(colors.size());
			this.color = colors.get(selectedColor);
			colors.remove(selectedColor);
//			if (colors.size() == 0)
//				createColors();
			
		}
		@Override
		public void sendData(Coord n, Current __current) {
			// TODO Auto-generated method stub
			Log.d(TAG,"Sent Data in ListenerService");
			for(ListenerServant listener: _listeners){
				listener.sendData(n, this.color);
			}
		}

	}

	private ArrayList<Integer> colors =  new ArrayList<Integer>();
	
	private void initializeServant(){
		_iceservice.createObjectAdapter("IceDDSSubscriber.Adapter", 
				8000); 
//		subscriber = _iceservice.add(new ListenerI());
		sub = _iceservice.add(subscribedToSetFilters);
		
	}
	private ObjectPrx sub;
	private void initializeTopicManager() {
		String strprx = "IceDDS/TopicManager -t:tcp -h 161.67.106.65 -p 3000";
		communicator = _iceservice.communicator();
		Ice.ObjectPrx base = communicator.stringToProxy(strprx);
		manager = DDS.TopicManagerPrxHelper.checkedCast(base);
		subscribedToSetFilters = new ListenerI(); 
	}
	
	private class InitializationThread extends Thread {
		public void run() {
			initializeTopicManager();
			initializeServant();
		}
	}
	
	private static InitializationThread _initialization;
	private ListenerI subscribedToSetFilters;
	
	@Override
	public void onCreate() {
		// TODO Auto-generated method stub
		super.onCreate();
		Intent intent = new Intent(this, IceCoreService.class);
		bindService(intent, _serviceConn, 
				Context.BIND_AUTO_CREATE);

		createColors();
		
	}
	
	public void createColors(){
		colors.add(Color.BLACK);
		colors.add(Color.BLUE);
//		colors.add(Color.CYAN);
//		colors.add(Color.GRAY);
//		colors.add(Color.GREEN);
//		colors.add(Color.MAGENTA);
		colors.add(Color.RED);
		colors.add(Color.WHITE);
//		colors.add(Color.YELLOW);
	}
	
	@Override
	public IBinder onBind(Intent intent) {
		// TODO Auto-generated method stub
		return _binder;
	}
	
	@Override
	public void onDestroy(){
		super.onDestroy();
//		topic.unsubscribe(subscriber);
		Log.d(TAG, "ListenerService on Destroy");
		unbindService(_serviceConn);
	}
}
