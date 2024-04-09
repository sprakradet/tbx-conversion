# -*- coding: utf-8 -*-
"""Create a tbx from Rikstermbanken's internal format

The code for ..
"""

from xml.etree.ElementTree import Element, SubElement, Comment
from xml.etree import ElementTree
from xml.dom import minidom

from fetch_from_db import *
from get_from_db import *
import configuration

import json
import sys
import os

"""
Other constants than tags
----------
"""
XCS = "https://eurotermbank.com/tbx-0.5.1.xcs"

"""
Tags used
----------
"""

# Tags
MARTIFHEADER = "martifHeader"
FILEDESC = "fileDesc"
SOURCEDESC = "sourceDesc"
P = "p"
ENCODINGDESC = "encodingDesc"
TEXT = "text"
BODY = "body"
TERMENTRY = "termEntry"
LANGSET = "langSet"
NTIG = "ntig"
TERMGRP = "termGrp"
TERM = "term"
TERMNOTE = "termNote"
TERMCOMPLIST = "termCompList"
TERMCOMP = "termComp"
XREF = "xref"
DESCRIPGRP = "descripGrp"
DESCRIP = "descrip"
NOTE = "note"
ADMIN = "admin"
REF = "ref"
ADMINGRP = "adminGrp"
ADMINNOTE = "adminNote"

# Attributes
TYPE = "type"
TARGET = "target"
ID = "id"
XMLLANG = "xml:lang"
ANNOTATEDNOTE = "annotatedNote"
NOTESOURCE = "noteSource"

# ref type
CROSSREFERENCE = "crossReference"
SEE = "see"

# termNote type
ADMINISTRATIVESTATUS = "administrativeStatus"
NORMATIVEAUTHORIZATION = "normativeAuthorization"
TERMTYPE = "termType"
GRAMMATICALGENDER = "grammaticalGender"
GRAMMATICALNUMBER = "grammaticalNumber"
PARTOFSPEECH = "partOfSpeech"
GRAMMATICALVALENCY = "grammaticalValency"
USAGENOTE = "usageNote"
GEOGRAPHICALUSAGE = "geographicalUsage"
HOMOGRAPH = "homograph"
PRONUNCIATION = "pronunciation"
TRANSFERCOMMENT = "transferComment"

# descrip type
DEFINITION = "definition"
EXAMPLE = "example"
EXPLANATION = "explanation"
CONTEXT = "context"

# termCompList type
MORPHOLOGICALELEMENT = "morphologicalElement"

# admin type
SOURCEIDENTIFIER = "sourceIdentifier"
SEARCHTERM = "searchTerm"

# xref type
XSOURCE = "xSource"

#p type
XCSURI = "XCSURI"

DEBUG_INFO_FOLDER = "DEBUG-INFO"

DESC_MAPPING_DICT = {"definition" : "definition",
                    "explanation" : "explanation",
                    "context" : "context",
                    "example" : "example"}
                    
"""
Help functions
----------
"""

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8', method='xml')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def add_tag_and_content(tag_name, parent, type, text):
    tag = SubElement(parent, tag_name)
    tag.set(TYPE, type)
    tag.text = text
    
def add_term_note(parent, type, text):
    add_tag_and_content(TERMNOTE, parent, type, text)

def add_xref(parent, type, target):
    tag = SubElement(parent, XREF)
    tag.set(TYPE, type)
    tag.set(TARGET, target)
       
def add_description(parent, type, text):
    add_tag_and_content(DESCRIP, parent, type, text)
    
def add_admin(parent, type, text):
    add_tag_and_content(ADMIN, parent, type, text)

def add_annotated_note(parent, type, text):
    add_tag_and_content(ADMINNOTE, parent, type, text)
    
def add_note(parent, text):
    tag = SubElement(parent, NOTE)
    tag.text = text

def add_ref(parent, type, target, text):
    tag = SubElement(parent, REF)
    tag.set(TYPE, type)
    tag.set(TARGET, target)
    tag.text = text
    

"""
Main tbx creation function
----------
"""

