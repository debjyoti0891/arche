import unittest
import os
from .test_sac_mapper import BasicSacTest
from archetech.spirit.sac_mapper import SACMapper
from archetech.spirit.mapping_solution import verifyOutput
import shutil


class SacTestPart(BasicSacTest):
    def test_sac_cm82a_k2(self):
        benchfile = "./tests/fixtures/cm82a_k2.v"
        newObj = SACMapper(benchfile,self.benchdir,'logs.txt', False, True)
        newObj.mapBenchmark(64, 64, 0, True)
        res,out = verifyOutput(benchfile, \
            'tests/genfiles/Cr_64_64_k0_cm82a_k2.v.v', self.benchdir)
        if not res:
            print(out)
        self.assertEqual(res, True, "Generated file is not functionally same")


class SacTestPartOne(BasicSacTest):
    def test_sac_constmod1(self):
        benchfile = "./tests/fixtures/constmod_1.v"
        newObj = SACMapper(benchfile,self.benchdir,'logs.txt', True, True)
        newObj.mapBenchmark(8, 8, 0, True)
        res,out = verifyOutput(benchfile, \
            'tests/genfiles/Cr_8_8_k0_constmod_1.v.v', self.benchdir)
        if not res:
            print(out)
        self.assertEqual(res, True, "Generated file is not functionally same")
if __name__ == "__main__":
    unittest.main()