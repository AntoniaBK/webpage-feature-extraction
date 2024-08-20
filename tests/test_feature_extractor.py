import unittest
from feature_extractor.feature_extractor import FeatureExtractor
from feature_extractor.zip_processor import ZipProcessor

class TestFeatureExtractor(unittest.TestCase):
    def __init__(self):
        cpt1 = ZipProcessor("/tests/captures/capture.zip")
        extractor1 = FeatureExtractor(cpt1)
        self.obs1 = extractor1.extract_features()

        cpt2 = ZipProcessor("/tests/captures/goDaddy_en_.zip")
        extractor2 = FeatureExtractor(cpt2)
        self.obs2 = extractor2.extract_features()

        cpt3 = ZipProcessor("/tests/captures/unternehmen_doxallia.zip")
        extractor3 = FeatureExtractor(cpt3)
        self.obs3 = extractor3.extract_features()

    def test_keywords(self):
        self.assertEqual(self.obs1['number_domain_keywords_en'], 0)

    def test_html(self):
        pass

    def test_har(self):
        pass

    def test_hash(self):
        pass

    def test_host(self):
        pass

    def test_link(self):
        pass

    def test_parking(self):
        pass

    def test_text(self):
        pass

    def test_module(self):
        pass

    
