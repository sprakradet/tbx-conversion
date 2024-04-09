from create_tbx import get_tbxs_and_source
import sys
import os
import json

def get_metadata_template(collection_id, source):

    # Duplicated code, but this might be changed anyway later
    name = ""
    if 'Utgivare' in source:
        utgivare = source['Utgivare']
        org_list = []
        for utg in utgivare:
            if 'organisation' in utg:
                org_list.append(utg['organisation'])
        name = name + ", ".join(org_list) + ": "
    if 'Titel' in source:
        name = name + source['Titel']
    if 'Utgivningsår' in source:
        name = name + " | " + source['Utgivningsår']
    
    contact_person = "CONTACT-PERSON"
    email = "E-MAIL"
    organisation = "ORGANISATION"
    if "Utgivare" in source:
        contact_person = source["Utgivare"][0].get("kontaktperson", "CONTACT-PERSON")
        email = source["Utgivare"][0].get("e-post", "E-MAIL")
        organisation = source["Utgivare"][0].get("organisation", "ORGANISATION")
    metadata_json = {
        "name": source.get("Titel", "TITLE"),
        "description": name,
        "domainid": "36",
        "attributionText": "ATTRIBUTION TEXT",
        "cpEmail": "terminologi@isof.se",
        "iprOrganization": "IPR HOLDER ORGANIZATION",
        "licence": "CC-BY-4.0",
        "originalName": name,
        "originalNameLang": "sv",
        "sourceURL": source.get("URL", "https://www.rikstermbanken.se")
    }
    return json.dumps(metadata_json)
    
def create_eurotermbank_folder(collection_id, output_folder, debug):
    output_for_collection = os.path.join(output_folder, str(collection_id))
    
    if not os.path.isdir(output_for_collection):
        print("Creating " + str(output_for_collection))
        os.mkdir(output_for_collection)
    else:
        print("Write to existing " + str(output_for_collection))
        
    
    tbxs, source = get_tbxs_and_source(collection_id, debug)
    file_nr = 1
    for tbx in tbxs:
        outputfile_name = os.path.join(output_for_collection,
            str(collection_id) + "_" + str(file_nr) + ".tbx")
        print(outputfile_name)
        with open(outputfile_name, "w") as outputfile:
            outputfile.write(tbx)
        file_nr = file_nr + 1
            
    metadata_json = get_metadata_template(collection_id, source)
    metadata_outputfile_name = os.path.join(output_for_collection,
        "TEMPLATE_" + str(collection_id) + "_metadata.json")
    with open(metadata_outputfile_name, "w") as metaoutputfile:
        metaoutputfile.write(metadata_json)
        
        

if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise ValueError('As the first argument, provide the id of the collection to convert to tbx. As the second argument provide the main folder into which the results is to be exported \n E.g.: \n python create_eurotermbank_folder.py 1 output')
        exit(1)
    
    if len(sys.argv) == 4 and sys.argv[3].lower().replace("-", "") == "debug":
        debug = True
    else:
        debug = False
        
    
    # TODO: Should id really be an int?
    collection_id = int(sys.argv[1])
    
    output_folder = sys.argv[2]
    if not os.path.isdir(output_folder):
        raise ValueError("'" + output_folder + "' is is not an existing folder")
        exit(1)
        
    create_eurotermbank_folder(collection_id, output_folder, debug)


# TODO: Compare xmls
# https://stackoverflow.com/questions/24492895/comparing-two-xml-files-in-python

