from haralyzer import HarParser
from urllib.parse import urlparse

class HARFeaturesExtractor:
    """ 
    according to the har features of parking sensors 2015
    """
    def __init__(self, har_data):
        self.har_parser = HarParser(har_data)
        self.initial_domain = urlparse(self.har_parser.pages[0].entries[0].request.url).netloc # type: ignore

    def is_third_party(self, url):
        domain = urlparse(url).netloc
        return domain != self.initial_domain

    def extract_features(self):
        total_requests = len(self.har_parser.pages[0].entries) # type: ignore
        third_party_requests = 0
        total_data = 0
        third_party_data = 0
        total_html_content = 0
        third_party_html_content = 0
        initial_response_size = 0
        number_redirects = 0

        for entry in self.har_parser.pages[0].entries: # type: ignore
            status = entry['response']['status']
            if status in [301, 302, 303, 307, 308]:
                number_redirects += 1
            url = entry.request.url
            response_size = entry.response.bodySize
            content_type = entry.response.mimeType
            if self.is_third_party(url):
                third_party_requests += 1
                third_party_data += response_size

                if "text/html" in content_type:
                    third_party_html_content += response_size

            if "text/html" in content_type:
                total_html_content += response_size

            total_data += response_size

            if entry == self.har_parser.pages[0].entries[0]: # type: ignore
                initial_response_size = response_size

        # Calculating ratios
        third_party_requests_ratio = (third_party_requests / total_requests) if total_requests else 0
        third_party_data_ratio = (third_party_data / total_data) if total_data else 0
        third_party_html_content_ratio = (third_party_html_content / total_html_content) if total_html_content else 0
        initial_response_ratio = (initial_response_size / total_data) if total_data else 0

        features = {
            "third_party_requests_ratio": third_party_requests_ratio,
            "third_party_data_ratio": third_party_data_ratio,
            "third_party_html_content_ratio": third_party_html_content_ratio,
            "initial_response_size": initial_response_size,
            "initial_response_ratio": initial_response_ratio, 
            "number_redirects": number_redirects
        }

        return features
