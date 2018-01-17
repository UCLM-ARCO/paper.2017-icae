		package arco.icedds;

import android.app.Activity;
import java.util.ArrayList;

import android.app.AlertDialog;
import android.app.Dialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.Spinner;
import android.widget.TextView;
import android.view.View.OnClickListener;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.AdapterView.OnItemSelectedListener;

public class SubscribeToNewTopic extends Activity {
	final String[] filterstype = {"Equal (x == a)", "Range (in [a,b])",
			"Over (x > a) ", "Below (x < a)"};
	final String[] variables = {"x", "y", "z"};
	
	private Context context = this;
	private EditText choiceNameTopic;
	private TextView title1Values;
	private TextView title2Values;
	private EditText value1;
	private EditText value2;
	ListView subscribeFilters;
	
	private String choiceFilter;
	private String variable;
	private int choiceRemoveFilter;
	
	private ArrayList<String> filtersNamesList = new ArrayList<String>();
	private ArrayAdapter<String> adapterFilterList;
	
	/* Dialog to subscribe */
	private Dialog dialogSubscribeNewTopic;
	
	@Override
	public void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.transparent);
		
		filtersNamesList.clear();
		
		dialogSubscribeNewTopic = new Dialog(this);
		dialogSubscribeNewTopic.setTitle("Subscribe to New Topic");
		dialogSubscribeNewTopic.setContentView(R.layout.createnewtopic);
		
		choiceNameTopic = (EditText) dialogSubscribeNewTopic.findViewById(R.id.textTopicName);
		
		Spinner filterTypesNewTopic = (Spinner) dialogSubscribeNewTopic.findViewById(R.id.filtertypeSpinner);
		
		Spinner variablesFilterNewTopic = (Spinner) dialogSubscribeNewTopic.findViewById(R.id.variablefilterSpinner);
		
		title1Values = (TextView) dialogSubscribeNewTopic.findViewById(R.id.description1);
		title2Values = (TextView) dialogSubscribeNewTopic.findViewById(R.id.description2);
		value1 = (EditText) dialogSubscribeNewTopic.findViewById(R.id.value);
		value2 = (EditText) dialogSubscribeNewTopic.findViewById(R.id.valueHigh);
		
		subscribeFilters = (ListView) dialogSubscribeNewTopic.findViewById(R.id.subscribeFilters);
		
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
				android.R.layout.simple_list_item_1, filtersNamesList);
		
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
						filtersNamesList.remove(choiceRemoveFilter);
						adapterFilterList = new ArrayAdapter<String>(context, 
								android.R.layout.simple_list_item_1, filtersNamesList);
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
		
		Button addFilterButton = (Button) dialogSubscribeNewTopic.findViewById(R.id.addnewFilter);

		addFilterButton.setOnClickListener(new OnClickListener() {
			@Override
			public void onClick(View v) {
				String filterName = variable + " " + choiceFilter;
				if (choiceFilter == "in") {
					filterName = filterName + " range(" + 
							value1.getText().toString() + "," + 
							value2.getText().toString() + ")";
				
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
						filtersNamesList.add(filterName);
						adapterFilterList = new ArrayAdapter<String>(context, 
							android.R.layout.simple_list_item_1, filtersNamesList);
						subscribeFilters.setAdapter(adapterFilterList);
					}
				}
			}
	
		});
		
		
		/* Buttons windows Subscribe/Cancel */
		
		Button subscribe = (Button) dialogSubscribeNewTopic.findViewById(R.id.buttonSubscribeToTopic);
	    subscribe.setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) {
				if(choiceNameTopic.getText().toString().trim().equals("")){
					showAlert("You must introduce a topic name");
				}
				else {
					dialogSubscribeNewTopic.dismiss();
					
					Intent resultIntent = new Intent();
					resultIntent.putExtra("TopicName", choiceNameTopic.getText().toString());
					resultIntent.putExtra("TopicFilters", getFiltersOfTopic());
					setResult(Activity.RESULT_OK, resultIntent);
					
					finish();
				}
			}
		});
	    
	    Button cancelSubscribeWithFilter = (Button) dialogSubscribeNewTopic.findViewById(R.id.cancelSubscribeWithFilters);
	    cancelSubscribeWithFilter.setOnClickListener(new OnClickListener() {
			
			@Override
			public void onClick(View v) {
				filtersNamesList.clear();
				dialogSubscribeNewTopic.dismiss();
				finish();
			}
		});
		
		dialogSubscribeNewTopic.show();
		
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
	
	public void showNumbersBox(int selected) {
		switch(selected){
			case 0:
				title1Values.setVisibility(1);
				title1Values.setText("Equal");
				title2Values.setVisibility(-1);
				value1.setVisibility(1);
				value2.setVisibility(-1);
				choiceFilter = "==";
				break;
			case 1:
				title1Values.setVisibility(1);
				title1Values.setText("From");
				value1.setVisibility(1);
				title2Values.setVisibility(1);
				title2Values.setText("to");
				value2.setVisibility(1);
				choiceFilter = "in";
				break;
			case 2:
				title1Values.setVisibility(1);
				title1Values.setText("Over");
				title2Values.setVisibility(-1);
				value1.setVisibility(1);
				value2.setVisibility(-1);
				choiceFilter = ">";
				break;
			case 3:
				title1Values.setVisibility(1);
				title1Values.setText("Below");
				title2Values.setVisibility(-1);
				value1.setVisibility(1);
				value2.setVisibility(-1);
				choiceFilter = "<";
				break;
				
		};
	}
	
	public String[] getFiltersOfTopic() {
		String[] filtersSet = new String[filtersNamesList.size()];
		int index = 0;
		for (String filter: filtersNamesList) {
//			DDS.Filter f = new DDS.Filter();
//			f.expression = filter;
			filtersSet[index] = filter;
			index++;
		}
		return filtersSet;
	}
}
