import pymongo
import pandas as pd

class mongo:

    def __init__(self, client:str, db:str, collection:str):
        self.client = pymongo.MongoClient(client)
        self.db = self.client[db]
        self.collection = self.db[collection]

    def mongo_dc_to_pd(self):
        id_list = self.collection.find().distinct("_id")
        dest_raw_df = pd.DataFrame(columns = ['seq', 'Lat', 'Lon', 'vin'])
        for vin in id_list:
            filt = {'_id': vin}
            query_response = self.collection.find_one(filt)
            temp_df = pd.DataFrame(query_response['destination']).transpose().reset_index().rename(columns = {'index':'seq',0:'Lat',1:'Lon'})
            temp_df['vin'] = query_response['_id']
            dest_raw_df = dest_raw_df.append(temp_df, ignore_index = True)
        return dest_raw_df

    def mongo_dtc_to_pd(self):
        id_list = self.collection.find().distinct("_id")
        dwell_raw_df = pd.DataFrame(columns = ['seq', 'start_timestamp', 'end_timestamp', 'vin'])
        for vin in id_list:
            filt = {'_id': vin}
            query_response = self.collection.find_one(filt)
            temp_df = pd.DataFrame(query_response['dwell']).transpose().reset_index().rename(columns = {'index':'seq',0:'Lat',1:'Lon'})
            temp_df['vin'] = query_response['_id']
            dwell_raw_df = dwell_raw_df.append(temp_df, ignore_index = True)
        return dwell_raw_df