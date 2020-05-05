import sys

from .coarse_lut_mapper import CoarseMapper
from .detailed_lut_mapper import DetailedMapper
from .lutdag import LutGraph
from .graph_helper import topoOrdering
from .mapping_solution import MappingSolExplorer
from .solution import Solution

class SACMapper:

    def __init__(self,benchname,gendir=None,logfile='log.txt',debug = False, 
                                                            fastMode = False ):
        self.__benchname = benchname 
        self.__lutgraph = None 
        self.__crossbar = None 
        self.__instructions = None 
        self.__stats = dict()
        self.__logfile = logfile 
        self.__k = None 
        self.__benchdir = None 
        self.__benchname = benchname
        self.__fastMode = fastMode
        if gendir == None: 
            self.__benchdir = './'
        else:
            self.__benchdir = gendir 
        if '/' in benchname:
            
            self.__basename = benchname[benchname.rfind('/')+1:]
        else:
            
            self.__basename = benchname 
        # configure the logger [check if it works with arche]
        self.__debug = debug 
        self.__log = Solution()
        self.__log.addParam('benchmark', benchname)
        self.__log.addParam('workdir', gendir)
        if debug: 
            self.__log.addParam('debug', debug)
        self.__logfile = logfile 
        
    
    def mapBenchmark(self,R,C, k=None):
        if k == None:  
            kList = [i for i in range(6,8,2)]
        else:
            kList = [k]
        for k in kList:
            self.__log.initSolution()
            self.__log.addParam('benchmark',self.__basename)
            self.__k = k
            self.__log.addParam('k',k)
            self.__log.addParam('R',R)
            self.__log.addParam('C',C)
            lg = LutGraph(self.__benchdir, self.__benchname, self.__debug, self.__logfile)
            lutGraph = lg.genLutGraph(k)
            if lutGraph == None:
                print('{} LUT Graph generation failed for k = {}'.format(self.__benchname,k))
                self.__log.addParam('finished',False)
                continue 
            topoOrder,vertexLevel = topoOrdering(lutGraph, lutGraph['inputs'])

            # Phase I
            print('LUT placement for {} begins.'.format(self.__basename))
            cmap = CoarseMapper(self.__benchname, self.__benchdir, self.__logfile, self.__debug, self.__fastMode)
            result = cmap.placeBenchmark(lutGraph, R, C)
            if result is None:
                print('Retrying placement with more separation')
                result = cmap.placeBenchmark(lutGraph, R, C, True) # Try again

                if result == None:
                    self.__log.addParam('finished',False)
                    self.__log.writeJsonSolution(self.__logfile)
                    return None 
            print('LUT placement for {} completed.'.format(self.__basename))

            # Phase II
            alloc, schedule, placed = result[0], result[1], result[2]
            print('Detailed placement starts.')
            dmap = DetailedMapper(self.__benchname, self.__benchdir, self.__logfile, self.__debug, self.__fastMode)
            
            steps, posOutAlloc = dmap.computeBenchmark(lutGraph, R, C, alloc, schedule, placed)

            
            if steps is None:
                int('Detailed placement for {} failed.'.\
                    format(self.__basename))
                self.__log.addParam('finished',False)
                self.__log.writeJsonSolution(self.__logfile)
                return None
            print('Detailed placement completed.')



            # analyse the solution
            self.__log.addParam('cycles',"{}".format(len(steps)))
            solexp = MappingSolExplorer(steps,lutGraph,R,C,alloc, posOutAlloc, self.__debug)
            opCycles, opCount = solexp.getSteps(steps)

            # generate verilog output
            if '.' in self.__basename:
                modname = self.__basename[:self.__basename.rfind('.')]
            else:
                modname = self.__basename
            res = solexp.writeVerilog(
                modname,
                self.__benchdir+'Cr_{}_{}_k{}_'.format(R,C,k)+self.__basename+'.v'
            )
            # write the steps directly
            solexp.writeSteps(steps,self.__benchdir+'st_{}_{}_k{}_'.format(R,C,k)+self.__basename)

            self.__log.addParam('opcount', opCount )
            self.__log.addParam('opcycles', opCycles )
            
            self.__log.writeJsonSolution(self.__logfile)
            return opCycles

if __name__ == '__main__':
    
    if len(sys.argv) < 4:
        print('error: no file specified for mapping')
        print('usage: python3 sac.py benchmark[.v|.blif] row col [k] [debug] ')
        sys.exit()
    
    if len(sys.argv) == 4:
        k = None
    else:
        k = int(sys.argv[4])
        print('k:',k)
        
    if len(sys.argv) <= 5:
        debug = False
    else:
        debug = sys.argv[5]
        if debug == 'True':
            print('Debug mode set')
            debug = True 
        else:
            debug = False 
        print('k:',k)
        
    newObj = SACMapper(sys.argv[1],'genfiles/','logs.txt', debug, True)
    
    newObj.mapBenchmark(int(sys.argv[2]), int(sys.argv[3]),k)
    
