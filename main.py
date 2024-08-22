import os
import queue
import csv
import json
import sys
from typing import Any
from feature_extractor.zip_processor import ZipProcessor
from feature_extractor.feature_extractor import FeatureExtractor

parking_keywords = {}
all_rows = {}

def make_observation(path:str, tags:list[str] = []) -> dict[str, Any]|None:
    processor = ZipProcessor(path)
    processor.set_tags(tags)
    extractor = FeatureExtractor(processor)
    try:
        features = extractor.extract_all_features()
        all_rows[features['uuid']] = features
    except Exception as e:
        print(f"Error: {e} in {path}")
        features = None
    finally:
        processor.delete_extracted_folder
        return features
    
def main():
    #capture_dir = 'data/captures/Testcaptures/en/'
    capture_dir = "tests/captures"
    tags = []
    keyword_file = 'data/output/keywords.json'
    json_file = 'data/output/data.json'
    csv_file = 'data/output/data.csv'
    test_observation = make_observation("tests/captures/capture.zip")
    
    if test_observation:
        fieldnames = test_observation.keys()
    else:
        print("Something is not working. Exiting.")
        sys.exit(1)
        
    folder_queue = queue.Queue()
    folder_queue.put(capture_dir)
    mode = 'w' # if not os.path.exists(csv_file) else 'a'
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
                    observation = make_observation(os.path.join(capture_dir, capture_file), tags)
                    if observation:
                        writer.writerow(observation)
                else:
                    folder_queue.put(os.path.join(capture_dir, capture_file))   
                        
    with open(json_file, 'w') as file:
        json.dump(all_rows, file)
    with open(keyword_file, 'w') as file:
        json.dump(parking_keywords, file)

if __name__ == "__main__":
    main()