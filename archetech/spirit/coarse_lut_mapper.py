import copy 
import sys

from .solution import Solution

class CoarseMapper:

    
    def __init__(self,benchname,gendir=None,logfile='log.txt',debug = False, fastMode = False ):
        self.__benchname = benchname 
        
        self.__lutgraph = None 
        self.__crossbar = None 
        self.__instructions = None 
        self.__stats = dict()
        self.__logfile = logfile 
        self.__k = None 
        self.__benchdir = None 
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
        self.__logfile = logfile 
    
    def __updateReady(self,lutGraph,v,active,ready,placed):
        if self.__debug: print('Placed:{} Node:{} -> Evaluating succ: {}| active{}'.format(placed,v,lutGraph.successors(v),active))
        
        for s in lutGraph.successors(v):
            # if the node is a constant node then its always ready
            snode =  lutGraph.vs[s]
            if snode['lut'].isConstant() != False:
                print('Added a constant lut:{}'.format(s))
                placed.add(s)
                continue 
            
            pred = set(lutGraph.predecessors(s))
            if self.__debug: print('pred %s | placed: %s | succ: %s ' % (pred, placed,s))
            if pred.issubset(placed) and not s in active:
                #add the lut to the ready queue
                vsucc = lutGraph.vs[s]
                terms,inputs = vsucc['lut'].getDim()
                
                ready.append((s,terms+1,inputs+1,1))
                active.add(s)
        if self.__debug: print('ready:', ready)
    
    def __resetCross(self,lutGraph,alloc,R,C, move=False):
        ''' Resets a crossbar while preserving temporary results and outputs 
            It can reserve either rows or columns to kepresever content of the reserved locations.

            Returns:
                n           : number of reserved rows/columns
                reservation : `r` or `c` depending on what is reserved
                l           : list of reserved rows/columns
                clean       : reset [indices]
                rlim        : new limit of rows
                clim        : new limit of columns 
        '''

        # remove elements from allocation that are no longer required
        if self.__debug: print('reset check:', alloc)
        eliminate = set()
        for lut in alloc.keys():
            evict = True 
            if self.__debug: print('succ {}: {}'.format(lut,lutGraph.successors(lut)))
            for s in lutGraph.successors(lut):
                
                if s not in alloc.keys():
                    evict = False 
                    break 
            if evict:
                eliminate.add(lut)
        

        #dont eliminate outputs
        out = set()
        for i in lutGraph['outputs']:
            
            v = lutGraph.vs.select(name=i)
            out.add(v[0].index)
        eliminate = eliminate.difference(out)

        if self.__debug: print('eliminating:',eliminate, out)

        
        if move: 
            # TODO: create operations to align the existing results using COPY
            pass 
        #find blocked rows/cols
        rows = set()
        cols = set()
        for lut in alloc.keys():
            if lut not in eliminate or lut in out:
                r,c = alloc[lut]
                rows.add(r)
                cols.add(c)
        
        if len(rows)*R >= len(cols)*C: 
            # reserve column 
            reserve = 'c'
            l = list(cols) 
            c = set([i for i in range(C)])
            clean = c.difference(cols)
            rlim = R 
            clim = C - len(cols)
            
        else:
            # reserve row 
            reserve = 'r'
            l = list(rows)
            r = set([i for i in range(R)])
            clean = r.difference(rows)
            
            rlim = R - len(rows) 
            clim = C
        clean = list(clean)
        clean.sort()
        return reserve,l,clean,rlim,clim
    
    
    def __findOccupied(self,crossbar):
        ''' Returns a list of rows and columns which have data '''
        freeCell = 0 
        R = len(crossbar)
        C = len(crossbar[0])
        
        rows = set()
        cols = set()
        for r in range(R):
            for c in range(C):
                if crossbar[r][c] != freeCell:
                    rows.add(r)
                    cols.add(c)
                    
        return list(rows), list(cols)  

    def __getReadyList(self, lutGraph):
        ''' '''
        ready = [] # [(luti,tmin)]
        placed = set()
        active = set()
        for i in lutGraph['inputs']:
            
            v = lutGraph.vs.select(name=i)
            
            placed.add(v[0].index)
            if self.__debug: print('input vertices:',i,v[0].index)
        
        
        #add level 1 LUTs to the ready queue 
        for v in placed:
            self.__updateReady(lutGraph,v,active,ready,placed)
            

        if self.__debug: print('Initial ready list:',ready)   
        return placed, active, ready 

    def placeBenchmark(self, lutGraph, R, C, secondAttempt=False):
        ''' Schedules the LUTs in the benchmark using RxC size crossbar '''
        self.__log.addParam('error', '')
        crossbar = [[1 for j in range(C)] for i in range(R)]
        steps = list() # actual MAGIC operations 
        bRow,bCol = self.__findOccupied(crossbar)
        
        placed, active, ready = self.__getReadyList(lutGraph)
                 
        if secondAttempt:
            spacing = 2
        else:
            spacing = 0
        # schedule the LUTs as blocks 
        alloc, schedule, placed = self.__simpleSchedule(lutGraph, R,C, ready, placed, active, spacing)
        if alloc == None:
            return None
            
        if self.__debug: print('Allocation: {}'.format(alloc))
        return (alloc, schedule, placed)

    def __getLUT(self, ready, avail,  lutGraph, currSlot=[]):
        ''' returns LUT for execution in the currSlot '''
        lut = None 
        success = False 

        laterLut = None 
        laterSucc = False 
        if currSlot == []: # anything in the ready queue can be placed 
            for i in range(len(ready)):
                testLut = ready[i]
                rows,ksel = lutGraph.vs[testLut]['lut'].getDim()
                
                if ksel + 1 <= len(avail[1]) and rows + 1<= len(avail[0]):
                    return 'now', testLut

            return False, None

        else: 
            # choose an LUT which can be scheduled in the currSlot 
            k = len(lutGraph.vs[currSlot[0][0]]['lut'].inputs)
            for i in range(len(ready)):
                testLut = ready[i]
                # check if dependency exists
                dep = False 
                
                for p in lutGraph.predecessors(testLut):
                    for val in currSlot:
                        if val[0] == p:
                            dep = True 
                            break
                    if dep:
                        break 
                
                if dep:
                    continue 
                rows,ksel = lutGraph.vs[testLut]['lut'].getDim()
                
                if ksel + 1 <= len(avail[1]) and rows + 1 <= len(avail[0]):
                    if ksel == k :
                        lut = testLut 
                        success = 'now'
                        break 
                    else:
                        laterLut = testLut
                        laterSucc = 'next' 


                
            # choose an LUT for the next slot 
            if success:
                return success, lut
            else:
                return laterSucc, laterLut 

    def __simpleSchedule(self, lutGraph, R, C, ready, placed, active, spacing=0):
    
        for i in range(len(ready)):
            ready[i] = ready[i][0]
        avail = [[i for i in range(R)], [j for j in range(C)]]
        schedule = dict()
        alloc = dict()
        ts = 2
        schedule[ts] = ['luts', []]
        resetCount = 0
        blocked = ['',[]]
        maxc = -1
        while ready != list(): # process all LUTs

            succ, lut = self.__getLUT(ready, avail, lutGraph, schedule[ts][1])

            if not succ:
                # try moving to the next columns 
                resetEnable = False 
                for c in range(maxc):
                    if avail[1]!= list():
                        avail[1].pop(0)
                    else:
                        resetEnable = True 
                if not resetEnable:
                    for r in range(R):
                        if blocked[0] == 'r' and r in blocked[1]:
                            continue 
                    succ, lut = self.__getLUT(ready, avail, lutGraph, schedule[ts][1])
                if succ and not resetEnable:
                    continue 
                else:
                    # reset crossbar
                     
                    if resetCount > 2:
                        print('Unable to map the benchmark to {}x{}'.format(R,C))
                        self.__log.addParam('error', 'Small crossbar dimension.')
                        
                        return None, None, None 
                    reserve,dirty,clean,rlim,clim = self.__resetCross(lutGraph, alloc, R, C)
                    blocked = [reserve, clean]
                    if reserve == 'r':
                        avail[0] = copy.deepcopy(clean)
                        avail[1] = []
                        for c in range(C):
                            avail[1].append(c)
                    elif reserve == 'c':
                        avail[1] = copy.deepcopy(clean)
                        avail[0] = []
                        for r in range(R):
                            avail[0].append(r)
                    ts = ts+1
                    schedule[ts] = ['reset', [reserve, copy.deepcopy(dirty), copy.deepcopy(clean)]]
                    ts = ts+1
                    schedule[ts] = ['luts', []]
                    resetCount = resetCount+1

            
            elif succ == 'now' or succ == 'next':
                # remove the rows from avail
                resetCount = 0
                ksel = len(lutGraph.vs[lut]['lut'].inputs)
                rows = len(lutGraph.vs[lut]['lut'].logic)

                startr = avail[0][0]
                startc = avail[1][0]
                for r in range(rows+1):
                    resr = avail[0].pop(0)
                # additional gaps can be inserted if available:
                gap = 0
                while avail[0] != list():
                    if gap == spacing:
                        break 
                    gap = gap+1
                    avail[0].pop(0)
                    
                maxc = max(maxc,ksel) 
                resc = avail[1][ksel]
                alloc[lut] = (resr,resc)
                if succ == 'now':
                    schedule[ts][1].append([lut,startr,startc,resr,resc])
                elif succ == 'next':
                    ts = ts+1
                    schedule[ts]= ['luts',[[lut,startr,startc,resr,resc]]]
                else:
                    print('Something went wrong')
                    sys.exit(1)
                
                ready.remove(lut)

                # update the ready queue 

                for s in lutGraph.successors(lut):
                    # check if already scheduled or placed or is a constant
                    if s in ready  or \
                        s in alloc.keys() or \
                        lutGraph.vs[lut]['lut'].isConstant():
                        continue 
                    # check alive condition
                    sReady = True 
                    for p in lutGraph.predecessors(s):
                        if p in alloc.keys() or lutGraph.vs[p]['name'] in lutGraph['inputs']:
                            continue
                        else:
                            sReady = False
                            break 
                    
                    if sReady:
                        ready.append(s)

        return alloc, schedule, list(alloc.keys())                  

    