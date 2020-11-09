
import boto3
from botocore import UNSIGNED
from botocore.client import Config
import json
import sqlite3
from sqlite3 import Error


class TelematicsDao():

    #Class Attributes
    lc = "locationCollector/"
    wtc = "waitTimeCollector/"
    dc = "destinationCollector/"

    #Initialize
    def __init__(self, s3_on = True):
        self.tableName = 'data'
        self.dbName = 'telematics'
        self.s3_on = s3_on
        if (self.s3_on):
            self.s3 = boto3.client('s3', config=Config(region_name = 'us-east-1', signature_version=UNSIGNED))
            self.bucketName = 'cse6242telematics'
            self.initS3()
            print("s3 is ON")
        else :
            self.initSQL()
            print("sqllit is ON")

    def isS3On(self):
        return self.s3_on
    
    def initS3(self):
        print (" **** S3 INITIALIZED")

    #Store Wait Collector
    def putWaitCollector(self, detailsInDict):
        if (self.s3_on):
            print("***** STORING IN S3")
            self.putWaitCollectorS3(detailsInDict)
            print("***** DATA STORED IN S3 SUCCESSFULLY")
        else:
            print("***** STORING IN SQLLITE")
            self.putWaitCollectorSQL(detailsInDict)
            print("***** DATA STORED IN SQLLITE SUCCESSFULLY")

    #Retrieve Wait Collector
    def getWaitCollector(self):
        if (self.s3_on):
            print("***** STORING IN S3")
            return self.getWaitCollectorS3()
            #print("***** DATA STORED IN S3 SUCCESSFULLY")
        else:
            print("***** STORING IN S3")
            return self.getWaitCollectorSQL()
            #print("***** DATA STORED IN S3 SUCCESSFULLY")
            print("***** DATA STORED IN SQLLITE SUCCESSFULLY")

    #Store Location Collector
    def putLocationCollector(self, detailsInDict):
        if (self.s3_on):
            print("***** STORING IN S3")
            self.putLocationCollectorS3(detailsInDict)
            #print("***** DATA STORED IN S3 SUCCESSFULLY")
        else:
            print("***** STORING IN S3")
            self.putLocationCollectorSQL(detailsInDict)
            #print("***** DATA STORED IN S3 SUCCESSFULLY")
            print("***** DATA STORED IN SQLLITE SUCCESSFULLY")


    #Retrieve Location Collector
    def getLocationCollector(self):
        if (self.s3_on):
            print("***** STORING IN S3")
            return self.getLocationCollectorS3()
            #print("***** DATA STORED IN S3 SUCCESSFULLY")
        else:
            print("***** STORING IN SQLLITE")
            return self.getLocationCollectorSQL()
            #print("***** DATA STORED IN S3 SUCCESSFULLY")
            print("***** DATA STORED IN SQLLITE SUCCESSFULLY")

    #Store Destination Collector
    def putDestinationCollector(self, detailsInDict):
        if (self.s3_on):
            print("***** STORING IN S3")
            self.putDestinationCollectorS3(detailsInDict)
            #print("***** DATA STORED IN S3 SUCCESSFULLY")
        ##Create corresponding storage methods for SQlite #Priority 3
        # else:
        #     print("***** STORING IN S3")
        #     self.putDestinationCollectorSQL(detailsInDict)
        #     print("***** DATA STORED IN S3 SUCCESSFULLY")

    #Retrieve Destination Collector
    def getDestinationCollector(self):
        if (self.s3_on):
            print("***** STORING IN S3")
            return self.getDestinationCollectorS3()
            #print("***** DATA STORED IN S3 SUCCESSFULLY")
        ##Create corresponding retrieval methods for SQlite #Priority 3
        # else:
        #     print("***** STORING IN S3")
        #     return self.getDestinationCollectorSQL()
        #     print("***** DATA STORED IN S3 SUCCESSFULLY")


    #Location Collector Methods for storing and retrieving from S3
    #LC S3 Helper Method ##Encapsulate #Priority 3
    def putLocationCollectorS3(self, detailsInDict):
        for key in detailsInDict:
            newDict = detailsInDict[key]
            data = self.getDataByKeyLocCollectorS3(key)
            if data is not None:
                data.update (newDict)
                newDict = data
            storeValue = str(json.dumps(newDict))
            self.putDataLocCollectorS3(key, storeValue)
    #LC S3 Helper Method ##Encapsulate #Priority 3

    def getLocationCollectorS3(self):
        s3Object = self.s3.list_objects(Bucket=self.bucketName)
        content = s3Object['Contents']
        keyList = []
        valueDict={}
        lcLen = len ( self.lc)
        for key in content:
            tempKey = key["Key"]
            vin = ""
            if (tempKey.startswith(self.lc)):
                vin = tempKey[tempKey.index(self.lc)+lcLen:]
            if ( len(vin) > 0 ): 
                keyList.append(tempKey)
                data = self.s3.get_object(Bucket=self.bucketName, Key=tempKey)
                content = data['Body'].read().decode()
                deJson=json.loads(content)
                valueDict[vin] = deJson
        
        return valueDict
    #LC S3 Helper Method ##Encapsulate #Priority 3
    def getDataByKeyLocCollectorS3(self, s3Key):
        return self.getDataByKeyS3(self.lc+s3Key)
    #LC S3 Helper Method ##Encapsulate #Priority 3
    def putDataLocCollectorS3(self, vin, data):
        self.putDataS3(self.lc+vin, data)

    #Wait Time Collector Methods for storing and retrieving from S3
    #WTC S3 Helper Method ##Encapsulate #Priority 3    
    def getWaitCollectorS3(self):
        ##Change to use Prefix argument in get_object() call #Priority 4
        print ( "getWaitCollector")
        s3Object = self.s3.list_objects(Bucket=self.bucketName)
        content = s3Object['Contents']
        keyList = []
        valueDict={}
        lcLen = len (self.wtc)
        for key in content:
            tempKey = key["Key"]
            vin = ""
            if (tempKey.startswith(self.wtc)):
                vin = tempKey[tempKey.index(self.wtc)+lcLen:]
            if ( len(vin) > 0 ): 
                keyList.append(tempKey)
                data = self.s3.get_object(Bucket=self.bucketName, Key=tempKey)
                content = data['Body'].read().decode()
                deJson=json.loads(content)
                valueDict[vin] = deJson

        return valueDict
    #WTC S3 Helper Method ##Encapsulate #Priority 3
    def putWaitCollectorS3(self, detailsInDict):
        for key in detailsInDict:
            newDict = detailsInDict[key]
            data = self.getDataByKeyWTCollectorS3(key)
            if data is not None:
                ##This needs to perform object value traversal #Priority 1
                data.update (newDict)
                newDict = data
            storeValue = str(json.dumps(newDict))
            self.putDataWTCollectorS3(key, storeValue)
    #WTC S3 Helper Method ##Encapsulate #Priority 3
            newDict = self.mergeWaitCollectorS3(key, data, newDict)
            storeValue = str(json.dumps(newDict))
            self.putDataWTCollectorS3(key, storeValue)

    def mergeWaitCollectorS3(self, vin, existingDict, newDict):
        for key in newDict:
            data = existingDict.get(key)
            if ( data is None):
                existingDict[key] = newDict.get(key)
            else:
                existingDict[key] = [data[0], newDict.get(key)[1]]
        return existingDict

    # def storeS3(self, detailsInDict):
    #     print ("store s3")
    #     for key in detailsInDict:
    #         newDict = detailsInDict[key]
    #         storeValue = str(json.dumps(newDict))
            
    #         self.s3.put_object(
    #             Body=storeValue,
    #             Bucket=self.bucketName,
    #             Key=key
    #         )
    #         print ( " value stored in s3" )
        
 

    # def getAllDataS3(self):
    #     s3Object = self.s3.list_objects(Bucket=self.bucketName)
    #     content = s3Object['Contents']
    #     keyList = []
    #     valueDict={}
    #     for key in content:
    #         keyList.append(key["Key"])
    #         data = self.s3.get_object(Bucket=self.bucketName, Key=key["Key"])
    #         content = data['Body'].read().decode()
    #         deJson=json.loads(content)
    #         valueDict[key["Key"]] = deJson
    #     return valueDict

    def getDataByKeyWTCollectorS3(self, s3Key):
        return self.getDataByKeyS3(self.wtc+s3Key)
    #WTC S3 Helper Method ##Encapsulate #Priority 3
    def putDataWTCollectorS3(self, vin, data):
        self.putDataS3(self.wtc+vin, data)

    #Destination Collector Methods for storing and retrieving from S3
    #DC S3 Helper Method ##Encapsulate #Priority 3
    def putDestinationCollectorS3(self, detailsInDict):
        for _vin in detailsInDict:
            newDict = detailsInDict[_vin]
            storedDict = self.getDataByKeyDestCollectorS3(_vin)
            if storedDict is not None:
                storedDict.update(newDict)
                newDict = storedDict
            storeValue = str(json.dumps(newDict))
            self.putDataDestCollectorS3(_vin, storeValue)
    #DC S3 Helper Method ##Encapsulate #Priority 3
    def getDestinationCollectorS3(self):
        ##Change to use Prefix argument in get_object() call #Priority 4
        print ( "getDestinationCollector")
        s3Object = self.s3.list_objects(Bucket=self.bucketName)
        content = s3Object['Contents']
        keyList = []
        valueDict={}
        dcLen = len(self.dc)
        for key in content:
            tempKey = key["Key"]
            vin = ""
            if (tempKey.startswith(self.wtc)):
                vin = tempKey[tempKey.index(self.dc)+dcLen:]
            if ( len(vin) > 0 ): 
                keyList.append(tempKey)
                data = self.s3.get_object(Bucket=self.bucketName, Key=tempKey)
                content = data['Body'].read().decode()
                deJson=json.loads(content)
                valueDict[vin] = deJson

        return valueDict
    #DC S3 Helper Method ##Encapsulate #Priority 3
    def getDataByKeyDestCollectorS3(self, s3Key):
        return self.getDataByKeyS3(self.dc+s3Key)
    #DC S3 Helper Method ##Encapsulate #Priority 3
    def putDataDestCollectorS3(self, vin, data):
        return self.putDataS3(self.dc+vin, data)

    #Generic S3 Helper Method
    #S3 GET Method ##Encapsulate #Priority 3
    def getDataByKeyS3(self, s3Key):
        try:
            data = self.s3.get_object(Bucket=self.bucketName, Key=s3Key)
            content = data['Body'].read().decode()
            dataDict = json.loads(content)
            return dataDict
        except self.s3.exceptions.NoSuchKey:
            print("no such key in bucket")
        return None
    #S3 PUT Method ##Encapsulate #Priority 3
    def putDataS3(self, s3Key, data):
        self.s3.put_object(
            Body=data,
            Bucket=self.bucketName,
            Key=s3Key
        )
        print ( " value stored in s3" )


    ##Probably separate SQLite methods into separate class #Priority 3
    def initSQL(self):
        try:
            connection = sqlite3.connect(self.dbName)
            connection.text_factory = str
        except Error as e:
            print("Error occurred: " + str(e))
        print('\033[32m' + "Sample: " + '\033[m')
        
        # # Sample Drop table
        # connection.execute("DROP TABLE IF EXISTS sample;")
        # # Sample Create
        try:
            connection.execute("CREATE TABLE wtc(vin text, seqCode text, startTime text, endTime text);")
            connection.execute("CREATE TABLE lc(vin text, seqCode text, lat text, lon text);")
            # # Sample Insert
            # connection.execute("INSERT INTO sample VALUES (?,?)",("1","test_name"))
            connection.commit()
            connection.close()
        except Error as e:
            #ignore the error
            print("")
        # # Sample Select
        #cursor = connection.execute("SELECT * FROM data;")
        #connection.execute("INSERT INTO sample VALUES (?,?)",("1","test_name"))
        #print(cursor.fetchall())
        print ( "***** SQL LITE INITIALIZED ")

    def putDataWaitCollectorSQL(self, vin, loc, startTime, endTime):
        try:
            connection = sqlite3.connect(self.dbName)
            connection.text_factory = str
        except Error as e:
            print("Error occurred: " + str(e))
        try:
            ############### EDIT SQL STATEMENT ###################################
            sql = """ SELECT * from wtc
                         where vin = ? and seqCode =? ;"""
            ######################################################################
            
            cursor = connection.execute(sql, (vin, loc))
            resultSet = cursor.fetchall()
            exist = False
            if len(resultSet) > 0 :
                exist = True

            if ( exist ):
                print ("EXECUTING IF CONDITION UPDATE")
                connection.execute("UPDATE wtc SET vin = ?, seqCode = ?,  endTime = ? where vin=? and seqCode=?",(vin,loc,endTime,vin,loc))
            else:    
                connection.execute("INSERT INTO wtc VALUES (?,?,?,?)",(vin,loc,startTime, endTime))

            connection.commit()
        except Error as e:
             print("Error occurred: " + str(e))

    def putDataLocationCollectorSQL(self, vin, loc, lat, lon):
        try:
            connection = sqlite3.connect(self.dbName)
            connection.text_factory = str
        except Error as e:
            print("Error occurred: " + str(e))
        try:
            ############### EDIT SQL STATEMENT ###################################
            sql = """ SELECT * from lc
                         where vin = ? and seqCode =? ;"""
            ######################################################################
            
            cursor = connection.execute(sql, (vin, loc))
            resultSet = cursor.fetchall()
            exist = False
            if len(resultSet) > 0 :
                exist = True
            print ( "######### VIN #####", vin)
            print ( "######### LOC #####", loc)
            print("###################",exist)
            if ( exist ):
                print ("EXECUTING IF CONDITION UPDATE")
                connection.execute("UPDATE lc SET vin = ?, seqCode = ?, lat = ?, lon = ? where vin=? and seqCode=?",
                (vin,loc,lat, lon,vin,loc))
            else:    
                print ("EXECUTING else CONDITION insert")
                connection.execute("INSERT INTO lc VALUES (?,?,?,?)",(vin,loc,lat, lon))
            connection.commit()
            connection.close()
        except Error as e:
             print("Error occurred: " + str(e))

    def putLocationCollectorSQL(self, detailsInDict):
        print ("sql")
        for key in detailsInDict:
            vin = key
            location = detailsInDict[key]
            for locKey in location:
                lat = location[locKey][0]
                lon = location[locKey][1]
                self.putDataLocationCollectorSQL(vin, locKey, lat, lon)

    def putWaitCollectorSQL(self, detailsInDict):
        print ("sql")
        for key in detailsInDict:
            vin = key
            location = detailsInDict[key]
            for locKey in location:
                startTime = location[locKey][0]
                endTime = location[locKey][1]
                self.putDataWaitCollectorSQL(vin, locKey, startTime, endTime)


    def getLocationCollectorRowsSQL(self):
        try:
            connection = sqlite3.connect(self.dbName)
            connection.text_factory = str
        except Error as e:
            print("Error occurred: " + str(e))
        try:
            sql = "SELECT vin, seqCode, lat, lon FROM lc;"
            cursor = connection.execute(sql)
            return cursor.fetchall()
        except Error as e:
             print("Error occurred: " + str(e))

    def getWaitCollectorRowsSQL(self):
        try:
            connection = sqlite3.connect(self.dbName)
            connection.text_factory = str
        except Error as e:
            print("Error occurred: " + str(e))
        try:
            sql = "SELECT vin, seqCode, startTime, endTime FROM wtc;"
            cursor = connection.execute(sql)
            return cursor.fetchall()
        except Error as e:
             print("Error occurred: " + str(e))

    def getWaitCollectorSQL(self):
        print ("getAllDataWaitCollectorSQL")
        rowSet = self.getWaitCollectorRowsSQL()
        vinData = {}
        for i in range(0,len(rowSet)):
            vin = rowSet[i][0]
            loc = rowSet[i][1]
            startTime = rowSet[i][2]
            endTime = rowSet[i][3]
            if vinData.get(vin) is None:
                vinData[vin] = {loc:[startTime, endTime]}
            else:
                locDict = vinData.get(vin)
                locDict[loc] = [startTime, endTime]
        return vinData

    def getLocationCollectorSQL(self):
        print ("getAllDataLocationCollectorSQL")
        rowSet = self.getLocationCollectorRowsSQL()
        vinData = {}
        for i in range(0,len(rowSet)):
            vin = rowSet[i][0]
            loc = rowSet[i][1]
            lat = rowSet[i][2]
            lon = rowSet[i][3]
            if vinData.get(vin) is None:
                vinData[vin] = {loc:[lat, lon]}
            else:
                locDict = vinData.get(vin)
                locDict[loc] = [lat, lon]
        return vinData