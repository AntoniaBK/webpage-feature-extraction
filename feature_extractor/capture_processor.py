
from abc import ABC, abstractmethod
from typing import Any

class CaptureProcessor(ABC):
    def __init__(self, source):
        self.source = source

    @abstractmethod
    def get_uuid(self) -> str:
        pass
    
    @abstractmethod
    def get_capture_settings(self)-> dict[str, Any]:
        pass

    @abstractmethod
    def get_html(self) -> str:
        pass

    @abstractmethod
    def get_har(self) -> str:
        pass  

    @abstractmethod
    def get_last_redirect(self) -> str:
        pass

    @abstractmethod
    def get_cnames(self)-> dict[str, Any]:
        pass

    @abstractmethod
    def get_ipasn(self)-> dict[str, Any]:
        pass

    @abstractmethod
    def get_ips(self)-> dict[str, Any]:  
        pass 
       
    @abstractmethod
    def get_tags(self) -> list[str]:
        pass
    
    @abstractmethod   
    def set_tags(self, tags: list[str]):
        pass

    @abstractmethod
    def get_redirects(self)-> dict[str, Any]:
        pass

