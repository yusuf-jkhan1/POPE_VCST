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
        ##Need to figure out how to package this. Either needs to be in separate module, or parent functions
        ##need to be methods not staticmethods or needs to be defined within parent function ##Priority 3
        
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
                for destination_record in data[vin].keys():
                    field = "destination."+str(destination_record)
                    payload = {"$set":{field : data[vin][destination_record]}}
                    mycol.update_one({"_id": documentID}, payload,upsert=True)
            else:
                mycol.insert_one({"_id": documentID, "destination": data[vin]})


class ubd_mongo_handler:
    
    def __init__(self):
        pass

    
    @staticmethod
    def load(mongoConnectionURI:str="mongodb://localhost:27017", \
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