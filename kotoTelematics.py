import os
print("PYTHONPATH:", os.environ.get('PYTHONPATH'))
print("PATH:", os.environ.get('PATH'))
print("PATH:", os.environ.get('PYTHONHOME'))

import sys
for p in sys.path:
    print(p)

import requests
import datetime
import time
import os
import pytz
import pymongo
import numpy
import pandas as pd
import plotly_express as px
import random

class telematics:

    #Initialize
    def __init__(self, access_token:str=None,access_token_file:str="access_token.txt"):
        ##Re-write to do cURL request ##Priority 5
        self.api_url = "https://gateway.api.cloud.wso2.com/t/hondaranddameri/iep/v1/query"
        if access_token:
            self.token = access_token
        else:
            assert os.path.exists(access_token_file), "Token Argument=None, File Path not found"
            with open(access_token_file, 'r') as f:
                self.token = f.read()
        self.headers = {'Authorization': 'Bearer %s' % self.token}

    #Vin Table single request
    def vin_table_request(self, \
                          fetch_size:int=100, \
                          columns:list=[], \
                          stream_request:bool=False, \
                          chunk_size:int=None):
        """
        Objective:

            Return data from VIN table for Kotomatic Telematics API

        Parameters:

            :fetch_size(int):100
                Number of records to retrieve
            :columns(list):[]
                Names of columns to select.
                Ref: https://developer.kotomatic.io/data-products/telematics-data-documentation/
            :stream_request(bool):False
                Boolean to indicate if request should be streamed
            :chunk_size(int):None **Building, unused right now**
                If request is streamed, chunk size will be byte size for each streamed response

        Return:

            if stream_request=False
                :rtype: list
                :rvalue: List of dictionaries containing keys corresponding to selected columns from columns arg
            if stream_request=True
                :rtype: requests module response object
                :rvalue: response object

        """
        #Build Request
        assert len(columns) > 0, "No columns selected"
        query_columns = " ".join(columns) 
        query_value = "{vin(input:{next:{fetch:"+ str(fetch_size) + "}}){" + query_columns + "}}"
        query_arg = {"query" : query_value}

        #Get and check
        response = requests.post(self.api_url,headers= self.headers, json= query_arg, stream= stream_request)
        assert response.status_code == 200, "Response Code: " + str(response.status_code)

        #Unpack
        response_list = response.json()['data']['vin']

        ##Improve or remove Streaming option
        if stream_request:
            return response
        else:
            return response_list

    #Timestamp Table single request
    def ts_table_request(self, \
                        fetch_size:int=100, \
                        columns:list=[], \
                        stream_request:bool=False, \
                        chunk_size:int=None, \
                        min_date:str=None, \
                        min_time:str="00:00:00", \
                        max_date:str=None, \
                        max_time:str="23:59:59", \
                        timestamp_correction:bool=True, \
                        timezone:str="US/Eastern", \
                        fmt:str="%Y-%m-%d %H:%M:%S %Z"):
        """
        Objective:

            Return data from Timestamp table for Kotomatic Telematics API

        Parameters:

            :fetch_size(int):100
                Number of records to retrieve
            :columns(list):[]
                Names of columns to select.
                Ref: https://developer.kotomatic.io/data-products/telematics-data-documentation/
            :stream_request(bool):False
                Boolean to indicate if request should be streamed
            :chunk_size(int):None
                If request is streamed, chunk size will be byte size for each streamed response
            :min_date(str):None
                string of lower date bound, using format "YYYY-MM-DD"
            :min_time(str):"00:00:00"
                string of lower time bound, using format "HH:MM:SS"
            :max_date(str):None
                string of upper date bound, using format "YYYY-MM-DD"
            :max_time(str):"23:59:59"
                string of upper time bound, using format "HH:MM:SS"
            :timestamp_correction(bool):True
                Boolean to indicate if timestamp should be reformatted in output
            :timezone(str):"US/Eastern"
                string of valid pytz module timezone
                Ref: See pytz.all_timezones attribute
            :fmt(str):"%Y-%m-%d %H:%M:%S %Z"
                string for formatting timestamp using .strftime() method
            
        Return:

            if stream_request=False
                :rtype: list
                :rvalue: List of dictionaries containing keys corresponding to selected columns from columns arg
            if stream_request=True
                :rtype: requests module response object
                :rvalue: response object

        """
        #Build Request
        assert len(columns) > 0, "No columns selected"
        if "timestamp" in columns:
            pass
        else:
            columns.append("timestamp")
        query_columns = " ".join(columns)


        ##Write assertion for valid date and time format
        minTs = "minTs: \""+ min_date +"T"+ min_time+ ".000Z"+ "\" "
        maxTs = "maxTs: \""+ max_date +"T"+ max_time+ ".000Z"+ "\" "

        #Build payload
        query_val = "{ts(input:{"+ minTs + maxTs + "next:{fetch:"+ str(fetch_size)+ "}}){"+ query_columns+ "}}"
        query_arg = {"query" : query_val}

        #Get and check
        n_tries = 0
        while n_tries <= 3:
            response = requests.post(self.api_url,headers= self.headers, json= query_arg, stream= stream_request)
            if response.status_code < 400:
                break
            else:
                time.sleep(60)
                n_tries+=1
        assert response.status_code < 400, "Response Code: " + str(response.status_code)

        #Unpack
        response_list = response.json()['data']['ts']

        #Timestamp Corrector 
        ##Make Timestamp corrector static class function ##Priority 5
        ##Make Timestamp corrector adjust for vehicles native timezone ##Priority 3
        if timestamp_correction:
            ts_corrector = lambda x: datetime.datetime.fromtimestamp(x/1000).astimezone(pytz.timezone(timezone)).strftime(fmt)

            timestamp_corrected_list = [ts_corrector(x['timestamp']) for x in response_list]

            for i in range(len(timestamp_corrected_list)):
                response_list[i]['timestamp'] = timestamp_corrected_list[i]

        #Return
        if stream_request:
            return response
        else:
            return response_list

    #Timestamp Table looping request 
    ##Build in handling for returnsize > fetchsize ##Priority 2
    ##Build in warnings for returnsize > fetchsize ##Priority 2
    ##Separate into two functions (or add handling) one where local workspace dictionary is output object
    ##Another where data is being stored externally e.g. MongoDB
    def ts_table_scrape(self, \
                        fetch_size:int=100, \
                        columns:list=[], \
                        stream_request:bool=False, \
                        chunk_size:int=None, \
                        start_date:str=None, \
                        start_time:str="00:00:00", \
                        time_window:int=5, \
                        n_loops:int=5, \
                        timestamp_correction:bool=True, \
                        timezone:str="US/Eastern", \
                        fmt:str="%Y-%m-%d %H:%M:%S %Z", \
                        functions:list=[], \
                        api_log:bool=True, \
                        api_log_fname:str="apiCallLog.txt", \
                        function_log:bool=True, \
                        function_log_fname:str="functionExeLog.txt"):

        """
        Objective:

            Return data from the telematics API, timestamp table for a specified window of time.
            Then, push that window of time forward and repeat for n_loops.

            ##Add below to readme
            This method will touch every record of the data, assuming the fetch size and
            and the return size are compatible. When they are incompatible there will be further handling.
            This will allow the user to add custom functions (##Maybe some standard in-built) as an argument.
            The custom function ideally is able to work though iterative aggregation
            and updates every loop to build an output answer or intermediate data structure

        Parameters:

            :fetch_size(int):100
                Number of records to retrieve
            :columns(list):[]
                Names of columns to select.
                Ref: https://developer.kotomatic.io/data-products/telematics-data-documentation/
            :stream_request(bool):False
                Boolean to indicate if request should be streamed
            :chunk_size(int):None
                If request is streamed, chunk size will be byte size for each streamed response
            :min_date(str):None
                string of lower date bound, using format "YYYY-MM-DD"
            :min_time(str):"00:00:00"
                string of lower time bound, using format "HH:MM:SS"
            :max_date(str):None
                string of upper date bound, using format "YYYY-MM-DD"
            :max_time(str):"23:59:59"
                string of upper time bound, using format "HH:MM:SS"
            :timestamp_correction(bool):True
                Boolean to indicate if timestamp should be reformatted in output
            :timezone(str):"US/Eastern"
                string of valid pytz module timezone
                Ref: See pytz.all_timezones attribute
            :fmt(str):"%Y-%m-%d %H:%M:%S %Z"
                string for formatting timestamp using .strftime() method
            
        Return:
            Per Loop:
                if stream_request=False
                    :rtype: list
                    :rvalue: List of dictionaries containing keys corresponding to selected columns from columns arg
                if stream_request=True
                    :rtype: requests module response object
                    :rvalue: response object
            Final:
                if output structure is handled locally:
                    :rtype: dictionary(s)
                    :rvalue: dictionary that custom function(s) build(s)
                if output structure is stored externally:
                    :rtype: None
                    :rvalue: None
        
        """

        minTs = datetime.datetime.strptime(start_date+ " "+ start_time,"%Y-%m-%d %H:%M:%S")
        maxTs = minTs + datetime.timedelta(minutes=time_window)
        ##Modify this to create one dictionary per function
        ##Priority 2
        #custom_store_dict_0 = {}
        ##Modify this to allow input to specify time period rather then n_loops * window size
        ##Priority 3

        for _ in range(n_loops):

            ##Modify to deal with when return size > fetch size
            min_date = str(minTs.date().strftime("%Y-%m-%d"))
            min_time = str(minTs.time().strftime("%H:%M:%S"))
            max_date = str(maxTs.date().strftime("%Y-%m-%d"))
            max_time = str(maxTs.time().strftime("%H:%M:%S"))

            start_time = datetime.datetime.now()
            response = self.ts_table_request(fetch_size=fetch_size, \
                                             columns=columns, \
                                             min_date=min_date, \
                                             max_date=max_date, \
                                             min_time=min_time, \
                                             max_time=max_time)
            end_time = datetime.datetime.now()
            run_time = end_time - start_time

            #Log API Call
            api_log = "\n"+"At: "+ str(start_time)+ ";Called: "+ str(fetch_size)+ ";For N columns: "+ str(len(columns))+";ReturnTime: "+ str(run_time)+ ";Return volume: "+ str(len(response))+ "\n"\
                +"Window: "+min_date+" "+min_time+" to "+max_date+" "+max_time+"; Loop "+ str(_) +"/"+str(n_loops)
            with open(api_log_fname, "a") as f:
                f.write(api_log)

            #Update slice
            minTs = minTs + datetime.timedelta(seconds=time_window*60)
            maxTs = maxTs + datetime.timedelta(seconds=time_window*60)

            #Execute functions from function list argument
            start_time = datetime.datetime.now()
            custom_function_0 = functions[0]
            custom_return_0 = custom_function_0(response)
            end_time = datetime.datetime.now()
            run_time = end_time - start_time

            #Log Function Execution
            function_log = "At: "+ str(start_time)+ ";N: "+ str(len(response))+";ElapsedTime: "+ str(run_time)+ "\n"
            with open(function_log_fname, "a") as f:
                f.write(function_log)


        return custom_return_0


    @staticmethod
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

    @staticmethod
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


    @staticmethod
    def location_collector_v2(response_object=[]):
        
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
            lc_mongo_handler(data=agg_loc_dict)
        else:
            agg_loc_dict = {}
            
        return agg_loc_dict


    @staticmethod
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

    ##Create function to collect vin as document id and destinations from navi as values in array
    @staticmethod
    def destination_collector(response_object=[], data_handler=[]):

        ##Write doc string #Priority 2

        if len(response_object) > 0:

            #Necessary fields
            neccesary_fields = ['vin', 'navi_destination_destination_latitude', 'navi_destination_destination_longitude']

            #Check if necessary fields are available
            valid_fields = all(field in response_object[0].keys() for field in neccesary_fields)
            assert valid_fields, "Not all required fields are present in the response object"

            agg_destination_dict = {}
            for entry in response_object:
                if entry['navi_destination_destination_latitude'] is not None:
                    destination = [entry['navi_destination_destination_latitude'], \
                                   entry['navi_destination_destination_longitude'] ]

                    if entry['vin'] not in agg_destination_dict.keys():
                        agg_destination_dict[entry['vin']] = destination

                    elif destination not in agg_destination_dict[entry['vin']]:
                        agg_destination_dict[entry['vin']].append(destination)
                    else:
                        pass
                else:
                    continue

            #Data Handler
            if len(data_handler)>0:
                data_handler(data= agg_destination_dict)
            else:
                pass

        else:
            agg_destination_dict = {}

        return agg_destination_dict

    def sequence_collector(response_object=[], data_handler=[]):
    
        ##Write doc string #Priority 2

        #Necessary fields
        neccesary_fields = ['vin', 'timestamp', 'sequence']

        if len(response_object)>0:
                
                agg_seq_dict = {}
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
                lc_mongo_handler(data=agg_loc_dict)
        else:
            agg_loc_dict = {}
            

