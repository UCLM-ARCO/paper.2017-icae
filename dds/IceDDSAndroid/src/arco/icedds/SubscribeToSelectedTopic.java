package arco.icedds;

import java.util.ArrayList;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.AdapterView.OnItemSelectedListener;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.Spinner;
import android.widget.TextView;

public class SubscribeToSelectedTopic extends Activity {
	final Context context = this;
	ListView topicsListView;
	final String[] filterstype = {"Equal (x == a)", "Range (in [a,b])",
			"Over (x > a) ", "Below (x < a)"};
	final String[] variables = {"x", "y", "z"};
	
	private TextView text1;
	private TextView text2;
	private EditText value1;
	private EditText value2;
	private String choiceFilter;
	private String variable;
	
	private ArrayList<String> ownFilters = new ArrayList<String>();
	ArrayList<String> topicsList = new ArrayList<String>();
	ArrayList<String> topicsNamesList = new ArrayList<String>();
	ArrayList<String[]> topicsFiltersList = new ArrayList<String[]>();
	
	int selectTopic;
	int choiceRemoveFilter;
	
	private Dialog dialogChoiceSubscription;
	
	private String topicName;
	private String[] topicFilters;
	
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.transparent);
			
		Bundle bundle = getIntent().getExtras();
		topicName = (String) bundle.get("TopicName");
		getFiltersOfTopic((Object[]) bundle.get("TopicFilters"));
		
        dialogChoiceSubscription = new Dialog(this);
        dialogChoiceSubscription.setContentView(R.layout.subscribewithfilters);
        dialogChoiceSubscription.setTitle("Do you want to subscribe to topic '" 
        							+ topicName + "'?");
        
        setOptionsSubscribeSelected();
	}
	
	private void getFiltersOfTopic(Object[] filters) {
		int index = 0;
		topicFilters = new String[filters.length];
		for (Object filter: filters) {
			String f = (String) filter;
			topicFilters[index] = f;
			index++;
		}
		
	}
	
	private void setOptionsSubscribeSelected() {
		
		
		Button subscribeToSelected = (Button) dialogChoiceSubscription.findViewById(
				R.id.subscribeSelected);
		
		subscribeToSelected.setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) {
				Intent resultIntent = new Intent();
				resultIntent.putExtra("TopicName", topicName);
				resultIntent.putExtra("TopicFilters", topicFilters);
				setResult(Activity.RESULT_OK, resultIntent);
				
				dialogChoiceSubscription.dismiss();
				finish();
			}
		});
		
		Button subscribeWithFilters = (Button) dialogChoiceSubscription.findViewById(
				R.id.WithFilters);
		
		subscribeWithFilters.setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) {
				showDialogOwnFilters();
				dialogChoiceSubscription.dismiss();
			}
		});
		
		Button cancelSubscribeButton = (Button) dialogChoiceSubscription.findViewById(
				R.id.canceledSubscribe);
		
		cancelSubscribeButton.setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) {
				dialogChoiceSubscription.dismiss();
				finish();
			}
		});
		
		dialogChoiceSubscription.show();
	}
	
	Dialog dialogSubscribeWithFilter;
	
	ArrayAdapter<String> adapterFilterList;
	ListView subscribeFilters;
	
	@Override
	protected void onStop() {
		// TODO Auto-generated method stub
		super.onStop();
	}

	public void showDialogOwnFilters(){
		
		
		ownFilters.clear();
		
		dialogSubscribeWithFilter = new Dialog(this);
		dialogSubscribeWithFilter.setTitle("Choice Own Filters to Subscribe...");
		dialogSubscribeWithFilter.setContentView(R.layout.newfiltersinsubscribe);
				
		Spinner filterTypesNewTopic = (Spinner) dialogSubscribeWithFilter.findViewById(R.id.filtertypeSpinner);
		
		Spinner variablesFilterNewTopic = (Spinner) dialogSubscribeWithFilter.findViewById(R.id.variablefilterSpinner);
		
		text1 = (TextView) dialogSubscribeWithFilter.findViewById(R.id.description1);
		text2 = (TextView) dialogSubscribeWithFilter.findViewById(R.id.description2);
		value1 = (EditText) dialogSubscribeWithFilter.findViewById(R.id.value);
		value2 = (EditText) dialogSubscribeWithFilter.findViewById(R.id.valueHigh);
		
		subscribeFilters = (ListView) dialogSubscribeWithFilter.findViewById(R.id.subscribeFilters);
		
		/* Set objects in screen */
		
		/* Spinner Filter Types */
		ArrayAdapter<String> adapterSpinnerFilterTypes = new ArrayAdapter<String>(this,
				android.R.layout.simple_spinner_item, filterstype);
		
		adapterSpinnerFilterTypes.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
	    
	    filterTypesNewTopic.setAdapter(adapterSpinnerFilterTypes);
	    
	    /* Spinner Variables to Filter */
	    ArrayAdapter<String> adpaterSpinnerVariablesFilter = new ArrayAdapter<String>(this,
				android.R.layout.simple_spinner_item, variables);
	    adpaterSpinnerVariablesFilter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
	    
	    variablesFilterNewTopic.setAdapter(adpaterSpinnerVariablesFilter);
		
		
	    /* Handler spinners */
	    
	    filterTypesNewTopic.setOnItemSelectedListener(new OnItemSelectedListener() {

			@Override
			public void onItemSelected(AdapterView<?> arg0, View arg1,
					int arg2, long arg3) {
				showNumbersBox(arg2);
			}

			@Override
			public void onNothingSelected(AdapterView<?> arg0) {		
			}
		});
	    
	    variablesFilterNewTopic.setOnItemSelectedListener(new OnItemSelectedListener() {
	
			@Override
			public void onItemSelected(AdapterView<?> arg0, View arg1,
					int arg2, long arg3) {
				variable = variables[arg2];
			}
	
			@Override
			public void onNothingSelected(AdapterView<?> arg0) {
			}
		});
	    
	    
		/* ListView Filters */
		adapterFilterList = new ArrayAdapter<String>(this, 
				android.R.layout.simple_list_item_1, ownFilters);
		
		subscribeFilters.setAdapter(adapterFilterList);
		
		subscribeFilters.setOnItemClickListener(new OnItemClickListener() {

			@Override
			public void onItemClick(AdapterView<?> arg0, View arg1, int arg2,
					long arg3) {
				choiceRemoveFilter = arg2;
				
				AlertDialog.Builder removeFilter = new AlertDialog.Builder(context);
		        removeFilter.setMessage("Do you want to remove this filter?");
		        removeFilter.setCancelable(false);
		        
		        removeFilter.setPositiveButton("Yes", 
		        		new DialogInterface.OnClickListener() {
					@Override
					public void onClick(DialogInterface dialog, int which) {
						ownFilters.remove(choiceRemoveFilter);
						adapterFilterList = new ArrayAdapter<String>(context, 
								android.R.layout.simple_list_item_1, ownFilters);
						subscribeFilters.setAdapter(adapterFilterList);
					}
				});
		        
		        removeFilter.setNegativeButton("No", new DialogInterface.OnClickListener() {
		            public void onClick(DialogInterface d, int id) {
		                 d.cancel();
		            }
		        });
		        
				AlertDialog alert = removeFilter.create();
				alert.show();
			}
			
		});	
	    
		
		/* Button Add Filters */
		
		Button addFilterButton = (Button) dialogSubscribeWithFilter.findViewById(R.id.addnewFilter);

		addFilterButton.setOnClickListener(new OnClickListener() {
			@Override
			public void onClick(View v) {
				String filterName = variable + " " + choiceFilter;
				if (choiceFilter == "in") {
					filterName = filterName + " range(" + 
							value1.getText().toString() + "," + 
							value2.getText().toString() + ") ";
				
				}
				else {
					filterName = filterName + " " + value1.getText().toString();
				}
				
				if (value1.getText().toString().trim().equals("") || 
						value2.getText().toString().trim().equals("")) {
					showAlert("The value cannot be empty");
				}
				
				else {
					if ((choiceFilter == "in") && invalidFields()) {
						showAlert("The values of filter are invalid");
					}	
			
					else {
						ownFilters.add(filterName);
						adapterFilterList = new ArrayAdapter<String>(context, 
							android.R.layout.simple_list_item_1, ownFilters);
						subscribeFilters.setAdapter(adapterFilterList);
					}
				}
			}
	
		});
		
		
		/* Buttons windows Subscribe/Cancel */
		
		Button subscribe = (Button) dialogSubscribeWithFilter.findViewById(R.id.buttonSubscribeToTopic);
	    subscribe.setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) {
				Intent resultIntent = new Intent();
				resultIntent.putExtra("TopicName", topicName);
				resultIntent.putExtra("TopicFilters", topicFilters);
				resultIntent.putExtra("FiltersInSubscriber", getOwnFilters());
				setResult(Activity.RESULT_OK, resultIntent);
				
				dialogSubscribeWithFilter.dismiss();
					

				finish();
			}
		});
	    
	    Button cancelSubscribeWithFilter = (Button) dialogSubscribeWithFilter.findViewById(R.id.cancelSubscribeWithFilters);
	    cancelSubscribeWithFilter.setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) {
				ownFilters.clear();
				dialogSubscribeWithFilter.dismiss();
				finish();
			}
		});
		
		dialogSubscribeWithFilter.show();
		
	}
	
	public String[] getOwnFilters() {
		String[] filtersSet = new String[ownFilters.size()];
		int index = 0;
		for (String filter: ownFilters) {
//			DDS.Filter f = new DDS.Filter();
//			f.expression = filter;
			filtersSet[index] = filter;
			index++;
		}
		return filtersSet;
	}
		
	private void showAlert(String alertDescription) {
		AlertDialog.Builder invalidValues = new AlertDialog.Builder(this);
		invalidValues.setMessage(alertDescription)
		       .setCancelable(false)
		       .setPositiveButton("Ok", new DialogInterface.OnClickListener() {
		           public void onClick(DialogInterface dialog, int id) {
		        	   dialog.cancel();
		           }
		       });
		       
		AlertDialog alert = invalidValues.create();
		alert.show(); 
	}
	
	private boolean invalidFields() {
		int valueLow = Integer.parseInt(value1.getText().toString());
		int valueHigh = Integer.parseInt(value2.getText().toString());
		boolean invalid = false;
		
		if (valueLow >= valueHigh) {
			invalid = true;
		}
		return invalid;
	}
	
	private void showNumbersBox(int selected) {
		switch(selected){
			case 0:
				text1.setVisibility(1);
				text1.setText("Equal");
				text2.setVisibility(-1);
				value1.setVisibility(1);
				value2.setVisibility(-1);
				choiceFilter = "==";
				break;
			case 1:
				text1.setVisibility(1);
				text1.setText("From");
				value1.setVisibility(1);
				text2.setVisibility(1);
				text2.setText("to");
				value2.setVisibility(1);
				choiceFilter = "in";
				break;
			case 2:
				text1.setVisibility(1);
				text1.setText("Over");
				text2.setVisibility(-1);
				value1.setVisibility(1);
				value2.setVisibility(-1);
				choiceFilter = ">";
				break;
			case 3:
				text1.setVisibility(1);
				text1.setText("Below");
				text2.setVisibility(-1);
				value1.setVisibility(1);
				value2.setVisibility(-1);
				choiceFilter = "<";
				break;
				
		};
	}
}
