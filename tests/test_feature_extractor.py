import unittest
from feature_extractor.feature_extractor import FeatureExtractor
from feature_extractor.zip_processor import ZipProcessor

class TestFeatureExtractor(unittest.TestCase):
    def __init__(self):
        cpt1 = ZipProcessor("/tests/captures/article.zip")
        extractor1 = FeatureExtractor(cpt1)
        self.article = extractor1.extract_all_features()

        cpt2 = ZipProcessor("/tests/captures/parking_page/goDaddy_en_.zip")
        extractor2 = FeatureExtractor(cpt2)
        self.go_daddy = extractor2.extract_all_features()

        cpt3 = ZipProcessor("/tests/captures/doxallia.zip")
        extractor3 = FeatureExtractor(cpt3)
        self.doxallia = extractor3.extract_all_features()

        cpt4 = ZipProcessor("/tests/captures/google.zip")
        extractor4 = FeatureExtractor(cpt4)
        self.google = extractor4.extract_all_features()

        cpt5 = ZipProcessor("tests/captures/parking-page/ad_portal_domain_in_title_and_text.zip")
        extractor5 = FeatureExtractor(cpt5)
        self.ad_portal = extractor5.extract_all_features()

        cpt6 = ZipProcessor("/tests/captures/parking-page/dan.zip")
        extractor6 = FeatureExtractor(cpt6)
        self.google = extractor6.extract_all_features()

    def test_keywords(self):
        self.assertEqual(self.article['number_domain_keywords_en'], 0)

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

    