##Potentially transfer to different sub-module
def ubd_mongo_handler(mongoConnectionURI:str="mongodb://localhost:27017", \
                        dbName:str="kotomatic_db", \
                        collName:str="uniqueDevices", \
                        connectionTimeOut:int=10000, \
                        data:dict=None
                        ):
    ##Need to figure out how to package this. Either needs to be in separate module, or parent functions
    ##need to be methods not staticmethods or needs to be defined within parent function ##Priority 3
    
    ##Write doc string
    #Verify input data
    assert isinstance(data,dict), "Data must be a dictionary"
    #Validate connection to client
    try:
        myclient = pymongo.MongoClient(mongoConnectionURI, serverSelectionTimeOutMS=connectionTimeOut)
        myclient.server_info()
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(err)
    #Verify selected db exists
    assert dbName in myclient.list_database_names(), "dbName provided does not exist"
    #Select db
    mydb = myclient[dbName]
    #Verify selected collection exists
    assert collName in mydb.collection_names(), "collName provided does not exist"
    #Select collection
    mycol = mydb[collName]

    #Update collection
    for vin in data.keys():
        documentID = vin
        if vin in mycol.find().distinct("_id"):
            payload = {"$addToSet":{"devices": {"$each":data[vin]}}}
            mycol.update_one({"_id": documentID}, payload,upsert=True)
        else:
            mycol.insert_one({"_id": documentID, "devices": data[vin]})

