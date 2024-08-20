'''
Test the abstract class to ensure it enforces the required interface.
This typically involves checking that the abstract methods are not instantiable and that subclasses implement them correctly.
'''
import unittest
from feature_extractor.capture_processor import CaptureProcessor
from abc import ABCMeta

class TestCaptureProcessor(unittest.TestCase):
    def test_abstract_methods(self):
        with self.assertRaises(TypeError):
            CaptureProcessor('dummy_source')

