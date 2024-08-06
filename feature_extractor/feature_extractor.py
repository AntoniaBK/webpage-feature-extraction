import hashlib
import json
import re
import tldextract
import spacy

from typing import Any
from urllib.parse import urlparse
from pylookyloo import Lookyloo
from bs4 import BeautifulSoup

from feature_extractor.blacklist_approach import BlacklistApproach
from feature_extractor.capture_processor import CaptureProcessor
from feature_extractor.helpers import if_exists, ipv4_in_subnet, safe_division, detect_language, read_json

class FeatureExtractor:
    def __init__(self, capture: CaptureProcessor):
        self.capture = capture
        self.html = capture.get_html()
        self.uuid = self.capture.get_uuid()
        self.soup = BeautifulSoup(self.html, features='lxml')
        self.url = self.capture.get_capture_settings()['url']
        self.observation = {
            'uuid': self.uuid,
            'tags': self.capture.get_tags(),
            'url': self.url
        }
        self.list_approach = BlacklistApproach()

    def extract_features(self, selected_features: list[str]|None = None) -> dict[str, Any]:
        
        if not selected_features:
            # all features by default
            selected_features = ['keywords', 'html', 'har', 'hash', 'host', 'link', 'parking', 'text', 'module']

        if 'keywords' in selected_features:
            self._keyword_features()     
        if 'html' in selected_features:
            self._html_features()
        if 'har' in selected_features:
            # self._har_features()
            pass
        if 'hash' in selected_features:
            self._hash_features()
        if 'host' in selected_features:
            self._host_features()
        if 'link' in selected_features:
            self._link_features()
        if 'parking' in selected_features:
            self._parking_features()
        if 'text' in selected_features:
            self._text_features()
        if 'module' in selected_features:
            # self._module_features()
            pass

        return self.observation
    
    def _keyword_features(self):
        """ Count appearance of keywords that are related to parking pages
        :return: array with count of synonyms of domain, parked and where they appear together in one line
        """
        domain_keywords = ['domain', 'site', 'website', 'page', 'webpage']
        # (other languages?)
        parked_keywords = ['registered', 'sold', 'sale', 'parked', 'parking', 'hosted', 'available']
        # other languages might have the same word root
        # keywords of the title, give often lot info about the content
        other_keywords = ['coming', 'soon', 'construction']
        # count how often these words appear, how often together in one line and if they appear in the title.
        features = {
                 'number_domain_keywords_en': 0, 
                 'number_parking_kewords_en': 0, 
                 'number_together_in_line_keywords_en': 0, 
                 'keyword_in_title': False
                 }

        title = self.soup.title.text if self.soup.title else ''
        if title:
            features['keyword_in_title'] = any(keyword in title for keyword in domain_keywords + parked_keywords + other_keywords)

        for text in self.soup.findAll(text=True):
            # gives numbers of lines that contain keywords
            domain = any(keyword in text for keyword in domain_keywords)
            parking = any(keyword in text for keyword in parked_keywords)
            if domain:
                features['number_domain_keywords_en'] += 1
            if parking:
                features['number_parking_kewords_en'] += 1
            if domain and parking:
                features['number_together_in_line_keywords_en'] += 1
        
        self.observation.update(features)

    def get_keywords_spacy(self) -> list[str]:
        #'extracted_keywords': extracted_keywords,
        # https://towardsdatascience.com/keyword-extraction-process-in-python-with-natural-language-processing-nlp-d769a9069d5c

        # Spacy: 34 dependancies ... 
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(self.soup.text)
        extracted_keywords = [ent.text for ent in doc.ents]
        return extracted_keywords
        
    def _html_features(self):
        images = self.soup.find_all('img')
        iframes = self.soup.findAll('iframe')
        self.observation['presence_of_form'] = True if self.soup.input else False
        self.observation['presence_of_nav'] = True if self.soup.nav else False
        self.observation['text-aplpha-length'] = len(str(self.html))
        self.observation['number-frames'] = len(iframes)
        self.observation['number-images'] = len(images) 

    def _parking_features(self):
        self.observation['parking'] = True if "parking-page" in self.capture.get_tags() else False

        circl_warninglist = read_json('data/blacklists/MISP-warninglist-parking-domain-ip.json')

        last_hostname = urlparse(self.capture.get_last_redirect()).hostname # redundant code
        if last_hostname:
            ipv4 = self.capture.get_ips()[last_hostname]['v4'] # redundant code

        dns_info = self.list_approach.dnsResolving(self.url)
        self.observation['ns'] = dns_info['NS'] if 'NS' in dns_info.keys() else None
        #self.observation['in_warninglist'] = self.list_approach.check_warning_list(data=dns_info)

        in_circl_warninglist = False
        for ip in ipv4:
            for subnet in circl_warninglist['list']:
                if ipv4_in_subnet(ip, subnet):
                    in_circl_warninglist = True
                    break
        self.observation['in_circl_pp_warninglists'] = in_circl_warninglist

    def _host_features(self):
        first_hostname = urlparse(self.url).hostname
        last_hostname = urlparse(self.capture.get_last_redirect()).hostname
        self.observation['ip'] = if_exists(self.capture.get_ips(), last_hostname, None)
        self.observation['number_redirects'] = len(self.capture.get_redirects())
        self.observation['different-final-domain'] = False if first_hostname == last_hostname else True

    def _link_features(self):
        last_hostname = urlparse(self.capture.get_last_redirect()).hostname
        links = self.soup.findAll('a')
        link_text_length = sum(len(link.text) for link in links)
        number_text_characters = len(self.soup.text)
        hrefs = [link.get('href') for link in links if link.get('href')]
        total_length = sum(len(href) for href in hrefs)
        self.observation['number_links'] = len(links)
        self.observation['number_link_same_domain'] = sum(1 for href in hrefs if last_hostname in href)
        self.observation['average_link_length'] = safe_division(total_length, len(hrefs))
        self.observation['maximum_link_length'] = max((len(href) for href in hrefs), default=0)
        self.observation['link-to-text-ratio'] = safe_division(link_text_length, number_text_characters)
        self.observation['number-non-link-characters'] = number_text_characters - link_text_length

    def _text_features(self):
        text = self.soup.text
        # self.observation['languages'] = detect_language(text) 
        self.observation['url_in_title'] = True if self.url in (self.soup.title if self.soup.title else '') else False
        self.observation['url_in_text'] = True if self.url in text else False
        # self.observation['present-contact-info']: bool
        

    def _hash_features(self):
        to_hash = "|".join(t.name for t in self.soup.findAll()).encode()
        pl_hash = hashlib.sha256(to_hash).hexdigest()[:32]
        self.observation['polish_hash'] = pl_hash
        #  self.observation['favicon_hash'] = None
    
    def _module_features(self):
        lookyloo = Lookyloo()
        self.observation['third_party_requests'] = bool(lookyloo.trigger_modules(self.uuid))

    def _har_features(self):
        """
        Code is adapted from https://github.com/flaiming/Domain-Parking-Sensors/blob/master/feature_extractor.py
        No idea if it works
        """
        with open(self.capture.get_har(), 'r') as file:
            har = json.load(file)

        domain = har["log"]["pages"][0]["id"]
        ext = tldextract.extract(domain)
        domain = f"{ext.domain}.{ext.suffix}"
        domainNoTLD = ext.domain

        har_features = {
            'third-party-data-ratio': 0.0,
            'third-party-html-content-ratio': 0.0,
            'third-party-request-ratio': 0.0,
            'domainStringSent': 0,
            'initial-response-size': 0,
            'initial-response-ratio': 0.0
        }

        firstparty_data, thirdparty_data = 0, 0
        firstparty_html, thirdparty_html = 0, 0
        firstparty_requests, thirdparty_requests = 0, 0

        for entry in har["log"]["entries"]:
            requestUrl = entry["request"]["url"]
            # ext = tldextract.extract(requestUrl)
            # requestDomain = f"{ext.domain}.{ext.suffix}"

            url_parameters = re.search(r'https?://.*/(.*)', requestUrl)
            if url_parameters and domainNoTLD in url_parameters.group(1):
                har_features['domainStringSent'] += 1

            result = re.search(r'https?://(.*)/.*', requestUrl)
            if result and domain in result.group(1):
                firstparty_requests += 1
                firstparty_data += int(entry["response"]["bodySize"])
                mimeType = entry["response"]["content"].get("mimeType", "")
                if 'text' in mimeType or 'javascript' in mimeType:
                    firstparty_html += entry["response"]["bodySize"]
            else:
                thirdparty_requests += 1
                thirdparty_data += int(entry["response"]["bodySize"])
                mimeType = entry["response"]["content"].get("mimeType", "")
                if 'text' in mimeType or 'javascript' in mimeType:
                    thirdparty_html += entry["response"]["bodySize"]

        har_features['third-party-data-ratio'] = safe_division(thirdparty_data, firstparty_data + thirdparty_data) # (number of bytes)
        har_features['third-party-html-content-ratio'] = safe_division(thirdparty_html, firstparty_html + thirdparty_html)
        har_features['third-party-request-ratio'] = safe_division(thirdparty_requests, firstparty_requests + thirdparty_requests)
        har_features['initial-response-size'] = har["log"]["entries"][0]["response"]["bodySize"]
        har_features['initial-response-ratio'] = safe_division(har_features['initial-response-size'],
                                                            firstparty_data + thirdparty_data)

        self.observation.update(har_features)
