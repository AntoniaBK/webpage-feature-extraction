from pylookyloo import Lookyloo
import os

from feature_extractor.helpers import read_json
from tests.testprograms.capturemaker import get_uuid

def save_file(path, uuid):
    lookyloo = Lookyloo()
    if lookyloo.is_up:
        zip_data = lookyloo.get_complete_capture(uuid)
        with open(f'{path}/{uuid}.zip', 'wb') as f:
            f.write(zip_data.getvalue())

def get_list(path:str) -> list[str]:
     with open(path, 'r') as file:
        lines = file.readlines()
        return [line.strip() for line in lines]

parking_not_in_warninglist = {	#  done
	'en' :[
    "200e85d7-6410-42ae-ae38-9957f2e0f031", # en (redirect godaddy)
    "2cf20207-a82d-4eda-804f-51fa59cce0eb", # en porkbun
    "c2199d6b-c299-45b4-bab2-403e4f93ff9d", # en parallels
    "eacf7091-2cf9-4521-8c7e-5579f2c0ab60", # en
    "c9a4a3b8-d86f-4d3f-9e7b-bc7eaa70d66e", # en porkbun
    "9e513e57-62a1-428d-b5c4-09007ac33042", # en (redirect inwx )
    "540927f6-e0a2-43bd-b06c-7f584cba67d5", # en (redirect nicsell)
    "f9a1b414-e04b-453a-a5fd-db2001497ba6", # en & arabic
    "1a130385-8409-4777-9203-e27acad91251" # en (redirect domain-auktionen.info)
],
'de' :[
    "eed3e57f-567c-4eee-bb4e-d44b2db02b7c", # de 
    "dd4da385-82f0-48b6-83af-3ec69341186d", # de
    "365f6402-9d61-4026-aba7-130487f25ef3", # de
    "31552400-cde9-4f5f-9c1a-cdb6371e3c3e" # de ("hier entsteht eine neue Internetpräsenz")
],
'fr': [
    "e49b46ab-127e-484b-9732-8157c2036faa" # fr 
]
}
parking = {
    'en' : ["https://lookyloo.circl.lu/tree/05cbc3cf-66d2-4a4f-8ef0-7376dd2c8d8c"],
    'de': ["https://lookyloo.circl.lu/tree/0586ab2b-11ac-4072-af66-153fee9632d8"],
    'fr': ["https://lookyloo.circl.lu/tree/e636bdda-66af-4e81-b240-a15069df5d20"] 
}
i=0

uuids = get_list("data/lists/ovh_captures.txt")
folder = "fr"

for line in uuids :
    if line == "en:":
        folder = "en"
    if line =="STOP":
        break
    uuid = get_uuid(line)
    save_file(f"data/captures/Testcaptures/ovh/{folder}", uuid)
    i+=1
    print(i)