#Importerar saker
import sys
import xml.etree.ElementTree as ET


METAPOST_1 = """metapost
Status publicerad
"""

METAPOST_2 = """
Titel.dokumentnr
Titel.överordnad
Utgivningsår 2020
Utgåvenr
ISBN-kod
ISSN-kod
Bakgrund Lexin är en kombination av lexikon och ordböcker som har tagits fram för användning i primärt invandrarundervisning.
Sekretariatskommentar
URL http://sprakresurser.isof.se/lexin/
URL-datum 2022-05-05
Utgivare.1.nu.organisation Institutet för språk och folkminnen
Utgivare.1.nu.författare
Utgivare.1.nu.kontaktperson Rickard Domeij
Utgivare.1.nu.e-post sprakteknologi@isof.se
Tolka.OKGR-märkning baraOmInteOrdklassSjälvklar/annarsOckså
Tolka.skillnadTermSynonym.förvalt troligenIngenSkillnad
Tolka.skillnadTermSynonym.språkkod troligenIngenSkillnad
"""

#Funktion som printar en textrad i NTRF-format en separat fil
#lang: välj mellan baselang eller targetlang (källspråk eller målspråk)
#tagname: ange namnet på vad tagen heter i XML-filen, tex "Meaning", "Comment", osv. Ange som sträng
#NTRF_name välj vad raden ska ha för tag i NTRF-formatet, kan tex svTE (svensk term), enDF (engelsk definition) eller fiAN (finsk anmärkning)
#outfile: lägger in i en separat fil (enligt det som står i "with open")
def print_text_row(lang, tagname, NTRF_name, outfile):
    for tag in lang.iter(tagname):
        if tag != None: #Maria kanske kan förklara den här raden
            if tag.text:
                print(NTRF_name + tag.text, file = outfile)
                
def get_meta_data(collection_nr, title):
    return METAPOST_1 + "Källid " + str(collection_nr) + "\nTitel " + title + \
        "\nTitel.kortform " + title + METAPOST_2

def parse_file(infile_name, outfile_name, collection_nr, title, language):
    tree = ET.parse(infile_name) #skriv sökvägen till filen som ska importeras inom parantesen
    root = tree.getroot()
    
    # Förbered för homografnummer
    word_occ_dict = {}
    for word in root.iter('Word'):
        word_lower = word.attrib["Value"].lower()
        if word_lower not in word_occ_dict:
                word_occ_dict[word_lower] = 0
        word_occ_dict[word_lower] = word_occ_dict[word_lower] + 1

    homograph_dict = {}
    with open(outfile_name, 'w') as outfile: #döper ny fil som det nedan ska läggas in i. OBS döp inte filen till nåt som redan finns på dator för då skrivs det över
                    
        print(get_meta_data(collection_nr, title), file = outfile)
        
        for word in root.iter('Word'):
            print("svTE " + word.attrib["Value"], file = outfile) #printar det svenska ordet och strängen "svTE"
            
            # Hantera homografer
            word_lower = word.attrib["Value"].lower()
            if word_occ_dict[word_lower] > 1: # Homografer finns
                if word_lower not in homograph_dict:
                    # inte givit homografnummer för annan homograf förut
                    homograph_dict[word_lower] = 1
                else:
                    homograph_dict[word_lower] = homograph_dict[word_lower] + 1
                print("HONR " + str(homograph_dict[word_lower]), file = outfile)
                        
            for baselang in word.iter("BaseLang"): #definierar att vi är under BaseLang (svenska) i XML-filen
                print_text_row(baselang, "Meaning", "svFK ", outfile)
                print_text_row(baselang, "Comment", "svAN ", outfile)
                print_text_row(baselang, "Explanation", "svAN ", outfile)
                
                #prinatr uppslagstermer eller "Index" som det heter i XML-filen
                for tag in baselang.iter("Index"):
                    if tag != None: #Maria kanske förklara den här raden
                        if tag.attrib["Value"] != word.attrib["Value"]: #gör så att vi inte printar index som är detsamma som "Word"/"svTE"
                            print("svUPTE " + tag.attrib["Value"], file = outfile)


    #Tar fram översättningarna för de svenska orden
            for targetlang in word.iter("TargetLang"): #definierar att vi är under TargetLang (i det här fallet albanska) i XML-filen
                print_text_row(targetlang, "Translation", language + "TE ", outfile)
                print_text_row(targetlang, "Comment", language + "AN ", outfile)
                print_text_row(targetlang, "Synonym", language + "AN ", outfile)
                print_text_row(targetlang, "Explanation", language + "AN ", outfile)
            print(file = outfile) #blankrad

if __name__ == "__main__":
    parse_file("swe_alb.xml", "../NTRF_files_not_in_rikstermbanken/lexin/lexin_albanska_NTRF.txt", 989001, "Lexin Swedish-Albanian Dictionary (Lexin: Svenskt-albanskt lexikon)", "sq")
    #parse_file("swe_eng.xml", "../NTRF_files_not_in_rikstermbanken/lexin/lexin_engelska_NTRF.txt", 989002, "Lexin Swedish-English Dictionary (Lexin: Svenskt-engelskt lexikon)", "en")
    #parse_file("swe_kmr.xml", "../NTRF_files_not_in_rikstermbanken/lexin/lexin_nordkurdiska_NTRF.txt", 989003, "Lexin Swedish-Northern Kurdish (Lexin: Svenskt-nordkurdiskt lexikon)", "kmr")
    #parse_file("swe_sdh.xml", "../NTRF_files_not_in_rikstermbanken/lexin/lexin_sydkurdiska_NTRF.txt", 989004, "Lexin Swedish-Southern Kurdish (Lexin: Svenskt-sydkurdiskt lexikon)", "sdh")
