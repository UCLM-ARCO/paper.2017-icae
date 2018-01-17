package arco.icedds.services;
import Ice.ObjectPrx;
import android.app.Service;
import android.content.Intent;
import android.os.Binder;
import android.os.IBinder;
import android.util.Log;
import arco.icedds.servants.ListenerI;


public class IceCoreService extends Service {

	private static final String TAG = "IceCoreService";

	private static Ice.Communicator _communicator = null;
	private static Ice.ObjectAdapter _adapter = null;

	public class IceCoreServiceBinder extends Binder {

		public void shutdown(){
			destroy();
		}
		
		public void restart(){
			_communicator = Ice.Util.initialize();
			Log.d(TAG, "(restart) re-initialize communicator");
		}
		
		public Ice.Communicator communicator(){
			initializeCommunicator();
			return _communicator;
		}
		
		public Ice.ObjectAdapter createObjectAdapter(String name, int port){
			if (_adapter == null)
				return createObjectAdapterFromName(name, port);

			return _adapter;
		}
		
		public Ice.ObjectPrx add(arco.icedds.services.ListenerService.ListenerI listener) {
			Ice.ObjectPrx subscriber = _adapter.addWithUUID(listener);
			Log.d(TAG, "Activated adapter");
			return subscriber;
		}

	}

	private IceCoreServiceBinder _binder = new IceCoreServiceBinder();

	private void initializeCommunicator() {
		if (_communicator  != null)
			return;

		deleteFile("subscribed topics");
		_communicator = Ice.Util.initialize();

		Log.d(TAG, "(initializeCommunicator) communicator initialized!");
	}

	private Ice.ObjectAdapter createObjectAdapterFromName(String name, 
			int port){
		initializeCommunicator();

		if(_adapter != null)
			return _adapter;

//		_adapter = _communicator.createObjectAdapterWithEndpoints(name,
//				"tcp -p " + port);
		_adapter = _communicator.createObjectAdapterWithEndpoints(name,
				"tcp");
		_adapter.activate();

		Log.d(TAG, "(createObjectAdapter) Object adapter created (" +
			  name +" p: " + port + ")");

		return _adapter;
	}
	
	private void destroy(){
		if (_communicator != null){
			_communicator.destroy();
			Log.d(TAG, "(destroy) Communicator destroy");
		}		
	}
	
	@Override
	public void onCreate(){
		super.onCreate();
		initializeCommunicator();
		Log.d(TAG, "(onCreate)");
	}

	@Override
	public IBinder onBind(Intent intent) {
		return _binder;
	}

	@Override
	public void onDestroy(){
		super.onDestroy();
//		destroy();
		Log.d(TAG, "(onDestroy) Destroyed!");
	}


}
