import os
import queue
import csv
import json
from feature_extractor.zip_processor import ZipProcessor
from feature_extractor.feature_extractor import FeatureExtractor

parking_keywords = {}
all_rows = {}

def main():
    capture_dir = '/home/antonia/Documents/Testcaptures/en/'
    tags = []
    keyword_file = 'data/output/keywords.json'
    json_file = 'data/output/data.json'
    csv_file = 'data/output/data.csv'
    selected_features = ['keywords', 'html', 'har', 'hash', 'host', 'link', 'parking', 'text', 'module']

    all_features = {
        'general': [ # 
            'uuid', 
            'tags', 
            'url'
            ],
        'keywords': [ #
            'number_domain_keywords_en',
            'number_parking_kewords_en', 
            'number_together_in_line_keywords_en', 
            'keyword_in_title', 
            'extracted_keywords' # except
            ],
        'html': [ #
            'presence_of_form',
            'presence_of_nav', 
            'text-aplpha-length', 
            'number-images',
            'number-frames'
            ], 
        'har': [ # Nope
            'third-party-request-ratio', 
            'third-party-data-ratio', 
            'third-party-html-content-ratio', 
            'domainStringSent',
            'initial-response-size', 
            'initial-response-ratio'
            ], 
        'hash': [ #
            'polish_hash', 
            'favicon_hash' #except
            ], 
        'host': [
            'different-final-domain', 
            'ip', 
            'ns', # except
            'number_redirects' # via API
            ], 
        'link': [ #
            'number_links',    
            'number_link_same_domain', 
            'average_link_length', 
            'maximum_link_length', 
            'link-to-text-ratio', 
            'number-non-link-characters'
            ], 
        'parking': [
            'parking',
            'in_circl_pp_warninglists',
            'in_zirngibl_pp_warninglist'
            ],
        'text':[
            'url_in_title', 
            'url_in_text',
            'languages', # except
            'present-contact-info' # except
        ],
        'module':[
            'third_party_requests' # via API
        ]
    }

    fieldnames = []
    for feature in all_features:
        fieldnames.extend(all_features[feature])

    folder_queue = queue.Queue()
    folder_queue.put(capture_dir)
    mode = 'w' # if os.path.exists(csv_file) else 'a'
    count = 15
    with open(csv_file, mode, newline='', encoding='utf-8') as file:        
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if mode == 'w':
            writer.writeheader()

        while not folder_queue.empty():
            capture_dir = folder_queue.get()
            tags = [os.path.basename(capture_dir)]
            for capture_file in os.listdir(capture_dir): # what if not dir
                if count < 1:
                    break
                count -= 1
                print(count)
                
                if capture_file.endswith('.zip'):
                    make_row(os.path.join(capture_dir, capture_file), tags, writer)
                else:
                    folder_queue.put(os.path.join(capture_dir, capture_file))   
                        
    with open(json_file, 'w') as file:
        json.dump(all_rows, file)
    with open(keyword_file, 'w') as file:
        json.dump(parking_keywords, file)

if __name__ == "__main__":
    main()

def make_row(file, tags, writer):
    processor = ZipProcessor(file)
    processor.set_tags(tags)
    extractor = FeatureExtractor(processor)
    try:
        features = extractor.extract_features()
        if features['parking']:
            parking_keywords[features['uuid']] = extractor.get_keywords_spacy()
        all_rows[features['uuid']]= features
        writer.writerow(features)
    except Exception as e:
        print(f"Error: {e} in {file}")
    finally:
        processor.delete_extracted_folder