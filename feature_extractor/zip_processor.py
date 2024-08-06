
import os
import shutil
from typing import Any
import zipfile
from io import StringIO
from feature_extractor.capture_processor import CaptureProcessor
from feature_extractor.helpers import read_file, read_json
from pylookyloo import Lookyloo

class ZipProcessor(CaptureProcessor):
    def __init__(self, capture_file):
        if not os.path.exists(capture_file):
            raise FileNotFoundError(f"The path {capture_file} does not exist.")
        self.capture_file = capture_file
        self.raw_data = self._load_capture()
        self.tags = []

    def _load_capture(self) -> str:
        with zipfile.ZipFile(self.capture_file, 'r') as zip_ref:
            folder = os.path.splitext(self.capture_file)[0]
            self.folder = folder # not fine here
            zip_ref.extractall(folder)

        extracted_folders = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]

        if len(extracted_folders) != 1:
            raise RuntimeError("Expected exactly one folder inside the ZIP file, but found multiple or none.")

        return os.path.join(folder, extracted_folders[0])
    
    def delete_extracted_folder(self):
        shutil.rmtree(self.folder)

    def get_uuid(self) -> str:
        return read_file(os.path.join(self.raw_data, 'uuid'))
    
    def get_capture_settings(self) -> dict[str, Any]:
        return read_json(os.path.join(self.raw_data, 'capture_settings.json'))

    def get_html(self) -> str:
        return read_file(os.path.join(self.raw_data, '0.html'))

    def get_har(self) -> str:
        return read_file(os.path.join(self.raw_data, '0.har.gz'), binary=True)

    def get_last_redirect(self) -> str:
        return read_file(os.path.join(self.raw_data, '0.last_redirect.txt'))

    def get_cnames(self) -> dict[str, Any]:
        return read_json(os.path.join(self.raw_data, 'cnames.json'))

    def get_ipasn(self) -> dict[str, Any]:
        return read_json(os.path.join(self.raw_data, 'ipasn.json'))

    def get_ips(self) -> dict[str, Any]:
        return read_json(os.path.join(self.raw_data, 'ips.json'))

    def get_tags(self) -> list[str]:
        return self.tags
        #elif os.path.exists(os.path.join(self.raw_data, 'categories')):
         #   tags = read_file(os.path.join(self.raw_data, 'categories')).splitlines()
        #return tags
        
    def set_tags(self, tags: list[str]):
        # check tags
        self.tags = tags

    def get_redirects(self)  -> dict[str, Any]:
        redirects = {}
        lookyloo = Lookyloo()
        if lookyloo.is_up:
            redirects = lookyloo.get_redirects(self.get_uuid())
        return redirects
