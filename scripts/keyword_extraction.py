import csv
import os
import queue
import re
import string
from typing import Any
from nltk.stem.snowball import SnowballStemmer
 
snow_stemmer = SnowballStemmer(language='french')
from bs4 import BeautifulSoup
from feature_extractor.helpers import read_json
from feature_extractor.zip_processor import ZipProcessor
from wordcloud import WordCloud
import matplotlib.pyplot as plt


dirs = {"en":"data/captures/Testcaptures/parking-page/en",
        "fr": "data/captures/Testcaptures/parking-page/fr",
        "all": "data/captures/Testcaptures/parking-page"}

# Stopwords from https://countwordsfree.com/stopwords
stop_en = read_json("data/lists/stop_words_english.json")['list']
stop_fr = read_json("data/lists/stop_words_french.json")["list"]

def remove_stopwords(l:list, stopwords:list)-> list[str]:
    return [w for w in l if w not in stopwords]

def splitting(s:str)-> list[str]:
    s = s.translate(str.maketrans('', '', string.punctuation))
    return re.split(';|,| |\n|\\|\'|\t', s)

def get_captures_in_subfolders(capture_dir:str)-> list[str]:
    captures = []
    folder_queue = queue.Queue()
    folder_queue.put(capture_dir)
    while not folder_queue.empty():
        capture_dir = folder_queue.get()
        if os.path.isdir(capture_dir):
            for capture_file in os.listdir(capture_dir):
                if capture_file.endswith(".zip"):
                    captures.append(os.path.join(capture_dir, capture_file))
                elif os.path.isdir(os.path.join(capture_dir, capture_file)):
                    folder_queue.put(os.path.join(capture_dir, capture_file))
    return captures

def get_captures_in_folder(dir:str)-> list[str]:
    captures = []
    if os.path.isdir(dir):
        for file in os.listdir(dir):
            if file.endswith('.zip'):
                captures.append(os.path.join(dir, file))
    return captures

def process_file(filepath:str, stop:list)-> list[str]:
        cpt = ZipProcessor(filepath)  
        soup = BeautifulSoup(cpt.get_html(), features='lxml')
        words = remove_stopwords(splitting(soup.get_text()), stop)
        words = [snow_stemmer.stem(w) for w in words]
        cpt.delete_extracted_folder()
        return words

def make_wordcloud(d:dict[str, Any], name:str):
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(d)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig(f'data/output/wordclouds/{name}.png')


#en = get_captures_in_subfolders(dirs["en"])
fr = get_captures_in_subfolders(dirs["fr"])

words = {}

#all = get_captures_in_folder(dirs["all"]) + en + fr


for cpt in fr:
    for w in process_file(cpt, stop_en):
        if len(w) > 20 or len(w) < 4:
            continue
        w = w.lower()
        if w in words.keys():
            words[w] += 1
        else:
            words[w] = 1

make_wordcloud(words, "french4")
csv_file = 'data/output/wordclouds/french4.csv'
fieldnames = ['keyword', 'frequency']
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for key in words.keys():
        if words[key] > 10:
            writer.writerow({'keyword': key, 'frequency': words[key]})

