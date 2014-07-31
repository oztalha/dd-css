import pymongo
import io
import json
import os
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import current_app

def get_file_params(filename):
    filepath = os.path.abspath(current_app.root_path)+"/../download/"+filename
    #print filepath
    #if os.path.isfile(filepath):
    #    return filename,"/download/"+filename,os.path.getsize(filepath)
    with open(filepath, 'w') as outfile:
        data = load_from_mongo("ddcss","queries",\
            criteria = {"_id" : ObjectId(filename)}, projection = {'_id': 0})
        #outfile.write(json.dumps(data[0], default=json_util.default))
        outfile.write(dumps(data[0]))
    #print os.path.getsize(filepath)    
    return filename, "/download/"+filename, os.path.getsize(filepath)

def save_json(filename, data):
    print data
    print json.dumps(data, ensure_ascii=False)
    with io.open('tests/{0}.json'.format(filename), 
                 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(data, ensure_ascii=False)))

def save_to_mongo(data, mongo_db, mongo_db_coll, save = True, manipulate=True ,**mongo_conn_kw):
    
    # Connects to the MongoDB server running on 
    # localhost:27017 by default
    
    client = pymongo.MongoClient(**mongo_conn_kw)
    
    # Get a reference to a particular database
    
    db = client[mongo_db]
    
    # Reference a particular collection in the database
    
    coll = db[mongo_db_coll]
    
    # Perform a bulk insert and  return the IDs
    if(save):
        return coll.save(data)
    else:
        return coll.insert(data)

def load_from_mongo(mongo_db, mongo_db_coll, return_cursor=False,
                    criteria=None, projection=None, **mongo_conn_kw):
    
    # Optionally, use criteria and projection to limit the data that is 
    # returned as documented in 
    # http://docs.mongodb.org/manual/reference/method/db.collection.find/
    
    # Consider leveraging MongoDB's aggregations framework for more 
    # sophisticated queries.
    
    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]
    
    if criteria is None:
        criteria = {}
    
    if projection is None:
        cursor = coll.find(criteria)
    else:
        cursor = coll.find(criteria, projection)

    # Returning a cursor is recommended for large amounts of data
    
    if return_cursor:
        return cursor
    else:
        return [ item for item in cursor ]