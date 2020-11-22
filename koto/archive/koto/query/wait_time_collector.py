
def wait_time_collector(response_object=[]):

    ##Write doc string #Priority 2

    if len(response_object) > 0:

        #Necessary fields
        neccesary_fields = ['vin','sequence','timestamp']

        #Check if necessary fields are available
        valid_fields = all(field in response_object[0].keys() for field in neccesary_fields)
        assert valid_fields, "Not all required fields are present in the response object"

        agg_timestamp_dict = {}
        for entry in response_object:
            seq = entry['sequence']
            ts = entry['timestamp']

            if entry['vin'] == '123b9a7bbd7775662d3a55656dc2379b':
                pass
            elif entry['vin'] in agg_timestamp_dict.keys():
                if seq not in agg_timestamp_dict[entry['vin']].keys():
                    agg_timestamp_dict[entry['vin']][seq] = [ts, None]
                elif seq in agg_timestamp_dict[entry['vin']].keys():
                    agg_timestamp_dict[entry['vin']][seq][1] = ts                        
            elif entry['vin'] not in agg_timestamp_dict.keys():
                agg_timestamp_dict[entry['vin']] = {seq : [ts, None]}
        
        print(agg_timestamp_dict)
        
    else:
        agg_timestamp_dict = {}

    return agg_timestamp_dict 