def get_tbxs_and_source(source_id, debug):
    if debug:
        if not os.path.exists(DEBUG_INFO_FOLDER):
            os.makedirs(DEBUG_INFO_FOLDER)
        else:
            print(DEBUG_INFO_FOLDER + " already exists. Remove to create new debug folder")
            print("Exit without output")
            exit(1)

    mongo_connector = MongoConnector()
    concept_posts = mongo_connector.fetch_all_concept_posts_in_source(source_id)
    
    if configuration.TERM_BATCH_SIZE == None:
        STEP = len(concept_posts)
    else:
        STEP = configuration.TERM_BATCH_SIZE
    
    used_ids = set()
    to_index = STEP
    from_index = 0
    tbxs = []
    source = None
    while(from_index<len(concept_posts)):
        if to_index > len(concept_posts):
            to_index = len(concept_posts)
        tbx, source = do_get_tbxs_and_source(source_id, mongo_connector, used_ids, concept_posts[from_index:to_index], concept_posts, debug)
        tbxs.append(tbx)
        from_index = to_index
        to_index = to_index + STEP
    return tbxs, source
    
def do_get_tbxs_and_source(source_id, mongo_connector, used_ids, concept_posts, all_concept_posts, debug):

    # Construct header: Information on the source and the encoding
    martif = Element(MARTIFHEADER)
    
    source = mongo_connector.fetch_source(source_id)
    print(source)

    add_header(source_id, martif, source)
    text = SubElement(martif, TEXT)
    body = SubElement(text, BODY)
    
    # Loop through the concept posts in the source

    
    if len(concept_posts) == 0:
        print("No concept posts found. No tbx exported")
        exit(1)
    
    for concept_post in concept_posts:
        if debug:
            debug_path = os.path.join(DEBUG_INFO_FOLDER, str(source_id)) + ".json"
            with open(debug_path, "a") as debug_file:
                #debug_file.write(str(concept_post) + "\n")
                debug_file.write("{}" + "\n")
 
        see_also_list = []
        see_under_list = []
        
        concept_post_id = get_id_for_concept_post(concept_post)
        
        if not concept_post_id.isascii():
            print("Not able to create TBX, concept id not converted to ascii")
            print(concept_post_id)
            exit(1)
            
        if concept_post_id in used_ids:
            print("Not able to create TBX, not able to create a unique id")
            print(concept_post_id)
            exit(1)
            
        used_ids.add(concept_post_id)
        
        term_entry = SubElement(body, TERMENTRY)
        term_entry.set(ID, concept_post_id)
        
        language_names = get_all_language_names_for_concept_post(concept_post)
        
        for language_name in language_names:
            
            # Get descriptions, notes and search terms (also use later)
            language_level_informations = get_all_language_level_information_for_language(language_name, concept_post)
            added_language_level_information_on_term_level = False
                        
            #  Adding ”term equivalents”, their type
            term_equivalents = get_all_term_equivalents_for_language(language_name, concept_post)

                        
            if term_equivalents:
                lang_set = SubElement(term_entry, LANGSET)
                language_name_in_tbx = language_name
                if language_name_in_tbx == "rk": # kalderash according to temporary coding
                    language_name_in_tbx = "rmy" # https://en.wikipedia.org/wiki/Vlax_Romani_language
                if language_name_in_tbx == "ra": # arli according to temporary coding
                    language_name_in_tbx = "rmn" # https://en.wikipedia.org/wiki/Balkan_Romani
                lang_set.set(XMLLANG, language_name_in_tbx)
            
                for term_equivalent in term_equivalents:
                    ntig = SubElement(lang_set, NTIG)
                    add_term_equivalent_info(ntig, term_equivalent)
                    
                    # Grammatical information
                    add_grammatical_information(ntig, term_equivalent)
                    
                    # Adding additional associated information
                    add_additional_associated_information(ntig, term_equivalent)
                    
                    if term_equivalent.is_a_standard_term and not added_language_level_information_on_term_level:
                        for language_level_information in language_level_informations:
                            if language_level_information.type != "definition":
                                add_description_or_note(ntig, language_level_information, add_on_term_level=True)
                        added_language_level_information_on_term_level = True
                        
            # Use language_level_informations, i.e., descriptions, notes and search terms
            search_terms = get_all_search_terms_for_language(language_name, concept_post)
            for language_level_information in language_level_informations:
                add_description_or_note(lang_set, language_level_information, add_on_term_level=False)
            for search_term in search_terms:
                add_search_term(lang_set, search_term)
            
            # References to other concepts and classifications
            see_also_list_for_lang = get_see_also_or_see_under_for_language(language_name, concept_post, all_concept_posts, "seealso")
            see_under_list_for_lang = get_see_also_or_see_under_for_language(language_name, concept_post, all_concept_posts, "seeunder")
            if see_also_list_for_lang:
                see_also_list.extend(see_also_list_for_lang)
            if see_under_list_for_lang:
                see_under_list.extend(see_under_list_for_lang)
                
            # For debugging
            if debug:
                with open(debug_path, "a") as debug_file:
                    debug_file.write("language: " + language_name + "\n")
                    for lli in language_level_informations:
                        debug_file.write("language_level_information: " + json.dumps(lli._asdict()) + "\n")
                    for term_eq in term_equivalents:
                        debug_file.write("term_equivalent: " + json.dumps(term_eq._asdict()) + "\n")
                    for search_term in search_terms:
                        debug_file.write("search_term: " + json.dumps(search_term._asdict()) + "\n")
                    for see_also in see_also_list_for_lang:
                        debug_file.write("see_also: " + json.dumps(see_also._asdict()) + "\n")
                    for see_under in see_under_list_for_lang:
                        debug_file.write("see_under: " + json.dumps(see_under._asdict()) + "\n")
                    debug_file.write("---------\n")
                    
        add_references_to_other_concepts(parent = term_entry,
            reference_list = see_also_list, reference_type = "crossReference")
        add_references_to_other_concepts(parent = term_entry,
            reference_list = see_under_list, reference_type = "see")
            
            
                        
    return prettify(martif), source
    

    
    
