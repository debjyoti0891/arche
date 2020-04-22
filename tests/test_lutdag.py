import unittest
import os
from archetech.spirit.lutdag import LutGraph
import shutil


class BaseLUTTest(unittest.TestCase):
    def setUp(self):
        # Create test directory
        self.benchdir = "./tests/genfiles/"
        print("Creating test directory: {}".format(self.benchdir))
        if not os.path.exists(self.benchdir):
            os.makedirs(self.benchdir)

    def partitioning(self):
        k_list = [2, 3, 4]
        for k in k_list:
            lG = self.graph.genLutGraph(k)
            self.assertIsNotNone(lG, "LUT graph should be generated")

    def tearDown(self):
        # remove generated files
        print("Removing test directory: {}".format(self.benchdir))
        shutil.rmtree(self.benchdir)


class TestSmallLUT(BaseLUTTest):
    def test_load(self):
        debug = True
        benchfile = "./tests/fixtures/b1.blif"
        self.graph = LutGraph(self.benchdir, benchfile, debug)
        self.partitioning()


class TestLargeLUT(BaseLUTTest):
    def test_load(self):
        debug = False
        benchfile = "./tests/fixtures/c6288.blif"
        self.graph = LutGraph(self.benchdir, benchfile, debug)
        self.partitioning()


class TestInvalidLUT(BaseLUTTest):
    def test_partitioning(self):
        benchfile = "./tests/fixtures/C7552.blif"
        print("Testing with a blif file with invalid identifiers ")
        self.graph = LutGraph(self.benchdir, benchfile, False)
        k_list = [2, 3, 4]
        for k in k_list:
            lG = self.graph.genLutGraph(k)
            self.assertIsNone(lG)


class TestPerformanceLUT(BaseLUTTest):
    def test_load(self):
        debug = False
        benchfile = "./tests/fixtures/c6288.blif"
        self.graph = LutGraph(self.benchdir, benchfile, debug)
        self.partitioning()


if __name__ == "__main__":
    unittest.main()
