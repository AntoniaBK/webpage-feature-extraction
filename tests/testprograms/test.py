def extract_parking_services():
    from feature_extractor.helpers import read_json

    ps = read_json("data/blacklists/parking_services.json")
    with open("data/blacklists/new.txt", 'w') as f:
        f.write('{\n')
        for k in ps.keys():
            f.write(f'\t"{k}": None,\n')
        f.write('\t"END": None\n}')

def test_dns(domain):
    import dns.name
    import dns.resolver
    answ = dns.resolver.resolve(domain, "A")
    loc = list()
    for rdata in answ: # type: ignore
        loc.append(rdata.to_text())
    print(loc)
    return loc

def test_languages(text:str):
    from lingua import Language, LanguageDetectorBuilder
    detector = LanguageDetectorBuilder.from_all_languages().build()
    l = detector.detect_language_of(text)
    print(l)

import os
from bs4 import BeautifulSoup
import spacy
from feature_extractor.feature_extractor import FeatureExtractor
from feature_extractor.helpers import ipv4_in_subnet, read_json
from feature_extractor.main import main
from feature_extractor.zip_processor import ZipProcessor
# Start with loading all necessary libraries
import numpy as np
import pandas as pd
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
#test_languages("Textbaustein")
#dns = test_dns('dan.com')
# dan testcapture should be true
#a = ["3.64.163.50/32", "52.58.78.16/32"]
#for i in a : 
    #print(ipv4_in_subnet("3.64.163.50", i))
 #   pass
'''
queue = queue.Queue()
queue.add("folder")
tags = []
while folder = queue.next():
    tags = tags + end_of(folder) # after the last /
    for file in x:
        if endswith(".zip"):
            get_infos()
        else:
            path = folder + file
            if path.isFolder():
                queue.addPath

from feature_extractor.zip_processor import ZipProcessor

#cpt1 = ZipProcessor("tests/captures/capture.zip")
cpt1 = ZipProcessor("tests/captures/unternehmen_doxallia.zip")
extractor1 = FeatureExtractor(cpt1)
obs1 = extractor1.extract_features()
cpt1.delete_extracted_folder()
print(obs1)
'''
# main()

def makeWordcloud(text):
    wordcloud = WordCloud().generate(text)

    # Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()

def processPPs():
    i=0
    dirs = ["/home/antonia/Documents/Testcaptures/en/parking-page",
            "/home/antonia/Documents/Testcaptures/others", 
            "/home/antonia/Documents/Testcaptures/fr/parking_page"]
    keywords = {}
    for dir in dirs:
        for cpt in os.listdir(dir):
            if cpt.endswith('.zip'):
                keywords.update(getWordsForCapture(os.path.join(dir, cpt)))
                i+=1
                print(i)
    print(keywords)
    all_keywords = ' '.join([' '.join(words) for words in keywords.values()])
    makeWordcloud(all_keywords)

def getWordsForCapture(path):
    cpt = ZipProcessor(path)
    soup = BeautifulSoup(cpt.get_html(), features='lxml')
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(soup.text)
    extracted_keywords = [ent.text for ent in doc.ents]
    return {cpt.get_uuid(): extracted_keywords}

processor = ZipProcessor("tests/captures/capture.zip")
extractor = FeatureExtractor(processor)
extractor.har_features()
print(extractor.get_observation())
processor.delete_extracted_folder()