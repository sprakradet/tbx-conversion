# -*- coding: utf-8 -*-

# The following import was used for only temporary for testing. Remove when not needed.
# from db_info_tuples_test import *

# Import the tuples used for getting information

from db_info_tuples import *

"""
Help functions
----------
"""

def __construct_text_from_paragraphs_discard_annotations(paragraph_list):
    if not paragraph_list:
        return ""
    el = paragraph_list[0]
    if "text" in el:
        return el["text"] + __construct_text_from_paragraphs_discard_annotations(paragraph_list[1:])
    if "annotated_text" in el:
        return __construct_text_from_paragraphs_discard_annotations(el["annotated_text"]) + __construct_text_from_paragraphs_discard_annotations(paragraph_list[1:])
    if "content" in el:
        return __construct_text_from_paragraphs_discard_annotations(el["content"]) + __construct_text_from_paragraphs_discard_annotations(paragraph_list[1:])
    else:
        print("not text, content or annotated text, something wrong in the following:")
        print(el)
        exit(1)
        
def __construct_text_from_paragraphs_with_annotations(paragraph_list):
    if not paragraph_list:
        return ""
    el = paragraph_list[0]
    if "text" in el:
        return el["text"] + __construct_text_from_paragraphs_with_annotations(paragraph_list[1:])
    if "annotated_text" in el:
        return __construct_text_from_paragraphs_with_annotations(el["annotated_text"]) + __construct_text_from_paragraphs_with_annotations(paragraph_list[1:])
    if "content" in el:
        start_tag = "" # TODO: Not implemented yet to add start and end tags from the annotation
        end_tag = "" # perhaps it has to be done on when building the XML tree, not to get the HTML escaped
        return start_tag + __construct_text_from_paragraphs_with_annotations(el["content"]) + end_tag +  __construct_text_from_paragraphs_with_annotations(paragraph_list[1:])
    if "term" in el:
        el_content = el["term"]
        if "term" in el_content:
            el_text = el_content["term"]
        else:
            print("expected a dictionary with a term key in the following:")
            print(el_content)
            exit(1)
        if "homonym" in el_content:
            el_text = el_text + " (" + el_content["homonym"] + ") "
        return el_text + __construct_text_from_paragraphs_with_annotations(paragraph_list[1:]) 
    else:
        print("not text, content or annotated text, something wrong in the following:")
        print(el)
        exit(1)


def __construct_term_to_present(term, annotated_term):
    if term:
        return term
    else: # For terms, discard annotations
        return __construct_text_from_paragraphs_discard_annotations(annotated_term)


def __construct_text_from_paragraphs_for_texts(paragraph_list):
    # TODO: Keeps some annotations
    return __construct_text_from_paragraphs_with_annotations(paragraph_list)

   
def __construct_target_text_for_swedish_reference(term, concept_posts, homonym_number=None, language_name=None):

    target = None
    for concept_post in concept_posts:
        term_content_list = concept_post["terms"]
        for db_term in term_content_list:
            if "term" in db_term and db_term["term"] == term and "lang" in db_term and db_term["lang"] == language_name:
                if homonym_number:
                    if "homonym" in db_term and db_term["homonym"] == homonym_number:
                        target = __contruct_id_from_slug(concept_post["slugs"][0])
                        break
                else:
                    target = __contruct_id_from_slug(concept_post["slugs"][0])
                    break
    if not target:
        print("No matching reference found for '" + term + "'. Use empty string.")
        target = ""
      
    return target
    
    
def __contruct_id_from_slug(utf_id):
    utf_id = utf_id.lower().replace("å", "aa").replace("ä", "ae").replace("ö", "oe").replace("é", "ee")
    utf_id = utf_id.encode("ascii", "ignore").decode()
    # The first element in the list is the id
    return utf_id

"""
Convert the information from the database
----------
"""
def get_source_text(source):
    # TODO: Check that status is published (Magnus knows which number)
    if not source: # TODO: Perhaps error instead
        return ""
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
    return name


