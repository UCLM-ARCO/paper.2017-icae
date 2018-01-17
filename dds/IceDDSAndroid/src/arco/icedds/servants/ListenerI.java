package arco.icedds.servants;

import android.util.Log;
import arco.icedds.services.ListenerService.ListenerServant;
import Event._ListenerDisp;
import Ice.Current;
import MLP.Coord;

public class ListenerI extends _ListenerDisp {
	
	private static final String TAG = "ListenerServant";
	
	@Override
	public void sendData(Coord n, Current __current) {
		// TODO Auto-generated method stub
		Log.d(TAG,"Sent Data in ListenerI");
			
	}

}
