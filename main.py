import os
import queue
import csv
import json
import sys
from typing import Any
from feature_extractor.zip_processor import ZipProcessor
from feature_extractor.feature_extractor import FeatureExtractor


def make_observation(path:str, tags:list[str] = []) -> dict[str, Any]|None:
    processor = ZipProcessor(path)
    processor.set_tags(tags)
    extractor = FeatureExtractor(processor)
    try:
        features = extractor.extract_all_features()
    except Exception as e:
        print(f"Error: {e} in {path}")
        features = None
    finally:
        processor.delete_extracted_folder()
        return features
    
def remove_useless_tags(l:list[str])-> list[str]:
    useless_tags = ["captures", "data", "tests", "Testcaptures"]
    for t in useless_tags:
        if t in l:
            l.remove(t)
    return l

def main():
    #capture_dir = 'data/captures/Testcaptures/en/'
    all_rows = {}
    capture_dir = "tests/captures"
    tags = []
    json_file = 'data/output/data.json'
    csv_file = 'data/output/data.csv'
    
    # Test if the extraction works and get fieldnames
    test_observation = make_observation("tests/captures/parking-page/capture.zip")
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

        # Go through folders to get all the captures 
        while not folder_queue.empty():
            capture_dir = folder_queue.get()
            if os.path.isdir(capture_dir):
                tags = remove_useless_tags(capture_dir.split("/"))

                for capture_file in os.listdir(capture_dir): 
                    
                    if capture_file.endswith('.zip'):
                        if count < 1:
                            sys.exit(0)
                        count -= 1
                        print(count)
                        observation = make_observation(os.path.join(capture_dir, capture_file), tags)
                        if observation:
                            writer.writerow(observation)
                            all_rows[observation['uuid']] = observation
                    else:
                        # !there should not be extracted captures... 
                        folder_queue.put(os.path.join(capture_dir, capture_file)) 
                        
    with open(json_file, 'w') as file:
        json.dump(all_rows, file)

if __name__ == "__main__":
    main()