import pymongo
import io
import json
import os
from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import current_app
import csv
import codecs
import StringIO

# -*- coding: utf-8 -*-

def get_file_params(filebasename, fformat):
    filename = filebasename + "." + fformat 
    filepath = os.path.abspath(current_app.root_path)+"/../download/"+filename

    with open(filepath, 'w') as outfile:
        data = load_from_mongo("ddcss","queries",\
            criteria = {"_id" : ObjectId(filebasename)}, projection = {'_id': 0})
        #outfile.write(json.dumps(data[0], default=json_util.default))
        print fformat
        if fformat == "json":
            print data[0]
            outfile.write(dumps(data[0], indent=1))
            outfile.close()
        if fformat == "csv":
            if data[0][u'qname'] == "Twitter Friends & Followers":
                print data[0][u'data']
                save_csv(filepath,[[k]+v for (k,v) in data[0][u'data'].iteritems()])
            if data[0][u'qname'] == "Twitter User Timeline":
                status_texts = [ (unicode('"'+str(status['id'])+'"'), unicode(status['created_at']), unicode(status['text'])) for status in data[0][u'data']]
                print status_texts
                save_csv(filepath, status_texts, header=[u'id', u'created_at', u'text'])
                
    #print os.path.getsize(filepath)    
    return filename, "/download/"+filename, os.path.getsize(filepath)


def save_csv(mypath, mylist, header=None):
    myfile = open(mypath, 'w')
    
    #myfile = codecs.open(mypath, 'w', 'utf-8')
    wr = UnicodeWriter(myfile, quoting=csv.QUOTE_ALL)
    # wr = writer(myfile, dialect=csv.excel, quoting=csv.QUOTE_MINIMAL)
    if header:
        wr.writerow(header)
    wr.writerows(mylist)
    myfile.close()


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
                    criteria=None, projection=None, sorting = None, **mongo_conn_kw):
    
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
        if sorting:
            cursor = coll.find(criteria, projection).sort(sorting[0],sorting[1])
        else:
            cursor = coll.find(criteria, projection)

    # Returning a cursor is recommended for large amounts of data
    
    if return_cursor:
        return cursor
    else:
        return [ item for item in cursor ]


def remove_from_mongo(mongo_db, mongo_db_coll, criteria=None,
                    projection=None, sorting = None, **mongo_conn_kw):
        
    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]
    if criteria is None:
        criteria = {}
    
    if projection is None:
        cursor = coll.remove(criteria)    

    return cursor


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel_tab, encoding="utf-16", **kwds):
        # Redirect output to a queue
        self.queue = StringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f

        # Force BOM
        if encoding=="utf-16":
            import codecs
            f.write(codecs.BOM_UTF16)

        self.encoding = encoding

    def writerow(self, row):
        # Modified from original: now using unicode(s) to deal with e.g. ints
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = data.encode(self.encoding)

        # strip BOM
        if self.encoding == "utf-16":
            data = data[2:]

        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)