def get_id_for_concept_post(concept_post):
    utf_id = concept_post['slugs'][0]
    return __contruct_id_from_slug(utf_id)
   

def get_all_language_names_for_concept_post(concept_post):
    """
    Extract a list of language codes strings from the concept post,
    both accociated with the terms and those associated with the texts

    Returns:
    list:List of language names for which there are terms in the
    concept post, e.g., ["en", "ar"]
    """
    
    # Copied from rikstermbanken-web import_util.py
    # (if not all languages are include, alphabetical order will be used instead)
    term_lang_prio = {
        "sv": 0,
        "en": 1,
        "de": 2,
        "fr": 3,
        "es": 4,
        "ca": 5,
        "rom": 6,
        "la": 7,
        "da": 8,
        "fo": 9,
        "is": 10,
        "nb": 11,
        "nn": 12,
        "no": 13,
        "hr": 14,
        "pl": 15,
        "ru": 16,
        "gr": 17,
        "fi": 18,
        "fit": 19,
        "se": 20,
        "et": 21,
        "kl": 22,
        "tr": 23,
        "ku": 24,
        "ar": 25,
        "so": 26,
        "ja": 27,
        "nl": 28,
        "it": 29,
        "re": 30,
        "em": 31,
        "pt": 32,
        "il": 33,
        "sy": 34,
        "sq": 35,
        "rm": 36,
        "re": 37,
        "rk": 37,
        "ra": 38,
    }
    
    # Make a list of all unique languages in the list, i.e. contained in 'lang'
    
    term_equivalent_info_terms = [el['lang'] for el in concept_post.get("terms", [])]
    
    term_equivalent_info_texts = [el['lang'] for el in concept_post.get("texts", [])]
    
    langs = set(term_equivalent_info_terms + term_equivalent_info_texts)
    try:
        langs_prio = sorted([(term_lang_prio[l], l) for l in langs])
        lang_list_with_prio = [l for (p,l) in langs_prio]
    except KeyError:
        print("No term_lang_prio for language, use alphabetical order")
        lang_list_with_prio = sorted(langs)
        
    return lang_list_with_prio



def get_all_term_equivalents_for_language(language_name, concept_post):
    """
    Extract a list of term equivalents from the concept post for language

    A concept_post contains the key "terms", which is a list of term-equivalents.
    The relevant information from these term-equivalents is here
    packaged into the TermEquivalent named-tuples to make them useful for building the
    TBX structure.
    
    Returns:
    list:List of TermEquivalent named-tuples.
    """
    term_equivalent_list = []
    
    # If language matches:
    for term_equivalent_info in [tei for tei in concept_post.get("terms", []) if tei["lang"] == language_name]:
    
        """
        Term equivalents and their types
        """
        
        term_to_present = __construct_term_to_present(term_equivalent_info.get("term", None), term_equivalent_info.get("annotated_term", None))
        
        is_a_standard_term = term_equivalent_info.get('status', None) == 'TE'
            
        is_deprecated = term_equivalent_info.get('status', None) == 'AVTE'

        # if split: True AND status: TE
        is_preferred = term_equivalent_info.get('split', False) and term_equivalent_info['status'] == 'TE'
        
        # if split: True AND status: SYTE
        is_admitted = term_equivalent_info.get('split', False) and term_equivalent_info['status'] == 'SYTE'
        
        is_phrase = term_equivalent_info.get('phrase', False)
                
        is_synonym = term_equivalent_info.get('status', None) == 'SYTE'
        
        is_formula = term_equivalent_info.get('status', None) == 'BT'
            
        
        """
        Grammatical information
        """
        
        grammar = term_equivalent_info.get("grammar", None)
                
        gender = term_equivalent_info.get("gender", None)
        
        pos = term_equivalent_info.get("pos", None)
        
        
        """
        Additional term equivalent information
        """
    
        narrowing = term_equivalent_info.get("narrowing", None) #In NTRF: SA, speciellt användningsområde (termnivå))

        geo = term_equivalent_info.get("geo", None) # (In NTRF: geografiskt användningsområde, GE)

        # TODO: This is not working, as equivalence is stored on a term-post level in the datastructure and not
        # on the language level
        equivalence = term_equivalent_info.get("equivalence", None)
        
        is_abbreviation =  term_equivalent_info.get("abbreviation", False)
        
        is_full_form = term_equivalent_info.get("full form", False)
            
        homonym = term_equivalent_info.get("homonym")
        
        pronunciation = term_equivalent_info.get("pronunciation")
        
        source = term_equivalent_info.get("source")
        
        term_equivalent_list.append(TermEquivalent(term_to_present = term_to_present,
                                                    is_a_standard_term = is_a_standard_term,
                                                    is_synonym = is_synonym,
                                                    is_admitted = is_admitted,
                                                    is_deprecated = is_deprecated,
                                                    is_preferred = is_preferred,
                                                    is_phrase = is_phrase,
                                                    is_formula = is_formula,
                                                    grammar = grammar,
                                                    gender = gender,
                                                    pos = pos,
                                                    narrowing = narrowing,
                                                    geo = geo,
                                                    equivalence = equivalence,
                                                    is_abbreviation = is_abbreviation,
                                                    is_full_form = is_full_form,
                                                    homonym = homonym,
                                                    pronunciation = pronunciation,
                                                    source = source))
                                                        
    return term_equivalent_list
    
    
    
