package arco.icedds;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.StreamCorruptedException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Map;
import java.util.Set;

import org.mapsforge.android.maps.ArrayCircleOverlay;
import org.mapsforge.android.maps.GeoPoint;
import org.mapsforge.android.maps.MapActivity;
import org.mapsforge.android.maps.MapView;
import org.mapsforge.android.maps.OverlayCircle;

import MLP.Coord;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.graphics.Color;
import android.graphics.Paint;
import android.os.Bundle;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.View.OnTouchListener;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;
import arco.icedds.services.ListenerService;
import arco.icedds.services.ListenerService.ListenerServant;
import arco.icedds.services.ListenerService.ListenerServiceBinder;


public class DDSEventsActivity extends MapActivity {
	private final String TAG = "IceDDSApplication";
	
	protected ListenerServiceBinder _connect;
	private static Handler _handler;
	
	private MapView mapView;
	
	private ArrayCircleOverlay circleOverlay;
	
	protected ArrayList<String> topicsNamesList = new ArrayList<String>(); 
	protected ArrayList<String[]> topicsFiltersList = new ArrayList<String[]>(); 
	
	private Paint circleDefaultPaintFill = new Paint(Paint.ANTI_ALIAS_FLAG);
	private Paint circleDefaultPaintOutline = new Paint(Paint.ANTI_ALIAS_FLAG);
	
	public class ListenerServantI implements ListenerServant {

		@Override
		public void sendData(Coord n, int color) {
			// TODO Auto-generated method stub
			Log.d(TAG, "Received Data (" + n.x + "," + n.y + "," + n.z + ")");
			Message msg = new Message();
            msg.obj = n;
            msg.arg1 = color;
            _handler.sendMessage(msg);
		}
		
	}

	private ListenerServantI _listener = new ListenerServantI();
	
	private ServiceConnection _serviceConn = new ServiceConnection() {
		@Override
		public void onServiceDisconnected(ComponentName arg0) {}

		@Override
		public void onServiceConnected(ComponentName arg0, IBinder binder) {
			_connect = (ListenerServiceBinder) binder;
			_connect.attach(_listener);

			Log.d(TAG, "(onServiceConnected) Attached to ListenerServant");
			Log.d(TAG, "(onServiceConnected) ListenerServiceBinder");

		}
	};
	
	static final int MIN_DISTANCE = 100;

	private LinearLayout viewList;
	private Button hideShowButton;
	private TextView hideShowText;
	private boolean isShowedTopicsList = false;
	
	private ListView topicsListView;
	private ArrayList<String> topicsList = new ArrayList<String>();
	
	private ListView subscribedTopicsListView;
	private ArrayList<String> subscribedTopicsList = new ArrayList<String>();
	
