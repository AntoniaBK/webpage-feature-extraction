import json
from typing import Any
from lingua import Language, LanguageDetectorBuilder
import ipaddress

def safe_division(a: int, b: int) -> float:
    return a / b if b != 0 else 0.0

def detect_language(text: str):
    """Detect the language(s) of a text"""
    detector = LanguageDetectorBuilder.from_all_languages().build()
    l = detector.detect_language_of(text)
    return l

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


    
