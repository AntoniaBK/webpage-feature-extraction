import hashlib

from typing import Any
from urllib.parse import urlparse
from pylookyloo import Lookyloo
from bs4 import BeautifulSoup

from feature_extractor.blacklist_approach import BlacklistApproach
from feature_extractor.capture_processor import CaptureProcessor
from feature_extractor.har_features import HARFeaturesExtractor
from feature_extractor.helpers import get_hostname, if_exists, ipv4_in_subnet, is_intersection, safe_division,  read_json

class FeatureExtractor:
    def __init__(self, capture: CaptureProcessor):
        """Initializes the observation

        Adds the following features to observation
        - 'uuid'
        - 'tags'
        - 'url'
        - 'parking'
        """
        self.capture = capture
        self.html = capture.get_html()
        self.uuid = self.capture.get_uuid()
        self.soup = BeautifulSoup(self.html, features='lxml')
        self.url = self.capture.get_capture_settings()['url']
        self.observation = {
            'uuid': self.uuid,
            'tags': self.capture.get_tags(),
            'url': self.url,
            'parking': True if "parking-page" in capture.get_tags() else False
        }
        self.list_approach = BlacklistApproach()

    def extract_all_features(self) -> dict[str, Any]:
        """Calls all methods to add all possible features to obseravation
        """
        
        self.keyword_features()  
        self.language_from_tags()
        self.html_features()
        self.warninglist_feature()
        self.redirect_features()
        self.link_features()
        self.har_features()
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

        title = self.soup.title.text.lower() if self.soup.title else ''
        if title:
            features['keyword_in_title_en'] = any(keyword in title for keyword in domain_keywords + parking_keywords)
            features['stemmed_keyword_in_title'] = any(keyword in title for keyword in stemmed_keywords)

        features.update(stemmed_keywords_features)
        self.observation.update(features)
        
    def html_features(self):
        """ Extracts a set of features from the HTML structure and content

        Adds the following features to observation:
        - 'presence_of_nav'
        - 'text_alpha_length'
        - 'number_frames'
        - 'number_images'
        - 'domain_in_title'
        - 'domain_in_text'
        """
        images = self.soup.find_all('img')
        iframes = self.soup.findAll('iframe')
        self.observation['presence_of_nav'] = True if self.soup.nav else False
        self.observation['text_alpha_length'] = len(list(filter(str.isalnum, self.soup.get_text())))
        self.observation['number_frames'] = len(iframes)
        self.observation['number_images'] = len(images) 

        first_hostname = get_hostname(self.url)
        text = self.soup.get_text()
        title = self.soup.title.text.lower() if self.soup.title else ''
        self.observation['domain_in_title'] = True if first_hostname in title else False
        self.observation['domain_in_text'] = True if first_hostname in text else False 

    def warninglist_feature(self):
        """Checks whether the domain's IP or NS appear on a warninglist

        Adds the following feature to observation:
        - 'in_warning_list'
        """
        last_hostname = get_hostname(self.capture.get_last_redirect())
        ipv4 = self.capture.get_ips()[last_hostname]['v4'] 

        in_warninglist = False
        dns_info = self.list_approach.dnsResolving(last_hostname)
        if 'A' in dns_info.keys():
            dns_corresponding = is_intersection(ipv4, dns_info['A']) 
        else:
            dns_corresponding = False
        if dns_corresponding and 'NS' in dns_info.keys():
            warning = self.list_approach.check_warning_list(data=dns_info)
            in_warninglist = warning['park_ns'] or warning['park_ip']

        circl_warninglist = read_json('data/blacklists/MISP-warninglist-parking-domain-ip.json')
        in_circl_warninglist = False
        for ip in ipv4:
            for subnet in circl_warninglist['list']:
                if ipv4_in_subnet(ip, subnet):
                    in_circl_warninglist = True
                    break
        in_warninglist = in_warninglist or in_circl_warninglist
        self.observation['in_warninglist'] = in_warninglist

    def redirect_features(self):
        """Gets information about redirects to other pages

        Adds the following features to observation:
        - 'number_redirects'
        - 'different_final_domain'
        """
        first_hostname = get_hostname(self.url)
        last_hostname = get_hostname(self.capture.get_last_redirect())

        self.observation['ip'] = if_exists(self.capture.get_ips(), last_hostname, None) # CDN gewichtung warninglist
        self.observation['number_redirects'] = len(self.capture.get_redirects())
        self.observation['different_final_domain'] = False if first_hostname == last_hostname else True

    def link_features(self):
        """Calculates statistics about anchor elements in the HTML

        Adds the following features to observation:
        - 'number_links'
        - 'number_link_same_domain'
        - 'average_link_length_same_domain'
        - 'number_different_link_domains'
        - 'average_link_length'
        - 'maximum_link_length'
        - 'link_to_text_ratio'
        - 'number_non_link_characters'
        """
        last_hostname = get_hostname(self.capture.get_last_redirect())

        links = self.soup.findAll('a')
        link_text_length = sum(len(list(filter(str.isalnum,link.text))) for link in links)
        number_text_characters = len(list(filter(str.isalnum, self.soup.get_text())))
        hrefs = [link.get('href') for link in links if link.get('href')]
        links_same_domain = [href for href in hrefs if last_hostname.lower() in href.lower()]
        total_length_links_same_domain = sum(len(href) for href in links_same_domain)
        total_length = sum(len(href) for href in hrefs)
        self.observation['number_links'] = len(links)
        self.observation['number_link_same_domain'] = len(links_same_domain)
        self.observation['average_link_length_same_domain'] = safe_division(total_length_links_same_domain, len(links_same_domain))
        self.observation['number_different_link_domains'] = len(set(get_hostname(href) for href in hrefs))
        self.observation['average_link_length'] = safe_division(total_length, len(hrefs))
        self.observation['maximum_link_length'] = max((len(href) for href in hrefs), default=0)
        self.observation['link_to_text_ratio'] = safe_division(link_text_length, number_text_characters)
        self.observation['number_non_link_characters'] = number_text_characters - link_text_length
        
    def hash_features(self):
        """Hashes the HTML-tags (helpfull for finding website clones)

        Adds the following feature to observation:
        - 'structural_hash'
        """
        to_hash = "|".join(t.name for t in self.soup.findAll()).encode()
        hash = hashlib.sha256(to_hash).hexdigest()[:32]
        self.observation['structural_hash'] = hash
    
    def har_features(self):
        """Calculates statistics about thirdparty content loaded on the domain

        Adds the following features to observation:
        - "third_party_requests_ratio"
        - "third_party_data_ratio"
        - "third_party_html_content_ratio"
        - "initial_response_size"
        - "initial_response_ratio"
        """
        har = self.capture.get_har()
        har_extractor = HARFeaturesExtractor(har)
        self.observation.update(har_extractor.extract_features())
