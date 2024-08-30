import json
from typing import Any
from urllib.parse import urlparse
from lingua import Language, LanguageDetectorBuilder
import ipaddress

def safe_division(a: int, b: int) -> float:
    return a / b if b != 0 else 0.0

def detect_language(text: str):
    """Detect the language of a text"""
    detector = LanguageDetectorBuilder.from_all_languages().build()
    l = detector.detect_language_of(text)
    if l is Language.ENGLISH:
        return "en"
    elif l is Language.FRENCH:
        return "fr"
    else:
        return "other"

'''
def get_keywords_spacy(text:str) -> list[str]:
    import spacy
    #'extracted_keywords': extracted_keywords,
    # https://towardsdatascience.com/keyword-extraction-process-in-python-with-natural-language-processing-nlp-d769a9069d5c

    # Spacy: 34 dependancies ... 
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)
    extracted_keywords = [ent.text for ent in doc.ents]
    return extracted_keywords
'''

def read_file(file_path: str, binary: bool = False) -> str:
    """Read a file and return its content."""
    mode = 'rb' if binary else 'r'
    with open(file_path, mode) as file:
        return file.read()

def read_json(file_path: str) -> dict[str, Any]:
    """Read a JSON file and return its content."""
    with open(file_path, 'r') as file:
        return json.load(file)
    
def ipv4_in_subnet(ip:str, subnet:str) -> bool:
    ipv4 = ipaddress.IPv4Address(ip)
    subnetv4 = ipaddress.IPv4Network(subnet)
    return ipv4 in subnetv4

def if_exists(dict:dict[str, Any], key:str|None, replacement:Any):
    if key and key in dict.keys():
        return dict[key]
    else:
        return replacement
    
def is_intersection(l1:list[Any], l2:list[Any]) -> bool:
    for el in l1:
        if el in l2:
            return True
    return False

def get_hostname(url:str)-> str:
    """Extracts hostname of a string if it is an url else returs the string
    """
    hostname = urlparse(url).hostname 
    if hostname:
        return hostname
    return url

    
