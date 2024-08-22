import os
import spacy
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from feature_extractor.zip_processor import ZipProcessor

class CaptureProcessor:
    def __init__(self, lang, dirs):
        self.dirs = dirs
        self.lang = lang
        langs = {"en":'en_core_web_sm',
                 "fr": 'fr_core_news_md'}
        self.nlp = spacy.load(langs[lang])

    def process_all(self):
        keywords = {}
        for file in self.get_files(self.dirs):
            try:
                words = self.process_file(file)
                keywords.update(words)
            except Exception as e:
                print(f"Error processing {file}: {e}")
        return keywords

    def get_files(self, dir):
        return [os.path.join(dir, f) for f in os.listdir(dir) if f.endswith('.zip')]

    def process_file(self, filepath):
        cpt = ZipProcessor(filepath)  
        soup = BeautifulSoup(cpt.get_html(), features='lxml')
        doc = self.nlp(soup.get_text())
        extracted_keywords = [ent.text for ent in doc.ents]
        return {cpt.get_uuid(): extracted_keywords}

class WordCloudGenerator:
    def __init__(self, lang, text):
        self.text = text
        self.lang = lang

    def generate(self):
        wordcloud = WordCloud(width=800, height=400).generate(self.text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.savefig(f'data/output/wordcloud_{self.lang}.png')
        plt.show()

# Main script execution

dirs = {#"en":"data/captures/Testcaptures/en/parking-page",
        #"/data/captures/Testcaptures/others", 
        "fr": "data/captures/Testcaptures/fr/parking_page"}
for lang in dirs.keys():
    processor = CaptureProcessor(lang, dirs[lang])
    keywords = processor.process_all()

    # Combine all keywords into a single string
    all_keywords = ' '.join([' '.join(words) for words in keywords.values()])
    print(all_keywords)
    # Generate and display the word cloud
    wordcloud_gen = WordCloudGenerator(lang, all_keywords)
    wordcloud_gen.generate()
