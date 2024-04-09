# -*- coding: utf-8 -*-
from typing import NamedTuple, Any, Optional, List

"""
Named tuples
-----------
"""

class TermEquivalent(NamedTuple):

    # A term equivalents and its type
    
    term_to_present: str
    annotated_term: Optional[Any] = None
    is_deprecated: Optional[bool] = False
    is_preferred: Optional[bool] = False
    is_admitted: Optional[bool] = False
    is_phrase: Optional[bool] = False
    is_synonym: Optional[bool] = False
    is_formula: Optional[bool] = False
    is_a_standard_term: Optional[bool] = True
    
    
    # Grammatical information
    
    gender: Optional[str] = None
        
    # Number, can be {plural, singular, mass, otherNumber}
    grammar: Optional[str] = None
    
    # Can be
    # {'subst.', 'förled', 'adj.', 'intr. verb', 'verb', 'adv.', 'tr. verb'}
    pos: Optional[str] = None
    
    # Additional term equivalent information
    
    narrowing: Optional[str] = None
    geo: Optional[str] = None
    equivalence: Optional[str] = None
    
    is_abbreviation: Optional[bool] = False
    is_full_form: Optional[bool] = False
    
    homonym: Optional[str] = None
    pronunciation: Optional[str] = None
    source: Optional[str] = None

class LanguageLevelInformation(NamedTuple):
    text_to_present: str
    type: str
    source: Optional[str] =  None


class SearchTermInformation(NamedTuple):
    term: str
    
    # Can be
    # {'subst.', 'förled', 'adj.', 'intr. verb', 'verb', 'adv.', 'tr. verb'}
    pos: Optional[str] = None #TODO: Check if needed, probably not

class SeeInformation(NamedTuple):
    term: str
    target: str
