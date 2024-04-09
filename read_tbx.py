# -*- coding: utf-8 -*-
"""This is the start of code for reading from TBX to the internal format of Rikstermbanken.
    What the code does now is to take the TBX and create named Tuples.
"""

from xml.etree.ElementTree import Element, SubElement, Comment
from xml.etree import ElementTree
from xml.dom import minidom

from fetch_from_db import *
from get_from_db import *
from create_tbx import *
import json
import sys
import os


###########
# This code only starts the work of translating from tbx back to NTRF
# It takes the TBX and creates named Tuples.
# The next step is to take these tuples and insert the information in the database.
# That is, to perform the work that is done in get_from_db.py, but backwards.
# Nothing is now returned, the information is only printed on the command line.
##########

def read_tbx(tbx_file_path):


    
    inv_genderdict = {v: k for k, v in GENDER_DICT.items()}
    inv_genderdict[NOT_IN_GENDER_DICT] = "other" # TODO: make other reconvertable
    
    inv_grammardict = {v: k for k, v in NUMBER_DICT.items()}
    inv_grammardict[NOT_IN_NUMBER_DICT] = "other" # TODO: make other reconvertable
    
    # what was original "verb:supinum" will be converted to "verb"
    inv_posdict = {v: k for k, v in POS_DICT.items() if k != "verb:supinum"}
    inv_posdict[NOT_IN_POS_DIC] = "other" # TODO: make other reconvertable
    
    inv_valency_dict = {"monovalent" : "itr verb", "divalent or more" : "tr verb"}
    
    
    DESC_MAPPING_DICT_inv = {v: k for k, v in DESC_MAPPING_DICT.items()}
    
    
    tree = ElementTree.parse(tbx_file_path)
    root = tree.getroot()
    for termEntry in root.iter("termEntry"):
        print("{}")

        split = False
        see_also_list = []
        see_under_list = []
        search_terms = []
        for ref in termEntry.iter(REF):
            
            if ref.attrib[TYPE] == "crossReference" or ref.attrib[TYPE] == "see":
                si = SeeInformation(term = ref.text,
                   target = ref.attrib[TARGET])
                if ref.attrib[TYPE] == "crossReference":
                    see_also_list.append(si)
                    #print("see_also: " +  json.dumps(si._asdict()))
                else:
                    see_under_list.append(si)
                    #print("see_under: ", json.dumps(si._asdict()))

        first_lang = True
        for langSet in termEntry.iter(LANGSET):
            current_lang = langSet.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
            if not first_lang:
                print("---------")
            first_lang = False
            print("language: " + current_lang)

            notes = {}
            for descripGrp in langSet.iter(DESCRIPGRP):
                # Each termEntry (and each language) can have several LanguageLevelInformation
                
                source =  None
                
                descrip_list = list(descripGrp.iter(DESCRIP))
                assert len(descrip_list) == 1
                for descrip in descrip_list:
                    text_to_present = descrip.text
                    type = DESC_MAPPING_DICT_inv[descrip.attrib[TYPE]]
                    
                admin_list = list(descripGrp.iter(ADMIN))
                assert len(admin_list) == 0 or len(admin_list) == 1
                for admin in admin_list:
                    if admin.attrib[TYPE] == SOURCEIDENTIFIER:
                        source = admin.text
                
                
                lli = LanguageLevelInformation(text_to_present = text_to_present,
                                                        type = type,
                                                        source = source)
                notes[text_to_present] = lli                
            
            for note in langSet.iter(NOTE):
                text = note.text
                type = "comment"
                if note.text.startswith("Domain: "):
                    type = "domain"
                    text = text.replace("Domain: ", "")
                elif note.text.startswith("Equivalence: "):
                    type = "equivalence"
                    text = text.replace("Equivalence: ", "")
                elif note.text.startswith("Example: "):
                    continue # fix, since Eurotermbank does not show normal example
                elif note.text.startswith("Explanation: "):
                    continue # fix, since Eurotermbank does not show normal explanation
                lli = LanguageLevelInformation(text_to_present = text,
                                                            type = type,
                                                        source = None)
                notes[text] = lli
                
            for adminGrp in langSet.iter(ADMINGRP):
                text = None
                source = None
                
                for admin in adminGrp.iter(ADMIN):
                    if admin.attrib[TYPE] == "annotatedNote":
                        text = admin.text
                for adminNote in adminGrp.iter(ADMINNOTE):
                    if adminNote.attrib[TYPE] == "noteSource":
                        source = adminNote.text
                lli = LanguageLevelInformation(text_to_present = text,
                    type = "comment",
                    source = source)
                 
                notes[text] = lli
                
            for key, item in notes.items():
                print("language_level_information: " + json.dumps(item._asdict()))
                
            for admin in langSet.iter(ADMIN):
                if admin.attrib[TYPE] == SEARCHTERM:
                    search = SearchTermInformation(term = admin.text)
                    search_terms.append(search)
                    
                    
            for ntig in langSet.iter(NTIG):
                # Each termEntry (and each language) can have several TermEquivalents
            
                is_synonym = False
                is_phrase = False
                is_abbreviation = False
                is_full_form = False
                
                is_deprecated =  False
                is_formula = False
                gender = None
                grammar = None
                pos = None
                
                narrowing = None
                geo = None
                pronunciation = None
                homonym = None
                
                source = None
            
                termGrps = list(ntig.iter('termGrp'))
                assert len(termGrps) == 1
                for termGrp in termGrps:
                    terms = list(termGrp.iter('term'))
                    assert len(terms) == 1
                    for term in termGrp.iter('term'):
                        term_to_present = term.text
                    
                for xRef in ntig.iter(XREF):
                    if xRef.attrib['type'] == XSOURCE:
                        source = xRef.attrib['target']
                    
                termNotes = ntig.iter(TERMNOTE)
                for termNote in termNotes:
                    if termNote.attrib[TYPE] == TERMTYPE:
                        if termNote.text == "synonym" or termNote.text == "synonymousPhrase":
                            is_synonym = True
                        elif termNote.text == "phraseologicalUnit" or termNote.text == "synonymousPhrase":
                            is_phrase = True
                        elif termNote.text == "formula":
                            is_formula = True
                        elif termNote.text == "abbreviation":
                            is_abbreviation = True
                        elif termNote.text == "fullForm":
                            is_full_form = True
                            
                    elif termNote.attrib[TYPE] == GRAMMATICALGENDER:
                        gender = inv_genderdict[termNote.text]
                    elif termNote.attrib[TYPE] == GRAMMATICALNUMBER:
                        grammar = inv_grammardict[termNote.text]
                    elif termNote.attrib[TYPE] == PARTOFSPEECH:
                        if inv_posdict[termNote.text] not in inv_valency_dict: # tr verb or itr verb
                            pos = inv_posdict[termNote.text]
                    elif termNote.attrib[TYPE] == GRAMMATICALVALENCY:
                        pos = inv_valency_dict[termNote.text]
                    elif termNote.attrib[TYPE] == NORMATIVEAUTHORIZATION or termNote.attrib[TYPE] == ADMINISTRATIVESTATUS:
                        if termNote.text == "deprecatedTerm" or termNote.text == "deprecatedTerm-admn-sts":
                           is_deprecated = True
                        elif termNote.text == "preferredTerm" or termNote.text == "preferredTerm-admn-sts" or termNote.text == "admittedTerm" or termNote.text == "admittedTerm-admn-sts":
                            split = True
                    elif termNote.attrib[TYPE] == USAGENOTE:
                        narrowing = termNote.text
                    elif termNote.attrib[TYPE] == GEOGRAPHICALUSAGE:
                        geo = termNote.text
                    elif termNote.attrib[TYPE] == PRONUNCIATION:
                        pronunciation = termNote.text
                    elif termNote.attrib[TYPE] == HOMOGRAPH:
                        homonym = termNote.text
                        
                
                te = TermEquivalent(term_to_present = term_to_present,
                    is_synonym = is_synonym,
                    is_admitted = False,
                    is_deprecated = is_deprecated,
                    is_preferred = False,
                    is_phrase = is_phrase,
                    is_formula = is_formula,
                    grammar = grammar,
                    gender = gender,
                    pos = pos,
                    narrowing = narrowing,
                    geo = geo,
                    is_abbreviation = is_abbreviation,
                    is_full_form = is_full_form,
                    homonym = homonym,
                    pronunciation = pronunciation,
                    source = source)
                
                print("term_equivalent: " + json.dumps(te._asdict()))
                #print(split)
                
            if current_lang == "sv":
                for el in search_terms:
                    print("search_term: " + json.dumps(el._asdict()))
                for el in see_also_list:
                    print("see_also: " +  json.dumps(el._asdict()))
                for el in see_under_list:
                    print("see_under: " + json.dumps(el._asdict()))
                        
        print("---------")
#################################
#################################


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError('As the first argument, provide the path of the tbx file to read. (As an optional second argument provide a debug option)')
        
    if len(sys.argv) == 3 and sys.argv[3].lower().replace("-", "") == "debug":
        debug = True
    else:
        debug = False
    
    tbx_file_path = sys.argv[1]
    if not os.path.exists(tbx_file_path):
        raise ValueError(tbx_file_path + " does not exist")
        
    read_tbx(tbx_file_path)
    
    
