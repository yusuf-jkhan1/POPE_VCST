import datetime


class destination_collector:

    columns = ['vin', 'navigation_location_coordinate_longitude', 'navigation_location_coordinate_latitude', 'sequence']

    def __init__(self):
        pass

    @staticmethod   
    def query(response_object):

            ##Write doc string #Priority 2

            if len(response_object) == 0:

                agg_destination_dict = {}

            else:
                #Necessary fields
                neccesary_fields = ['vin', 'navigation_location_coordinate_longitude', 'navigation_location_coordinate_latitude', 'sequence']

                #Check if necessary fields are available
                valid_fields = all(field in response_object[0].keys() for field in neccesary_fields)
                assert valid_fields, "Not all required fields are present in the response object"

                agg_destination_dict = {}
                for entry in response_object:
                    seq = str(entry['sequence'])
                    lat = entry["navigation_location_coordinate_latitude"]
                    lon = entry["navigation_location_coordinate_longitude"]
                    location = [lat, lon]

                    if entry['navigation_location_coordinate_longitude'] is None:
                        continue
                    elif entry['vin'] in agg_destination_dict.keys():
                        agg_destination_dict[entry['vin']][seq] = location
                    elif entry['vin'] not in agg_destination_dict.keys():
                        payload = {seq : location}
                        agg_destination_dict[entry['vin']] = payload

            return agg_destination_dict

class dwell_time_collector:

    def __init__(self):
        pass

    @staticmethod
    def query(response_object):

        if len(response_object) == 0:

            agg_dwell_dict = {}

        else:
            #Necessary fields
            neccesary_fields = ['vin', 'timestamp', 'sequence']

            #Check if necessary fields are available
            valid_fields = all(field in response_object[0].keys() for field in neccesary_fields)
            assert valid_fields, "Not all required fields are present in the response object"

            agg_dwell_dict = {}
            for entry in response_object:
                seq = str(entry['sequence'])
                vin = entry['vin']
                ts = entry['timestamp']

                if entry['sequence'] is None:
                    continue
                elif vin not in agg_dwell_dict.keys():
                    payload = {seq : [ts, None]}
                    agg_dwell_dict[entry['vin']] = payload
                elif vin in agg_dwell_dict.keys() and seq in agg_dwell_dict[vin].keys():
                    agg_dwell_dict[vin][seq][1] = ts
                else:
                    agg_dwell_dict[vin][seq] = [ts, None]

        return agg_dwell_dict

class location_collector:

    columns = ['vin', 'navigation_location_coordinate_longitude', 'navigation_location_coordinate_latitude', 'timestamp']

    def __init__(self):
        pass

    @staticmethod
    def query(response_object):
        
        ##Write doc string
        #assert len(response_object) > 0, "Empty list passed"

        if len(response_object) == 0:
            
            agg_loc_dict = {}
        else:

            #Necessary fields
            neccesary_fields = ['vin', 'navigation_location_coordinate_longitude', 'navigation_location_coordinate_latitude', 'timestamp']

            #Check if necessary fields are available
            valid_fields = all(field in response_object[0].keys() for field in neccesary_fields)
            assert valid_fields, "Not all required fields are present in the response object"

            agg_loc_dict={}
            for entry in response_object:

                #Data reduction
                time_ymd_hm = datetime.datetime.strptime(entry['timestamp'][:-4], "%Y-%m-%d %H:%M:%S")
                ts_key = time_ymd_hm.strftime("%Y-%m-%d %H:%M")
                if time_ymd_hm.minute % 3 == 0 and entry['navigation_location_coordinate_longitude'] is not None:
                    if entry['vin'] not in agg_loc_dict.keys():
                        vin_key = entry['vin']
                        loc_value = [entry['navigation_location_coordinate_latitude'],entry['navigation_location_coordinate_longitude']]
                        agg_loc_dict[vin_key] = {ts_key: loc_value }
                    elif ts_key not in agg_loc_dict[entry['vin']].keys():
                        loc_value = [entry['navigation_location_coordinate_latitude'],entry['navigation_location_coordinate_longitude']]
                        agg_loc_dict[entry['vin']][ts_key] = loc_value
                    else:
                        continue
          
        return agg_loc_dict

class unique_bt_device_collector:

    columns = ['vin', 'phone_bluetoothconnection_deviceaddress']

    def __init__(self):
        pass
    
    @staticmethod
    def query(response_object):
        ##Write doc string
        assert len(response_object) > 0, "Empty list passed"
        #Necessary fields
        neccesary_fields = ['vin', 'phone_bluetoothconnection_deviceaddress']
        #Check if necessary fields are available
        valid_fields = all(field in response_object[0].keys() for field in neccesary_fields)
        assert valid_fields, "Not all required fields are present in the response object"
        ##Sort out scoping issue with agg_dict

        agg_bluetooth_dict = {}
        for entry in response_object:
            if entry['phone_bluetoothconnection_deviceaddress'] is not None:
                if entry['vin'] not in agg_bluetooth_dict.keys():
                    agg_bluetooth_dict[entry['vin']] = [entry['phone_bluetoothconnection_deviceaddress']]

                elif entry['phone_bluetoothconnection_deviceaddress'] not in agg_bluetooth_dict[entry['vin']]:
                    agg_bluetooth_dict[entry['vin']].append(entry['phone_bluetoothconnection_deviceaddress'])
            else:
                continue

        return agg_bluetooth_dict