import unittest
import os
from .test_sac_mapper import BasicSacTest
from archetech.spirit.sac_mapper import SACMapper
from archetech.spirit.mapping_solution import verifyOutput
import shutil

class SacTest(BasicSacTest):
    def sac_generic(self,R,C,k,benchfile,benchfile_dir):
        newObj = SACMapper(benchfile_dir+benchfile,self.benchdir,'logs.txt', True, True)
        newObj.mapBenchmark(R, C, k)
        outfile = 'Cr_{}_{}_k{}_{}.v'.format(R,C,k,benchfile)
        res,out = verifyOutput(
            benchfile_dir+benchfile, \
            self.benchdir+outfile,
            self.benchdir
        )
        file_out = '{} and {} are different. \n'.format(benchfile_dir+benchfile,self.benchdir+outfile)+\
                    'Verification failed'
        self.assertEqual(res, True, file_out)


class SacAdderAll(SacTest):
    
    def test_adder_all(self):
        benchfile = 'full_adder_1bit.v'
        benchfile_dir = "./tests/fixtures/"
        klist = [2,3]
        dims = [6,8,12,16]
        
        for k in klist:
            for r in dims:
                for c in dims:
                    self.sac_generic(r,c,k,benchfile,benchfile_dir)
    
class SacCm151aAll(SacTest):
    def test_cm151a_all(self):
        benchfile = 'cm151a.blif'
        benchfile_dir = "./tests/fixtures/"
        klist = [2,3,4]
        dims = [12,16]
        
        for k in klist:
            for r in dims:
                for c in dims:
                    self.sac_generic(r,c,k,benchfile,benchfile_dir)
    
    

if __name__ == "__main__":
    unittest.main()