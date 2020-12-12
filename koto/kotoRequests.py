import requests
import datetime
import time
import math
import os
import pytz
import pymongo
import pandas as pd
import plotly_express as px
import random

class kotoConnect:

    #Initialize
    def __init__(self, access_token:str=None,access_token_file:str="access_token.txt"):
        #TODO: ##Re-write to do cURL request ##Priority 5
        self.api_url = "https://gateway.api.cloud.wso2.com/t/hondaranddameri/iep/v1/query"
        if access_token:
            self.token = access_token
        else:
            assert os.path.exists(access_token_file), "Token Argument=None, File Path not found"
            with open(access_token_file, 'r') as f:
                self.token = f.read()
        self.headers = {'Authorization': 'Bearer %s' % self.token}

        self.status = requests.get("https://gateway.api.cloud.wso2.com/t/hondaranddameri/iep/v1/status",
                                   headers=self.headers)

    #Vin Table single request
    #TODO: Create VIN pagination class and move there
    def vin_table_request(self,
                          fetch_size:int=100,
                          columns:list=[]):
        """
        Return data from VIN table for Kotomatic Telematics API

        Parameters
        ----------
        fetch_size : int
            Number of records to retrieve
        columns : list
            Names of columns to select.
            Ref --> https://developer.kotomatic.io/data-products/telematics-data-documentation/

        Returns
        -------
        list
            List of dictionaries containing keys corresponding to selected columns from columns arg

        """
        #Build Request

        if len(columns) == 0:
            raise Exception("No columns selected")

        query_columns = " ".join(columns) 
        query_value = "{vin(input:{next:{fetch:"+ str(fetch_size) + "}}){" + query_columns + "}}"
        query_arg = {"query" : query_value}

        #Get and check
        response = requests.post(self.api_url,headers= self.headers, json= query_arg)
        if response.status_code >= 400:
            raise Exception("Response Code: " + str(response.status_code))

        #Unpack
        response_list = response.json()['data']['vin']

        return response_list

    #TODO: Token status checker, curl token generator

