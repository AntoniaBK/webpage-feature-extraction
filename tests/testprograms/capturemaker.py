
import json
import re

from pylookyloo import Lookyloo

URL_PATTERN = re.compile(r'^(https?:\/\/)?(www\.)?([a-zA-Z0-9_\-]+\.)+[a-zA-Z]{2,}\/?.*$')
UUID_PATTERN = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$')

def get_uuid(url: str) -> str:
    if url.startswith("https://lookyloo.circl.lu/tree/"):
        return url.rstrip('/').split('/')[-1]

    elif is_uuid(url):
        return url
    else:
        lookyloo = Lookyloo()
        if lookyloo.is_up:
            return lookyloo.submit(url=url, quiet=True)
        else:
            raise Exception('lookyloo not up')
        
def get_list(path:str) -> list[str]:
     with open(path, 'r') as file:
        lines = file.readlines()
        return [line.strip() for line in lines]

def is_url(string):
    """Check if string is a valid URL"""
    return bool(URL_PATTERN.match(string))

def is_uuid(string):
    """Check if string is a valid UUID"""
    return bool(UUID_PATTERN.match(string))
'''
def get_categorized_uuids():
    looky = Lookyloo()
    dicti = looky.get_categories_captures()
    with open('uuid_file.json', 'w') as file:
        json.dump(dicti, file)
'''
def list_processing(file_suffix:str):

    urls = {
        #'parking_not_ip' : get_list('data/lists/pp_typosquatter.txt'),
        'other': get_list('data/lists/non_parking.txt').extend(get_list('data/lists/urls')),
        'ovh': get_list('data/lists/ovh_captures.txt')

    }
    uuid_file = f"data/output/uuids_{file_suffix}.json"
    label = "standard"
    uuids = {key : [] for key in urls.keys()}
    for key in urls:
        for url in urls[key]:
            if str(url).strip():
                if is_url(url):
                    if key in uuids.keys():
                        uuids[key].append(get_uuid(url))
                    else:
                        raise Exception('Unknown key')
                else:
                    label = url 
    with open(uuid_file, 'w') as file:
        json.dump(uuids, file)

def non_parking_uuids():
    uuid_file = "data/output/uuids_institution.json"
    url_file = "data/lists/non_parking.txt"
    uuids = {'institution' :[]}
    with open(url_file, 'r') as file:
        urls = file.readlines()
        for url in urls:
            uuids['institution'].append(get_uuid(url))
    with open(uuid_file, 'w') as file:
        json.dump(uuids, file)

ls = get_list("data/lists/urls")
uuids = {"50_majestic":[]}
for url in ls:
    uuids['50_majestic'].append(get_uuid(url))
with open("data/lists/uuids_of_famous_urls.json", "w") as file:
    json.dump(uuids, file)

    