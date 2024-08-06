from typing import Any
from feature_extractor.helpers import read_json, ipv4_in_subnet
import dns.name
import dns.resolver

class BlacklistApproach:
    def __init__(self):
        self.parking_domain_ns = read_json("data/blacklists/MISP-warninglist-parking-domain-ip.json")
        self.parking_domain_ip = read_json("data/blacklists/MISP-warninglist-parking-domain-ns.json")
        # self.parking_services = read_json("data/blacklists/parking_services.json")
        
    def check_warning_list(self, domain:str = '', data:dict[str, Any]|None = None) -> dict[str, Any]:
        if not data:
            if domain.strip():
                data = self.dnsResolving(domain)
            else:
                return {'Error': "invalid request"}

        data_keys = list(data.keys())

        to_return = {
            'park_ip': False,
            'park_ns': False,
            'park_service_ip': False,
            'park_service_ns': False
        }
        
        if 'A' in data_keys:
            for a in data['A']:
                for subnet in self.parking_domain_ip['list']:
                    if ipv4_in_subnet(a, subnet):
                        to_return['parking_domains'] = True
                        to_return['park_ip'] = True
                        break

        if 'NS' in data_keys:
            for ns in data['NS']:
                for park in self.parking_domain_ns['list']:
                    if park in ns.lower():
                        to_return['parking_domains'] = True
                        break

        return to_return
    
    def dnsResolving(self, domain:str) -> dict[str, Any]:
        type_request = ['A', 'NS']  # ['A', 'AAAA', 'NS', 'MX']
        result = dict()

        for t in type_request:
            try:
                answer = dns.resolver.resolve(domain, t)
                loc = list()
                for rdata in answer: # type: ignore
                    loc.append(rdata.to_text())
                if len(loc) > 0:
                    result[t] = loc
            except:
                pass
        
        if len(result) == 0:
            result['NotExist'] = True
        else:
            result['NotExist'] = False
        
            if 'NS' in result.keys():
                # Parse NS record to remove end point
                for i in range(0, len(result['NS'])):
                    result['NS'][i] = result['NS'][i][:-1]

        return result
    