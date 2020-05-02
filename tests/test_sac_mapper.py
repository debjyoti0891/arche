import unittest
import os
from archetech.spirit.sac_mapper import SACMapper
from archetech.spirit.mapping_solution import verifyOutput
import shutil


class BasicSacTest(unittest.TestCase):
    def setUp(self):
        # Create test directory
        self.benchdir = "./tests/genfiles/"
        print("Creating test directory: {}".format(self.benchdir))
        if not os.path.exists(self.benchdir):
            os.makedirs(self.benchdir)
    
    # def tearDown(self):
    #     # remove generated files
    #     print("Removing test directory: {}".format(self.benchdir))
    #     shutil.rmtree(self.benchdir)


class SacSmallTest(BasicSacTest):
    def test_sac_adder_v(self):
        benchfile = "./tests/fixtures/full_adder_1bit.v"
        newObj = SACMapper(benchfile,self.benchdir,'logs.txt', True, True)
        newObj.mapBenchmark(8, 8, 2)
        res,out = verifyOutput(benchfile, \
            'tests/genfiles/Cr_8_8_k2_full_adder_1bit.v.v', self.benchdir)
        if not res:
            print(out)
        self.assertEqual(res, True, "Generated file is not functionally same")
    
    def test_sac_cm82a(self):
        benchfile = "./tests/fixtures/cm82a.blif"
        newObj = SACMapper(benchfile,self.benchdir,'logs.txt', True, True)
        newObj.mapBenchmark(8, 8, 2)
        res,out = verifyOutput(benchfile, \
            'tests/genfiles/Cr_8_8_k2_cm82a.blif.v', self.benchdir)
        if not res:
            print(out)
        self.assertEqual(res, True, "Generated file is not functionally same")


class SacTestBig(BasicSacTest):
    def test_sac_c6288(self):
        benchfile = "./tests/fixtures/C6288.blif"
        newObj = SACMapper(benchfile,self.benchdir,'logs.txt', False, True)
        newObj.mapBenchmark(64, 64, 5)
        res,out = verifyOutput(benchfile, \
            'tests/genfiles/Cr_64_64_k5_C6288.blif.v', self.benchdir)
        if not res:
            print(out)
        self.assertEqual(res, True, "Generated file is not functionally same")


if __name__ == "__main__":
    unittest.main()