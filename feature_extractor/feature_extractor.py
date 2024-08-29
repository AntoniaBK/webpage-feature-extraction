import hashlib

from typing import Any
from urllib.parse import urlparse
from pylookyloo import Lookyloo
from bs4 import BeautifulSoup

from feature_extractor.blacklist_approach import BlacklistApproach
from feature_extractor.capture_processor import CaptureProcessor
from feature_extractor.har_features import HARFeaturesExtractor
from feature_extractor.helpers import if_exists, ipv4_in_subnet, is_intersection, safe_division,  read_json

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

    def extract_all_features(self) -> dict[str, Any]:
        
        self.keyword_features()  
        self.language_from_tags()
        self.html_features()
        self.dns_features()
        self.parking_features()
        self.host_features()
        self.link_features()
        self.text_features()
        self.har_features()
        # self.module_features()
        self.hash_features()

        return self.observation
    
    def get_observation(self):
        return self.observation
    
    def language_from_tags(self):
        """ Gets language of the website from the tags

        Adds the following feature to observation:
        - 'language'
        """
        tags = self.capture.get_tags()
        if 'en' in tags:
            self.observation['language'] = 'en'
        elif 'fr' in tags:
            self.observation['language'] = 'fr'
        else:
            self.observation['language'] = 'unknown'

    def keyword_features(self):
        """ Count appearance of keywords that are related to parking pages

        Adds the following features to observation:
        - 'number_domain_keywords_en':
        The sum of the frequency of the words "domain", "website", "site", "page" and "webpage"
        - 'number_parking_kewords_en':
        The sum of the frequency of the words "parked", "parking", "registered", "sold", "sale", "hosted" and "available"
        - 'number_together_in_line_keywords_en':
        Number of lines that contain at least one word of each of the two previous group of words together.
        - 'keyword_in_title_en':
        Does any contextual synonym of "parking" or "domain" appear in the webiste's title? 
        - 'stemmed_keyword_in_title':
        Does any stemmed keyword appear in the title?
        - The frequency of stemmed keywords per keyword (pattern: f'kword_{word}')
        """
        stemmed_keywords = ['auction',
                            'domain',
                            'regist',
                            'price',
                            'offer',
                            'servic',
                            'host',
                            'websit',
                            'contact',
                            'site',
                            'transfer',
                            'héberge',
                            'internet',
                            'serveur',
                            'découvr',
                            'mainten'
                            ]
        stemmed_keywords_features = {f'kword_{k}':0 for k in stemmed_keywords}

        domain_keywords = ['domain', 'site', 'website', 'page', 'webpage']
        parking_keywords = ['registered', 'sold', 'sale', 'parked', 'parking', 'hosted', 'available']

        features = {
                'number_domain_keywords_en': 0, 
                'number_parking_kewords_en': 0, 
                'number_together_in_line_keywords_en': 0, 
                'keyword_in_title_en': False,
                'stemmed_keyword_in_title': False
                 }

        for text in self.soup.findAll(text=True):
            text = text.lower()
            
            for keyword in stemmed_keywords:
                stemmed_keywords_features[f'kword_{keyword}'] += text.count(keyword)

            domain = sum(text.count(key) for key in domain_keywords)
            parking = sum(text.count(key) for key in parking_keywords)
            if domain:
                features['number_domain_keywords_en'] += domain
            if parking:
                features['number_parking_kewords_en'] += parking
            if domain and parking:
                features['number_together_in_line_keywords_en'] += 1

        title = self.soup.title.text if self.soup.title else ''
        if title:
            features['keyword_in_title_en'] = any(keyword in title for keyword in domain_keywords + parking_keywords)
            features['stemmed_keyword_in_title'] = any(keyword in title for keyword in stemmed_keywords)

        self.observation.update(features)
        
    def html_features(self):
        images = self.soup.find_all('img')
        iframes = self.soup.findAll('iframe')
        self.observation['presence_of_form'] = True if self.soup.input else False
        self.observation['presence_of_nav'] = True if self.soup.nav else False
        self.observation['text-aplpha-length'] = len(str(self.html))# alpha-numeric?
        self.observation['number-frames'] = len(iframes)
        self.observation['number-images'] = len(images) 

    def dns_features(self):
        last_hostname = urlparse(self.capture.get_last_redirect()).hostname # redundant code
        if not last_hostname:
            last_hostname = self.capture.get_last_redirect()

        ipv4 = self.capture.get_ips()[last_hostname]['v4'] # redundant code

        
        dns_info = self.list_approach.dnsResolving(last_hostname)
        # dns_info might not be corresponding to the original capture as the captures can be some weeks to months old
        if 'A' in dns_info.keys():
            self.observation["dns_corresponding"] = is_intersection(ipv4, dns_info['A']) 
        else:
            self.observation["dns_corresponding"] = False
        if 'NS' in dns_info.keys():
            # check if the dns_info corresponds to the original capture and ns-info exists
            self.observation['ns'] = dns_info['NS']
            warning = self.list_approach.check_warning_list(data=dns_info)
            self.observation['in_ns_warninglist'] = warning['park_ns']
            self.observation["in_ip_warninglist"] = warning["park_ip"]
        else:
            self.observation['ns'] = None
            self.observation['in_ns_warninglist'] = None
            self.observation["in_ip_warninglist"] = None

    def parking_features(self):
        self.observation['parking'] = True if "parking-page" in self.capture.get_tags() else False

        circl_warninglist = read_json('data/blacklists/MISP-warninglist-parking-domain-ip.json')

        # redundant code
        last_hostname = urlparse(self.capture.get_last_redirect()).hostname 
        if not last_hostname:
            last_hostname = self.capture.get_last_redirect()
        ipv4 = self.capture.get_ips()[last_hostname]['v4']
        
        in_circl_warninglist = False
        for ip in ipv4:
            for subnet in circl_warninglist['list']:
                if ipv4_in_subnet(ip, subnet):
                    in_circl_warninglist = True
                    break
        self.observation['in_circl_pp_warninglists'] = in_circl_warninglist

    def host_features(self):
        first_hostname = urlparse(self.url).hostname
        last_hostname = urlparse(self.capture.get_last_redirect()).hostname
        self.observation['ip'] = if_exists(self.capture.get_ips(), last_hostname, None) # CDN gewichtung warninglist
        self.observation['number_redirects'] = len(self.capture.get_redirects())
        self.observation['different-final-domain'] = False if first_hostname == last_hostname else True

    def link_features(self):
        last_hostname = urlparse(self.capture.get_last_redirect()).hostname
        links = self.soup.findAll('a')
        link_text_length = sum(len(link.text) for link in links)
        number_text_characters = len(self.soup.text)
        hrefs = [link.get('href') for link in links if link.get('href')]
        total_length = sum(len(href) for href in hrefs)
        self.observation['number_links'] = len(links)
        self.observation['number_link_same_domain'] = sum(1 for href in hrefs if last_hostname in href)
        self.observation['number_different_link_domains'] = len(set(urlparse(href).hostname for href in hrefs))
        self.observation['average_link_length'] = safe_division(total_length, len(hrefs))
        self.observation['maximum_link_length'] = max((len(href) for href in hrefs), default=0)
        self.observation['link-to-text-ratio'] = safe_division(link_text_length, number_text_characters)
        self.observation['number-non-link-characters'] = number_text_characters - link_text_length

    def text_features(self):
        text = self.soup.text
        # self.observation['languages'] = detect_language(text) 
        self.observation['url_in_title'] = True if self.url in (self.soup.title if self.soup.title else '') else False
        self.observation['url_in_text'] = True if self.url in text else False 
        
    def hash_features(self):
        to_hash = "|".join(t.name for t in self.soup.findAll()).encode()
        pl_hash = hashlib.sha256(to_hash).hexdigest()[:32]
        self.observation['polish_hash'] = pl_hash
        # ToDo: self.observation['favicon_hash'] = capture.get_favicon_hashes
    
    def module_features(self):
        lookyloo = Lookyloo() 
        try:
            if lookyloo.is_up:
                # does it work like this
                self.observation['third_party_requests'] = bool(lookyloo.trigger_modules(self.uuid))
            else:
                raise Exception("Lookyloo not reachable")
        except Exception as e:
            # e.g. uuid is not from  lookyloo.circl.lu
            # what to do with e? print?
            self.observation['third_party_requests'] = None

    def har_features(self):
        har = self.capture.get_har()
        har_extractor = HARFeaturesExtractor(har)
        self.observation.update(har_extractor.extract_features())
