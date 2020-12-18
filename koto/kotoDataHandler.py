import pymongo


class dc_mongo_handler:
    
    def __init__(self,
                 mongoConnectionURI:str="mongodb://localhost:27017",
                 dbName:str="POPE_VCST",
                 collName:str="destinationCollector",
                 connectionTimeOut:int=10000):
        self.cnxn_string = mongoConnectionURI
        self.dbName = dbName
        self.collName = collName
        self.cnxn_timeout = connectionTimeOut

    def load(self, data:dict=None):

        #TODO: Write DocString
        assert isinstance(data,dict), "Data must be a dictionary"
        #Validate connection to client
        try:
            myclient = pymongo.MongoClient(self.cnxn_string, serverSelectionTimeOutMS=self.cnxn_timeout)
            myclient.server_info()
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print(err)
        #Verify selected db exists
        assert self.dbName in myclient.list_database_names(), "dbName provided does not exist"
        #Select db
        mydb = myclient[self.dbName]
        #Select or Create collection
        mycol = mydb[self.collName]

        #Update collection
        for vin in data.keys():
            documentID = vin
            if vin in mycol.find().distinct("_id"):
                for destination_record in data[vin].keys():
                    field = "destination."+str(destination_record)
                    payload = {"$set":{field : data[vin][destination_record]}}
                    mycol.update_one({"_id": documentID}, payload,upsert=True)
            else:
                mycol.insert_one({"_id": documentID, "destination": data[vin]})

class ubd_mongo_handler:
    
    def __init__(self,
                 mongoConnectionURI:str="mongodb://localhost:27017",
                 dbName:str="POPE_VCST",
                 collName:str="uniqueBTDevicesCollector",
                 connectionTimeOut:int=10000):
        self.cnxn_string = mongoConnectionURI
        self.dbName = dbName
        self.collName = collName
        self.cnxn_timeout = connectionTimeOut


    @staticmethod
    def load(self, data:dict=None):

        #TODO: Write Docstring
        assert isinstance(data,dict), "Data must be a dictionary"
        #Validate connection to client
        try:
            myclient = pymongo.MongoClient(self.cnxn_string, serverSelectionTimeOutMS=self.cnxn_timeout)
            myclient.server_info()
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print(err)
        #Verify selected db exists
        assert self.dbName in myclient.list_database_names(), "dbName provided does not exist"
        #Select db
        mydb = myclient[self.dbName]
        #Verify selected collection exists
        assert self.collName in mydb.collection_names(), "collName provided does not exist"
        #Select collection
        mycol = mydb[self.collName]

        #Update collection
        for vin in data.keys():
            documentID = vin
            if vin in mycol.find().distinct("_id"):
                payload = {"$addToSet":{"devices": {"$each":data[vin]}}}
                mycol.update_one({"_id": documentID}, payload,upsert=True)
            else:
                mycol.insert_one({"_id": documentID, "devices": data[vin]})

class dtc_mongo_handler:

    def __init__(self,
                 mongoConnectionURI:str="mongodb://localhost:27017",
                 dbName:str="POPE_VCST",
                 collName:str="dwellTimeCollector",
                 connectionTimeOut:int=10000):
        self.cnxn_string = mongoConnectionURI
        self.dbName = dbName
        self.collName = collName
        self.cnxn_timeout = connectionTimeOut
    
    def load(self, data:dict=None):

        #TODO: Write DocString
        ##Write doc string
        #Verify input data
        assert isinstance(data,dict), "Data must be a dictionary"
        #Validate connection to client
        try:
            myclient = pymongo.MongoClient(self.cnxn_string, serverSelectionTimeOutMS=self.cnxn_timeout)
            myclient.server_info()
        except pymongo.errors.ServerSelectionTimeoutError as err:
            print(err)
        #Verify selected db exists
        assert self.dbName in myclient.list_database_names(), "dbName provided does not exist"
        #Select db
        mydb = myclient[self.dbName]
        #Select or Create collection
        mycol = mydb[self.collName]

        #Update collection
        for vin in data.keys():
            documentID = vin
            if vin in mycol.find().distinct("_id"):
                for sequence_record in data[vin].keys():
                    field = "dwell."+str(sequence_record)
                    seq_exists = len(mycol.find_one({"_id": documentID},{field:True})['dwell']) > 0
                    if seq_exists:
                        field_position = "dwell."+str(sequence_record)+".1"
                        if data[vin][sequence_record][1] is not None:
                            payload_inner_value = data[vin][sequence_record][1]
                        else:
                            payload_inner_value = data[vin][sequence_record][0]
                        payload = {"$set":{field_position : payload_inner_value}}
                        mycol.update_one({"_id": documentID}, payload,upsert=True)
                    else:
                        field = "dwell."+str(sequence_record)
                        payload_inner_value = data[vin][sequence_record]
                        payload = {"$set": {field: payload_inner_value}}
                        mycol.update_one({"_id": documentID}, payload,upsert=True)
            else:
                mycol.insert_one({"_id": documentID, "dwell": data[vin]})