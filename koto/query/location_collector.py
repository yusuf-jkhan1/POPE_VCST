import datetime

def location_collector(response_object=[], agg_loc_dict={}):
        
    ##Write doc string
    assert len(response_object) > 0, "Empty list passed"
    ##Sort out scoping issue with agg_dict
    
    for entry in response_object:

        #Is even minute? #Data reduction
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

def location_collector_v2(response_object=[], data_handler:list=[]):
        
    ##Write doc string
    #assert len(response_object) > 0, "Empty list passed"

    if len(response_object)>0:
        
        agg_loc_dict = {}
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

        #Data Handler
        data_handler(data=agg_loc_dict)
    else:
        agg_loc_dict = {}
        
    return agg_loc_dict