"""
Functions for helping in tbx construction
----------
"""

# Construct header: Information on the source and the encoding
######

def add_header(source_id, martif, source):
    """ Construct header: Information on the source and the encoding
    """
    # fileDesc
    fileDesc = SubElement(martif, FILEDESC)
    sourceDesc = SubElement(fileDesc, SOURCEDESC)
    p = SubElement(sourceDesc, P)
    p.text = get_source_text(source)
    
    # encodingDesc
    encodingDesc = SubElement(martif, ENCODINGDESC)
    p2 = SubElement(encodingDesc, P)
    p2.set(TYPE, XCSURI)
    p2.text = XCS
    
    
# Adding ”term equivalents”, their type and their parent tags
######

def add_term_equivalent_info(ntig, term_equivalent):
    """Adding ”term equivalents”, and information for their type
    """
    term_grp = SubElement(ntig, TERMGRP)
    term = SubElement(term_grp, TERM)
    
    term.text = term_equivalent.term_to_present
    
    if term_equivalent.is_deprecated:
        add_term_note(parent = ntig, type=NORMATIVEAUTHORIZATION, text= "deprecatedTerm")
        add_term_note(parent = ntig, type=ADMINISTRATIVESTATUS, text= "deprecatedTerm-admn-sts")
        
    if term_equivalent.is_preferred:
        add_term_note(parent = ntig, type=NORMATIVEAUTHORIZATION, text= "preferredTerm")
        add_term_note(parent = ntig, type=ADMINISTRATIVESTATUS, text= "preferredTerm-admn-sts")
 
    if term_equivalent.is_synonym:
        add_term_note(parent = ntig, type=TERMTYPE, text= "synonym")

    if term_equivalent.is_synonym and term_equivalent.is_phrase:
        add_term_note(parent = ntig, type=TERMTYPE, text= "synonymousPhrase")

    if term_equivalent.is_phrase:
        add_term_note(parent = ntig, type=TERMTYPE, text= "phraseologicalUnit")
        
             
    if term_equivalent.is_admitted:
        add_term_note(parent = ntig, type=NORMATIVEAUTHORIZATION, text= "admittedTerm")
        add_term_note(parent = ntig, type=ADMINISTRATIVESTATUS, text= "admittedTerm-admn-sts")
        
    if term_equivalent.is_formula:
        add_term_note(parent = ntig, type=TERMTYPE, text= "formula")

# Grammatical information
######

GENDER_DICT = {"f" : "feminine", "m" : "masculine", "n" : "neuter"}
NOT_IN_GENDER_DICT = "otherGender"

NUMBER_DICT = {"pl" : "plural", "sing" : "singular", "koll" : "mass" }
NOT_IN_NUMBER_DICT = "otherNumber"

POS_DICT = {"subst" : "noun", "adj" : "adjective", "adv" : "adverb", \
    "itrverb" : "verb", "trverb" : "verb", "verb" : "verb", "verb:supinum" : "verb"}
NOT_IN_POS_DIC = "other"
VALENCY_DICT = {"itrverb" : "monovalent", "trverb" : "divalent or more"}

