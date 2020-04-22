import unittest
import os
from archetech.spirit.mapping_solution import verifyOutput
import shutil


class TestABCVerification(unittest.TestCase):
    def setUp(self):
        # Create test directory
        self.benchdir = "./tests/genfiles/"
        print("Creating test directory: {}".format(self.benchdir))
        if not os.path.exists(self.benchdir):
            os.makedirs(self.benchdir)

    def test_verify_positive(self):
        res,out = verifyOutput('./tests/fixtures/b1.blif', './tests/fixtures/b1.blif',self.benchdir)
        self.assertEqual(res, True)
    
    def test_verify_negative(self):
        res,out = verifyOutput('./tests/fixtures/b1.blif', './tests/fixtures/cm151a.blif',self.benchdir)
        self.assertEqual(res, False)
        
    def tearDown(self):
        # remove generated files
        print("Removing test directory: {}".format(self.benchdir))
        shutil.rmtree(self.benchdir)