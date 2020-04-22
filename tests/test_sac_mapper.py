import unittest
import os
from archetech.spirit.sac_mapper import SACMapper
import shutil


class BasicSacTest(unittest.TestCase):
    def setUp(self):
        # Create test directory
        self.benchdir = "./tests/genfiles/"
        print("Creating test directory: {}".format(self.benchdir))
        if not os.path.exists(self.benchdir):
            os.makedirs(self.benchdir)

class SacAdderTest(BasicSacTest):
    def test_sac_adder_v(self):
        benchfile = "./tests/fixtures/full_adder_1bit.v"
        newObj = SACMapper(benchfile,self.benchdir,'logs.txt', True, True)
        newObj.mapBenchmark(8, 8, 2)
    
class SacSmallTest(BasicSacTest):
    def test_sac_cm151a_blif(self):
        benchfile = "./tests/fixtures/cm151a.blif"
        newObj = SACMapper(benchfile,self.benchdir,'logs.txt', True, True)
        newObj.mapBenchmark(16, 16, 4)

    # def tearDown(self):
    #     # remove generated files
    #     print("Removing test directory: {}".format(self.benchdir))
    #     shutil.rmtree(self.benchdir)

if __name__ == "__main__":
    unittest.main()