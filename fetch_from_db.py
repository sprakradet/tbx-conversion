# -*- coding: utf-8 -*-

from json import loads
from pymongo import MongoClient

"""
Fetch data from database
----------
"""
DEFAULT_DATABASE_NAME = "rikstermbanken_staging"

class MongoConnector:
    def __init__(self):
        self.DATABASE = DEFAULT_DATABASE_NAME
        self.client = None
       
    def get_connection(self):
        maxSevSelDelay = 5 #Check that the server is listening, wait max 5 sec
        if not self.client:
            self.client = MongoClient(serverSelectionTimeoutMS=maxSevSelDelay)
        return self.client

    def close_connection(self):
        if self.client:
            self.client.close()
            self.client = None

    def get_database(self):
        con = self.get_connection()
        db = con[self.DATABASE]
        return db
        
    def list_databases(self):
        con = self.get_connection()
        dbs = con.list_database_names()
        return dbs

    def get_all_collections(self):
        return [self.get_database()[collection_name] for collection_name in self.get_database().list_collection_names()]
        
    def get_kalla_collection(self):
        return self.get_database()["kalla"]

    def get_termpost_collection(self):
        return self.get_database()["termpost"]


    def fetch_source(self, source_id):
        source = self.get_kalla_collection().find_one({'id' : source_id})
        return source
        
    def fetch_all_concept_posts_in_source(self, source_id):
        """
        From the database, return all the complete information
        for each post from the source with source_id

        Returns:
        list:A list of concept posts
        """
        termposts = self.get_termpost_collection().find({'kalla.id' : source_id}).sort('_id', 1)
        return list(termposts)
    

if __name__ == "__main__":
    db = MongoConnector()
    print(db.get_all_collections())
    
    """
    print("-------")
    for el in db.get_kalla_collection().find({}):
        print(el)
        
    print("-------")
    for el in db.get_termpost_collection().find({}):
        print(el)
    """
    """
    print("-------")
    print(db.fetch_source_description_text(3533))
    """
    
    print("-------")
    #posts = db.fetch_all_concept_posts_in_source(3533)
    posts = db.fetch_all_concept_posts_in_source(1)
    for post in posts:
        print(post)
    
    