##Potentially transfer to different sub-module
def lc_mongo_handler(mongoConnectionURI:str="mongodb://localhost:27017", \
                    dbName:str="kotomatic_db", \
                    collName:str="locationCollector", \
                    connectionTimeOut:int=10000, \
                    data:dict=None
                    ):
    ##Need to figure out how to package this. Either needs to be in separate module, or parent functions
    ##need to be methods not staticmethods or needs to be defined within parent function ##Priority 3
    
    ##Write doc string
    #Verify input data
    assert isinstance(data,dict), "Data must be a dictionary"
    #Validate connection to client
    try:
        myclient = pymongo.MongoClient(mongoConnectionURI, serverSelectionTimeOutMS=connectionTimeOut)
        myclient.server_info()
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(err)
    #Verify selected db exists
    assert dbName in myclient.list_database_names(), "dbName provided does not exist"
    #Select db
    mydb = myclient[dbName]
    #Select or Create collection
    mycol = mydb[collName]

    #Update collection
    for vin in data.keys():
        documentID = vin
        if vin in mycol.find().distinct("_id"):
            for location_record in data[vin].keys():
                field = "location."+location_record
                payload = {"$set":{field : data[vin][location_record]}}
                mycol.update_one({"_id": documentID}, payload,upsert=True)
        else:
            mycol.insert_one({"_id": documentID, "location": data[vin]})


def single_vin_viz(vin:str='070aac90eee9f2eaf444a1ccbb894df0'):

    ##Write Doc String

    #Connect to locationCollector collection
    myclient = pymongo.MongoClient("mongodb://localhost:27017")
    mydb = myclient['kotomatic_db']
    mycol = mydb["locationCollector"]

    #Create list of document ids, which are encrypted vins
    id_list = mycol.find().distinct("_id")


    if vin == 'random':
        random_index = random.randint(0,len(id_list))
        vin = id_list[random_index]
        print(vin)

    #Find Vin locationCollector document
    filt = {'_id': vin}
    found = mycol.find_one(filt)

    #Create dataframe from document
    viz_df = pd.DataFrame(found['location']).transpose().reset_index().rename(columns = {'index':'DateTime',0:'Lat',1:'Lon'})

    #Get mapbox_token
    with open("mapbox_token.txt", 'r') as f:
        mb_token = f.read()

    #Create scatter
    fig = px.scatter_mapbox(viz_df, \
        lat = "Lat", \
        lon = "Lon", \
        color_discrete_sequence=["fuchsia"], \
        hover_name="DateTime")

    fig.update_layout(mapbox_style='dark',mapbox_accesstoken = mb_token)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()


import sys