def add_grammatical_information(ntig, term_equivalent):
    """Adding grammatical information
    """
    
    if term_equivalent.gender:
        add_term_note(parent = ntig, type=GRAMMATICALGENDER,
            text = GENDER_DICT.get(term_equivalent.gender.replace(".", "").lower().strip(), NOT_IN_GENDER_DICT))
        
    if term_equivalent.grammar:
        add_term_note(parent = ntig, type=GRAMMATICALNUMBER,
            text = NUMBER_DICT.get(term_equivalent.grammar.replace(".", "").lower().strip(), NOT_IN_NUMBER_DICT))
    
    # Part of speech
    # Can be
    # {'subst.', 'förled', 'adj.', 'intr. verb', 'verb', 'adv.', 'tr. verb'}
    if term_equivalent.pos:
        pos_cleaned = term_equivalent.pos.replace(".", "").replace(" ", "").lower().strip()
        add_term_note(parent = ntig, type=PARTOFSPEECH, text=POS_DICT.get(pos_cleaned, NOT_IN_POS_DIC))
        
        if pos_cleaned in VALENCY_DICT:
            add_term_note(parent = ntig, type=GRAMMATICALVALENCY, text=VALENCY_DICT[pos_cleaned])
        
# Adding additional associated information
######

def add_additional_associated_information(ntig, term_equivalent):
    """Adding additional associated information, i.e., usage,
        geographical usage, general notes,
        abbreviation/full form, homograph, pronunciation, source.
    """
    
    if term_equivalent.narrowing:
        add_term_note(parent = ntig, type=USAGENOTE, text = term_equivalent.narrowing)

    if term_equivalent.geo:
        add_term_note(parent = ntig, type=GEOGRAPHICALUSAGE, text=term_equivalent.geo)
    
    if term_equivalent.equivalence:
        add_term_note(parent = ntig, type=TRANSFERCOMMENT, text=term_equivalent.equivalence)
        
    if term_equivalent.is_abbreviation:
        add_term_note(parent = ntig, type=TERMTYPE, text="abbreviation")
    
    if term_equivalent.is_full_form:
        add_term_note(parent = ntig, type=TERMTYPE, text="fullForm")
        
    if term_equivalent.homonym:
        add_term_note(parent = ntig, type=HOMOGRAPH, text=str(term_equivalent.homonym))
        
    if term_equivalent.pronunciation:
        add_term_note(parent = ntig, type=PRONUNCIATION, text=term_equivalent.pronunciation)
    
    if term_equivalent.source:
        add_xref(parent = ntig, type=XSOURCE, target=term_equivalent.source)
        
# Descriptions, notes and search terms
######

def add_description_or_note(parent_tag, language_level_information, add_on_term_level=False):

    """Add descriptions (definition, explanation, context and example),
    and notes (comment, domain and equivalence).
    """
    
    if language_level_information.type in DESC_MAPPING_DICT.keys():
        if add_on_term_level and language_level_information.type == "example":
            # Add as a note on term level to adapt to Fedterm, which does not use the example tag
            add_note(parent = parent_tag, text = "Example: " + language_level_information.text_to_present)
        elif add_on_term_level and language_level_information.type == "explanation":
            # Add as a note on term level to adapt to Fedterm, which does not use the explanation tag
            add_note(parent = parent_tag, text = "Explanation: " + language_level_information.text_to_present)
        else:
            descripgrp = SubElement(parent_tag, DESCRIPGRP)
            add_description(parent = descripgrp, type=DESC_MAPPING_DICT[language_level_information.type], text=language_level_information.text_to_present)
            if language_level_information.source:
                add_admin(parent = descripgrp, type=SOURCEIDENTIFIER, text=language_level_information.source)
    
    if language_level_information.type == "comment":
        add_note(parent = parent_tag, text = language_level_information.text_to_present)
    if language_level_information.type == "domain":
         add_note(parent = parent_tag, text = "Domain: " + language_level_information.text_to_present)
    if language_level_information.type == "equivalence":
        add_note(parent = parent_tag, text = "Equivalence: " + language_level_information.text_to_present)
        
    # Add comment twice if it contains a source
    # since eTranslation-TermBank-TBX
    # only supports standard notes, without source
    if language_level_information.type == "comment" and language_level_information.source:
        descripgrp = SubElement(parent_tag, ADMINGRP)
        add_admin(parent=descripgrp, type=ANNOTATEDNOTE, text=language_level_information.text_to_present)
        add_annotated_note(parent=descripgrp, type=NOTESOURCE, text=language_level_information.source)
        
def add_search_term(lang_set, search_term):
    add_admin(parent = lang_set, type=SEARCHTERM, text=search_term.term)


# References to other concepts and classifications
######

def add_references_to_other_concepts(parent, reference_list, reference_type):
    for reference in reference_list:
        add_ref(parent, reference_type, reference.target, reference.term)



    
