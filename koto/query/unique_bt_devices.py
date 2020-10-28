
def unique_bluetooth_devices(response_object=[], agg_bluetooth_dict={}):
    ##Write doc string
    assert len(response_object) > 0, "Empty list passed"
    #Necessary fields
    neccesary_fields = ['vin', 'phone_bluetoothconnection_deviceaddress']
    #Check if necessary fields are available
    valid_fields = all(field in response_object[0].keys() for field in neccesary_fields)
    assert valid_fields, "Not all required fields are present in the response object"
    ##Sort out scoping issue with agg_dict

    for entry in response_object:
        if entry['phone_bluetoothconnection_deviceaddress'] is not None:
            if entry['vin'] not in agg_bluetooth_dict.keys():
                agg_bluetooth_dict[entry['vin']] = [entry['phone_bluetoothconnection_deviceaddress']]

            elif entry['phone_bluetoothconnection_deviceaddress'] not in agg_bluetooth_dict[entry['vin']]:
                agg_bluetooth_dict[entry['vin']].append(entry['phone_bluetoothconnection_deviceaddress'])
            
            else:
                pass
        else:
            continue

    return agg_bluetooth_dict

def unique_bluetooth_devices_v2(response_object=[], data_handler:list=[]):
        """
        Objective:

            Take a response object generated by a kotoTelematics request function
            Iteratively generate a dictionary where VIN numbers are keys and an list of
            unique bluetooth device IDs are values. User data handler to store externally
        
        Parameters:
            
            :response_object(list):[]
                List of returned values from a koto request function
            :data_handler(list):[ubd_mongo_handler]
                Function passed to manage data storage and aggregation
        
        Return:

            :rtype: dictionary
            :rvalue: 
                Dictionary with keys equal to VIN numbers and values as a list of unique devices that
                were observed to be connected at least once


        """

        
        if len(response_object) > 0:

            #Necessary fields
            neccesary_fields = ['vin', 'phone_bluetoothconnection_deviceaddress']

            #Check if necessary fields are available
            valid_fields = all(field in response_object[0].keys() for field in neccesary_fields)
            assert valid_fields, "Not all required fields are present in the response object"

            ##Sort out scoping issue with agg_dict
            agg_bluetooth_dict={}
            for entry in response_object:
                if entry['phone_bluetoothconnection_deviceaddress'] is not None:
                    if entry['vin'] not in agg_bluetooth_dict.keys():
                        agg_bluetooth_dict[entry['vin']] = [entry['phone_bluetoothconnection_deviceaddress']]

                    elif entry['phone_bluetoothconnection_deviceaddress'] not in agg_bluetooth_dict[entry['vin']]:
                        agg_bluetooth_dict[entry['vin']].append(entry['phone_bluetoothconnection_deviceaddress'])
                    
                    else:
                        pass
                else:
                    continue

            #Data Handler
            if len(data_handler)>0:
                data_handler(data= agg_bluetooth_dict)
            else:
                pass
        else:
            agg_bluetooth_dict={}

        return agg_bluetooth_dict