	private boolean showListFirst = false;
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_map);

		mapView = (MapView) findViewById(R.id.mapView);
		
		mapView.setClickable(true);
		mapView.setBuiltInZoomControls(true);
		mapView.setMapFile("/sdcard/esiplantabaja.map");
		mapView.setZoomMax((byte) 13);
		mapView.setZoomMin((byte) 11);
        
		_handler = new Handler(){
        	@Override
        	public void handleMessage(Message msg) {
        		Coord n = (Coord) msg.obj;
        		int color = msg.arg1;
        		
        		paintPosition(n, color);
        	}

		
        };  
        
        mapView.setOnTouchListener(new OnTouchListener() {
			
			@Override
			public boolean onTouch(View v, MotionEvent event) {
				switch(event.getAction()){
		        	case MotionEvent.ACTION_UP: {
		        		if (showListFirst){
//////		        			Toast.makeText(getApplicationContext(), "Hola Up", Toast.LENGTH_SHORT).show();
		        			_connect.setFiltersInTopic(calculateArea());
		        			subscribedTopicsList.set(0, "'foo': All events \n--> Own Filters: " + 
		                         getStringFilters(calculateArea()));
		        			subscribedTopicsListView.setAdapter(new ArrayAdapter<String>(getApplicationContext(), 
		                  		R.layout.mylist, subscribedTopicsList));
		        			setAdapterSubscribedTopicsList();
		        			refreshTopicsList();
		        			break;
		        		}
		        	}
				}
				return false;
			}
		});
        
		circleDefaultPaintFill.setStyle(Paint.Style.FILL);
		circleDefaultPaintFill.setColor(Color.RED);
		circleDefaultPaintFill.setAlpha(100);

		circleDefaultPaintOutline.setStyle(Paint.Style.STROKE);
		circleDefaultPaintOutline.setColor(Color.BLUE);
		circleDefaultPaintOutline.setAlpha(128);
		circleDefaultPaintOutline.setStrokeWidth(20);
		
        circleOverlay = new ArrayCircleOverlay(circleDefaultPaintFill,
				circleDefaultPaintOutline, this);
		
        
        viewList = (LinearLayout) findViewById(R.id.viewList);
        viewList.setVisibility(-1);
        
        hideShowText = (TextView) findViewById(R.id.textHideShowTopicsLists);
        
        
        topicsListView = (ListView) findViewById(R.id.topicsListView);
        subscribedTopicsListView = (ListView) findViewById(R.id.subcribedTopicsListView);
        
        topicsListView.setAdapter(new ArrayAdapter<String>(this, 
          		R.layout.mylist, topicsList));
        subscribedTopicsListView.setAdapter(new ArrayAdapter<String>(this, 
          		R.layout.mylist, subscribedTopicsList));
        
        topicsListView.setOnItemClickListener(new OnItemClickListener() {

			@Override
			public void onItemClick(AdapterView<?> arg0, View arg1, int option,
					long arg3) {
				Intent intent = new Intent(getApplicationContext(), 
						SubscribeToSelectedTopic.class);
				intent.putExtra("TopicName", topicsNamesList.get(option));
				intent.putExtra("TopicFilters", topicsFiltersList.get(option));
				startActivityForResult(intent, 1);
			}
		});
        
        hideShowButton = (Button) findViewById(R.id.hideShowTopicsList);
        hideShowButton.setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) {
				if (!isShowedTopicsList) {
					viewList.setVisibility(1);	
					hideShowButton.setBackgroundResource(R.drawable.hide_button_config);
					hideShowText.setText("Hide Topics List");
					isShowedTopicsList = true;
					
					refreshTopicsList();
					readFile();
				}
				else {
					viewList.setVisibility(-1);	
					hideShowButton.setBackgroundResource(R.drawable.show_button_config);
					hideShowText.setText("Show Topics List");
					isShowedTopicsList = false;
				}
			}
		});
        
        Button subscribeNewTopic = (Button) findViewById(R.id.buttonSubscribeNewTopic);
        
        subscribeNewTopic.setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) {
				Intent intent = new Intent(getApplicationContext(), 
						SubscribeToNewTopic.class);
				startActivityForResult(intent, 1);
			}
		});
        
        Button refresh = (Button) findViewById(R.id.buttonRefresh);
        refresh.setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) {
				refreshTopicsList();
			}
		});

	}
	
	private void readFile() {
		try {
			FileInputStream file = openFileInput("subscribedTopics");
			ObjectInputStream ois = new ObjectInputStream(file);
			ArrayList<String> subscribedList= (ArrayList<String>) ois.readObject();
			for (String topic: subscribedList) {
				String nameTopic = topic.split(" ")[0].substring(1, topic.split(" ")[0].length()-2);
				if(_connect.getTopicsNamesList().contains(nameTopic) &&
						!subscribedTopicsList.contains(topic)){
					subscribedTopicsList.add(topic);
				}
			}
			setAdapterSubscribedTopicsList();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (StreamCorruptedException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (ClassNotFoundException e) {
			e.printStackTrace();
		}
	}
	
	private void setAdapterSubscribedTopicsList() {
//		Collections.sort(subscribedTopicsList);
		subscribedTopicsListView.setAdapter(new ArrayAdapter<String>(
				getApplicationContext(), R.layout.mylist, 
          		subscribedTopicsList));
	}
	
	private void refreshTopicsList() {
		getArraysTopics();
		getStringTopics();
//		Collections.sort(topicsList);
		topicsListView.setAdapter(new ArrayAdapter<String>(
				this, 
          		R.layout.mylist, 
          		topicsList));
		refreshSubscribedTopicsList();
		
		// Create canal para setFilters
		if (!showListFirst) {
			showListFirst = true;
			_connect.createSubscriberWithFilters(calculateArea());
			subscribedTopicsList.clear();
			subscribedTopicsList.add("'foo': All events \n--> Own Filters: " + 
                    getStringFilters(calculateArea()));
		}
		
	}
	
	private String[] calculateArea() {
		int zoomLevel = mapView.getZoomLevel();
		Log.d(TAG, String.valueOf(zoomLevel));
		double centerY = mapView.getMapCenter().getLatitude();
		double centerX = mapView.getMapCenter().getLongitude();
		Log.d(TAG, String.valueOf(mapView.getMapCenter().getLatitude()));
		Log.d(TAG, String.valueOf(mapView.getMapCenter().getLongitude()));
		int variableX = (int) (centerX*100);
		int variableY = (int) (centerY*100);
		
		String[] filters = new String[2];
		switch (zoomLevel) {
		case 11:
			filters[0] = "x in range(" + (variableX - 44) + "," + (variableX + 44) + ")";
			filters[1] = "y in range(" + (variableY - 22) + "," + (variableY + 22) + ")";
			break;
		case 12:
			filters[0] = "x in range(" + (variableX - 22) + "," + (variableX + 22) + ")";
			filters[1] = "y in range(" + (variableY - 12) + "," + (variableY + 12) + ")";
			break;
		case 13:
			filters[0] = "x in range(" + (variableX - 11) + "," + (variableX + 11) + ")";
			filters[1] = "y in range(" + (variableY - 6) + "," + (variableY + 6) + ")";
			break;
			
		default:
			break;
		}
		Log.d(TAG, filters[0] + " " + filters[1]);
		return filters;
	}
	
	private void refreshSubscribedTopicsList() {
		ArrayList<String> subscribedTopicsListRenew = new ArrayList<String>();
		for (String topic: subscribedTopicsList) {
			String nameTopic = topic.split(" ")[0].substring(1,topic.split(" ")[0].length()-2);
			if (_connect.getTopicsNamesList().contains(nameTopic)){
				subscribedTopicsListRenew.add(topic);
			}
		}
		subscribedTopicsList = subscribedTopicsListRenew;
		setAdapterSubscribedTopicsList();
	}
	
	private ArrayList<String> getArrayNames(Set<String> s) {
		ArrayList<String> aux = new ArrayList<String>();
		for (String name: s) {
			aux.add(name);
		}
		return aux;
	}
	
	private ArrayList<String[]> getArrayFilters(Collection<String[]> s) {
		ArrayList<String[]> aux = new ArrayList<String[]>();
		for (String[] name: s) {
			aux.add(name);
		}
		return aux;
	}
	
	private void getArraysTopics() {
		Map<String, String[]> d = _connect.getTopicsNamesList2();
	 	topicsNamesList = getArrayNames(d.keySet());
	 	topicsFiltersList = getArrayFilters(d.values());
	}
	
	private void getStringTopics() {
		String topicName;
		int index;
		topicsList.clear();
		for (String[] filters : topicsFiltersList) {
			index = topicsFiltersList.indexOf(filters);
			topicName = "'" + topicsNamesList.get(index) + "'";
			String expression = "";
			for (String filter: filters) {
				String aux = filter;
				expression = expression + "\n{" + aux + "} ";		
			}
			if (expression.equals("")) {
				expression = topicName + ": All events";
			}
			else{
				expression = topicName + ": " + expression;
			}
			if (!topicsList.contains(expression)){
				topicsList.add(expression);
			}
		}
	}
	private ArrayList<Paint> cambiaColor(int colorListener){
		circleDefaultPaintOutline.setStyle(Paint.Style.STROKE);
		circleDefaultPaintOutline.setColor(colorListener);
		circleDefaultPaintOutline.setAlpha(128);
		circleDefaultPaintOutline.setStrokeWidth(20);
		
		ArrayList<Paint> paints = new ArrayList<Paint>();
		paints.add(circleDefaultPaintFill);
		paints.add(circleDefaultPaintOutline);
		
		return paints;
		
	}
	
	private void paintPosition(MLP.Coord n, int color) {
		GeoPoint userPoint = new GeoPoint(n.y/100, n.x/100);
		
		ArrayList<Paint> paints= cambiaColor(color);
		OverlayCircle circle = new OverlayCircle(userPoint, 300, null);
		circle.setPaint(paints.get(0), paints.get(1));
		circleOverlay.clear();
		circleOverlay.addCircle(circle);

		mapView.getOverlays().add(circleOverlay);
	}
	
	protected void subscribeToTopic(String topicName, String[] topicFilters) {
		_connect.subscribeToTopic(topicName, topicFilters);
	}
	private DDS.TopicPrx topicOfSubscriber = null;
	
	protected void subscribeWithFilters(String topicName, String[] topicFilters, 
			String[] subscriberFilters) {
		topicOfSubscriber = _connect.subscribeWithFilters(topicName, topicFilters, subscriberFilters);
	}
	
	private void setFilter(String [] filters) {
		_connect.setFilters(topicOfSubscriber, filters);
//		topicOfSubscriber.setFilters(filters, eventTypecode);
	}
	
	@Override
	public void onResume() {
		super.onResume();
		Intent intent = new Intent(this, ListenerService.class);
		bindService(intent, _serviceConn, 
				Context.BIND_AUTO_CREATE);
	}
	
	@Override
	public void onActivityResult(int requestCode,int resultCode, Intent data)
	{
		super.onActivityResult(requestCode, resultCode, data);
		Log.d(TAG, "onActivityResult");
		if (data != null) {
			Bundle b = data.getExtras();
			if (b != null) {
				String topicName = b.getString("TopicName");
				Object[] topicFilters = (Object[]) b.get("TopicFilters"); 
				Object[] filtersInSubscriber = (Object[]) b.get("FiltersInSubscriber");
				
				String[] filters = new String[topicFilters.length];
				int index = 0;
				for (Object filter: topicFilters) {
					filters[index] = (String) filter;
					index++;
				}
				if (filtersInSubscriber != null) {
					String[] subFilters = new String[filtersInSubscriber.length];
					index = 0;
					for (Object filter: filtersInSubscriber) {
						subFilters[index] = (String) filter;
						index++;
					}
					
					subscribeWithFilters(topicName, filters, subFilters);
					setSubscribedTopicsList(topicName, filters, subFilters);
				}
				else {
					
					subscribeToTopic(topicName, filters);
					setSubscribedTopicsList(topicName, filters, null);
				}
				
			}
		}
		refreshTopicsList();
	}
	
	private void setSubscribedTopicsList(String topicName, String[] filters, 
			String[] subFilters) {
		if (!subscribedTopicsList.contains(topicName)) {
			String f = getStringFilters(filters);
			if (f=="")
				f = "All events";
			
			String topic = "'" + topicName + "': " + f;
			if (subFilters != null) {
				String topictoSubscriber = topic + "\n--> Own Filters: " +
						getStringFilters(subFilters);
				if(!subscribedTopicsList.contains(topictoSubscriber))
					subscribedTopicsList.add(topictoSubscriber);
			}
			else {
				
				if(!subscribedTopicsList.contains(topic))
					subscribedTopicsList.add(topic);
			}

			setAdapterSubscribedTopicsList();
		}
	}
	
	public String getStringFilters(String[] filters) {
		String filterString = "";
		for (String filter : filters) {
			filterString += "{" + filter + "} ";
		}
		return filterString;
	}
	
	@Override
	public void onDestroy() {
		super.onDestroy();
		FileOutputStream fos = null;
		try {
			fos = openFileOutput("subscribedTopics", Context.MODE_PRIVATE);
			ObjectOutputStream oos = new ObjectOutputStream(fos);
			oos.writeObject(subscribedTopicsList);
			oos.close();
			Log.d(TAG, "File created");
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		unbindService(_serviceConn);

		Log.d(TAG, "(onDestroy) DDSEvents");
	}
}