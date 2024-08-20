
import json
import re

from pylookyloo import Lookyloo


def get_uuid(url: str) -> str:
    if url.startswith("https://lookyloo.circl.lu/tree/"):
        return url.rstrip('/').split('/')[-1]

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
    # Check if string is a valid URL
    url_pattern = re.compile(
        r'^(https?:\/\/)?(www\.)?([a-zA-Z0-9_\-]+\.)+[a-zA-Z]{2,}\/?.*$'
    )
    return bool(url_pattern.match(string))

def is_uuid(string):
    # Check if string is a valid UUID
    uuid_pattern = re.compile(
        r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
    )
    return bool(uuid_pattern.match(string))
'''
def get_categorized_uuids():
    looky = Lookyloo()
    dicti = looky.get_categories_captures()
    with open('uuid_file.json', 'w') as file:
        json.dump(dicti, file)
'''


urls = {
    #'parking_not_ip' : get_list('data/lists/pp_typosquatter.txt'),
    'other': get_list('data/lists/non_parking.txt').extend(get_list('data/lists/urls')),
    'ovh': get_list('data/lists/ovh_captures.txt')

}
uuids = {key : [] for key in urls.keys()}

uuid_file = "data/output/uuids.json"
label = "standard"
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



    