class kotoTsTableScraper:

    #Initialize
    def __init__(self,
                 cnxn_obj,
                 fetch_size:int=100,
                 start_date:str=None,
                 start_time:str="00:00:00",
                 time_window:int=5,
                 n_loops:int=5,
                 end_date:str=None,
                 end_time:str=None,
                 timestamp_correction:bool=True,
                 timezone:str="US/Eastern",
                 fmt:str="%Y-%m-%d %H:%M:%S %Z",
                 api_log_fname="apiCallLog.txt"):

        self.fetch_size = fetch_size
        self.minTs = datetime.datetime.strptime(start_date+ " "+ start_time,"%Y-%m-%d %H:%M:%S")
        self.maxTs = self.minTs + datetime.timedelta(minutes=time_window)
        self.timestamp_correction = timestamp_correction
        self.timezone = timezone
        self.fmt = fmt
        self.time_window = time_window
        self.cnxn = cnxn_obj
        self.api_log_fname = api_log_fname

        if end_date is None:
            self.n_loops = n_loops
        elif end_date is not None and end_time is not None:
            upr_bound = datetime.datetime.strptime(end_date+ " "+ end_time,"%Y-%m-%d %H:%M:%S")
            diff = upr_bound - self.minTs
            diff_mins = diff.seconds / 60
            self.n_loops = math.ceil(diff_mins / time_window)

    #Timestamp Table single request
    def ts_table_request(self,
                        cnxn,
                        fetch_size:int=100,
                        columns:list=[],
                        min_date:str=None,
                        min_time:str="00:00:00",
                        max_date:str=None,
                        max_time:str="23:59:59",
                        timestamp_correction:bool=True,
                        timezone:str="US/Eastern",
                        fmt:str="%Y-%m-%d %H:%M:%S %Z"):
        """
        Return data from timestamp table for 99P Labs Telematics API

        Parameterize call to timestamp table with date and time upper and lower bounds for response.

        Parameters
        ----------
        fetch_size : int
            Number of records to retrieve
        columns : list
            Names of columns to select.
            Ref --> https://developer.99plabs.io/data-products/telematics-data-documentation/
        min_date : str
            string of lower date bound, using format "YYYY-MM-DD"
        min_time : str
            string of lower time bound, using format "HH:MM:SS"
        max_date : str
            string of upper date bound, using format "YYYY-MM-DD"
        max_time : str
            string of upper time bound, using format "HH:MM:SS"
        timestamp_correction : bool
            Boolean to indicate if timestamp should be reformatted in output
        timezone : "US/Eastern"
            string of valid pytz module timezone
            Ref --> See pytz.all_timezones attribute
        fmt : str
            string for formatting timestamp using .strftime() method
            
        Returns
        -------
        list
            List of dictionaries containing keys corresponding to selected columns from columns arg

        Note
        ----
            The timestamp conversion and timezone correction only handles instances of one timezone, if data is being
            collected from multiple timezones at once it's best to set the timezone correction to UTC, then handle
            the timezone correction separately if needed.
        """

        #Build Request

        if len(columns) == 0:
            raise Exception("No colums selected")

        if "timestamp" in columns:
            pass
        else:
            columns.append("timestamp")
        query_columns = " ".join(columns)

        ##Write assertion for valid date and time format #Priority 4
        minTs = "minTs: \""+ min_date +"T"+ min_time+ ".000Z"+ "\" "
        maxTs = "maxTs: \""+ max_date +"T"+ max_time+ ".000Z"+ "\" "

        #Build payload
        query_val = "{ts(input:{"+ minTs + maxTs + "next:{fetch:"+ str(fetch_size)+ "}}){"+ query_columns+ "}}"
        query_arg = {"query" : query_val}

        #Get and check
        n_tries = 0
        while n_tries <= 3:
            response = requests.post(cnxn.api_url,headers= cnxn.headers, json= query_arg)
            if response.status_code < 400:
                break
            else:
                time.sleep(60)
                n_tries+=1

        if response.status_code >= 400:
            raise Exception("Response Code: " + str(response.status_code))

        #Unpack
        response_list = response.json()['data']['ts']

        #Timestamp Corrector 
        if timestamp_correction:
            ts_corrector = lambda x: datetime.datetime.fromtimestamp(x/1000).astimezone(pytz.timezone(timezone)).strftime(fmt)

            timestamp_corrected_list = [ts_corrector(x['timestamp']) for x in response_list]

            for i in range(len(timestamp_corrected_list)):
                response_list[i]['timestamp'] = timestamp_corrected_list[i]

        return response_list

    def _set_timebounds(self):
        """Splits min and max timestamp into string dates and returns

        """

        min_time = str(self.minTs.time().strftime("%H:%M:%S"))
        max_time = str(self.maxTs.time().strftime("%H:%M:%S"))

        return min_time, max_time

    def _set_datebounds(self):
        """Splits min and max timestamp into string dates and returns

        """

        min_date = str(self.minTs.date().strftime("%Y-%m-%d"))
        max_date = str(self.maxTs.date().strftime("%Y-%m-%d"))

        return min_date, max_date

    def _update_timebounds(self):
        """Updates timebounds to post to API for looping 

        Used by run_table_scraper method

        """

        self.minTs = self.minTs + datetime.timedelta(seconds=self.time_window*60)
        self.maxTs = self.maxTs + datetime.timedelta(seconds=self.time_window*60)
        print(f"minTs: {self.minTs}")
        print(f"maxTs: {self.maxTs}")
    
    def _log_api_call(self, start_time, end_time, run_time, n_columns, i, response):
        """Creates log file in workspace keeping track of API request parameters and response times
        
        """
        api_log = "\n"+"; At: "+ str(start_time)+ "; Called: "+ str(self.fetch_size)+ "; For N columns: "+ str(n_columns)+\
            "; ReturnTime: "+ str(run_time)+ "; Return volume: "+ str(len(response))+ "\n"\
            +"; Window: "+str(self.minTs)+" to "+str(self.maxTs)+"; Loop "+ str(i) +"/"+str(self.n_loops)+"\n"
        
        with open(self.api_log_fname, "a") as f:
            f.write(api_log)

    #Timestamp Table Scraper
    def run_table_scraper(self, columns, query_function, data_handler, with_logs:bool=True):
        """
        Iteratively fetch data from the timestamp table for a rolling time window

        This method will touch every record of the data, assuming the fetch size and
        and the return size are compatible. When they are incompatible there will be further handling.
        This will allow the user to add custom functions as an argument.
        The custom function ideally is able to work though iterative aggregation
        and updates every loop to build an output answer or intermediate data structure

        Parameters
        ----------
        columns : list
            Names of columns to select.
            Ref --> https://developer.99plabs.io/data-products/telematics-data-documentation/
            May be stored as class attribute within query_function. See kotoQuery >> destination_collector for example
        query_function :
            Class from kotoQuery module
        data_handler :
            Class from kotoDataHandler module
        with_logs : bool
            Flag for if a log of the api call and response metrics should be created in local workspace

        """
        

        for i in range(self.n_loops):

            min_time, max_time = self._set_timebounds()
            min_date, max_date = self._set_datebounds()

            start_time = datetime.datetime.now()
            response = self.ts_table_request(fetch_size=self.fetch_size,
                                             cnxn=self.cnxn,
                                             columns=columns,
                                             min_date=min_date,
                                             max_date=max_date,
                                             min_time=min_time,
                                             max_time=max_time)
            end_time = datetime.datetime.now()
            run_time = end_time - start_time

            if with_logs:
                self._log_api_call(start_time, end_time, run_time, len(columns), i, response)

            self._update_timebounds()

            query_output = query_function.query(response) #from kotoQuery
            handler = data_handler() #from kotoDataHandler
            handler.load(data=query_output)        