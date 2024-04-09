import requests
import os
import sys
import json
import glob
from requests.auth import HTTPBasicAuth
#from authentication import USERNAME, PASSWORD
from configuration import API_PATH
from json.decoder import JSONDecodeError

#To delete a resource, write, for instance:
#push_data.py ../TBX_files_ready_to_push/3548 DEL

SYNC_PATH = "collection"
EXTERNAL = "external"
USERNAME = ""
PASSWORD = ""

def get_Eurotermbank_HTTPBasicAuth():
    auth=HTTPBasicAuth(USERNAME, PASSWORD)
    return auth
    
def get_basic_path():
    return os.path.join(API_PATH, SYNC_PATH)

def get_basic_path_external():
    return os.path.join(API_PATH, SYNC_PATH, EXTERNAL)

def get_data_external():
    # TODO: Not working
    # Get all current data
    print("\n------\nMade request: ", get_basic_path_external())
    response = requests.get(get_basic_path_external(),
             auth = get_Eurotermbank_HTTPBasicAuth())
    print("Response: ", response)
    try:
        response_to_return = response.json()
    except JSONDecodeError:
        response_to_return = response
    return response_to_return



def get_data():
    # Get all current data
    print("\n------\nMade request: ", get_basic_path())
    response = requests.get(get_basic_path(),
                 auth = get_Eurotermbank_HTTPBasicAuth())
    print("Response: ", response)
    try:
        response_to_return = str(response.json()).encode('utf-8')
    except JSONDecodeError:
        response_to_return = response
    return response_to_return


def add_terms(collection_folder, id):
    responses = []
    headers = {'Content-Type': 'application/xml'}
    tbx_files = glob.glob(os.path.join(collection_folder, "*.tbx"))
    ENTRIES = "entries"
    request_str = os.path.join(get_basic_path_external(), str(id), ENTRIES)
    print("\n------\nMade request: ", request_str)
    
    for tbx_file in tbx_files:
        print("Reading from " + tbx_file)
        xml_text_file = open(tbx_file, encoding = 'utf-8')
        xml_text = xml_text_file.read()

        response = requests.post(request_str,
                      auth=get_Eurotermbank_HTTPBasicAuth(), data = xml_text.encode('utf-8'), headers=headers)
        print("Response when submitting " + tbx_file + ": ",  response)
        
        try:
            response_to_return = response.json()
        except JSONDecodeError:
            response_to_return = response
        responses.append(response_to_return)
        
    return responses

def delete_collection(id):
    request_str = os.path.join(get_basic_path_external(), str(id))
    del_response = requests.delete(request_str,
              auth=get_Eurotermbank_HTTPBasicAuth())
    return del_response
    
def create_collection(json_filename, id):
    # Create collection
    with open(json_filename, 'r', encoding='utf-8') as jsonfile:
        data = jsonfile.read()
        meta_data = json.loads(data)

        request_str = os.path.join(get_basic_path_external(), str(id))
        print("\n------\nMade request: ", request_str)

        response = requests.put(request_str,
              auth=get_Eurotermbank_HTTPBasicAuth(), json = meta_data)
        print("Response: ", response)

        try:
            response_to_return = response.json()
        except JSONDecodeError:
            response_to_return = response
        return response_to_return
        

if __name__ == '__main__':
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        raise ValueError('Provide search path to a collection to upload')
        exit(1)
        
    collection_folder = sys.argv[1].rstrip(os.sep)
    if not os.path.isdir(collection_folder):
        raise ValueError("'" + collection_folder + "' is is not an existing folder")
        exit(1)
    nr = os.path.split(collection_folder)[-1]

    with open(os.path.join(os.path.dirname(collection_folder), "authentication.json")) as authfile:
        auth = json.load(authfile)
        USERNAME = auth["USERNAME"]
        PASSWORD = auth["PASSWORD"]
        
    if len(sys.argv) == 3 and sys.argv[2] == "DEL":
        print("You have choosen to delete terms in the collection with id: ", nr)
        collection_returned = delete_collection(nr)
        print(collection_returned)
        exit(0)
    
    METADATA_FILENAME = "metadata.json"
   
    print("You have choosen to push terms in the collection with id: ", nr)
    collection_returned = create_collection(os.path.join(collection_folder, METADATA_FILENAME), nr)
    print("The api method for creating/updating new a collection returned the following: \n", collection_returned)


    add_terms_responses = add_terms(collection_folder, nr)
    print("add_terms_responses: ", add_terms_responses)
    
    get_data_response = get_data()
    print(get_data_response)
    