def get_all_language_level_information_for_language(language_name, concept_post):
    """
    Extract a list of language level information tuples from the concept post for language

    A concept_post contains a the key "texts", which is a list of language level information.
    The relevant information is here
    packaged into the LanguageLevelInformation named tuple
    
    Returns:
    list:List of LanguageLevelInformation named-tuples.
    """
    language_level_information_list = []
    
    for language_level_information in [lli for lli in concept_post.get("texts", []) if lli["lang"] == language_name]:
    
        text_to_present = __construct_text_from_paragraphs_for_texts(language_level_information.get("paragraphs", []))
        type = language_level_information["type"]
                
        source = language_level_information.get("source", None)
        
        language_level_information_list.append(LanguageLevelInformation(text_to_present = text_to_present,
                                                                        type=type,
                                                                        source = source))
    return language_level_information_list
     
     
     
def get_all_search_terms_for_language(language_name, concept_post):
    """
    Extract a list of search term information tuples from the concept post for language

    A concept_post contains the key "onlysearch", which is a list of search terms.
    The relevant information from is here
    packaged into the SearchTermInformation named tuple
    
    Returns:
    list:List of SearchTermInformation named-tuples.
    """
    
    search_term_information_list = []

    for search_term_information in [sti for sti in concept_post.get("onlysearch", []) if sti["lang"] == language_name]:
            
        # Term
        term = search_term_information["term"]
        
        #Pos? (Probably not needed, so skip)
        
        search_term_information_list.append(SearchTermInformation(term = term))
        
    return search_term_information_list



def get_see_also_or_see_under_for_language(language_name, concept_post, concept_posts, what_kind_of_see):
    """
    Extract a list of see_also information tuples from the concept post for language

    A concept_post contains the keys "seealso" and "seeunder", which is a list of terms from the same source.
    The relevant information is here
    packaged into the SeeInformation named tuple
    
    Returns:
    list:List of SeeInformation named-tuples.
    """
    
    see_list = []
    for see_info in [si for si in concept_post.get(what_kind_of_see, []) if si["lang"] == language_name]:
        term = see_info["term"]
        homonym_nr = see_info.get("homonym", None)
        
        target = __construct_target_text_for_swedish_reference(term, concept_posts, homonym_nr, language_name)
        
        see_list.append(SeeInformation(term = term, target=target))
    
    return see_list
