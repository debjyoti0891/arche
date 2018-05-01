from sortedcontainers import SortedDict
import copy
import sys
from igraph import *
import pdb 

class TechMagic:
        
    def __init__(self, debug):
        self.r = 0
        self.c = 0
        self.g = None
        self.ins = []
        self.topolabel = dict()
        self.debug = debug
        self.debug = True
        self.crossbar = SortedDict()
        self.maxrow = 0
        self.placed = dict()
        self.pivotLoc = dict() # pivot[gateId] = [(pivotloc, copyLoc)]
        self.inputsOfGate = dict()
        self.schedule = dict() # schedule[clk] = [gate1, gate2...]
        self.maxLevel = None 
        self.clk = None 
        self.utilization = None

    def __topoOrder(self, v):
        ''' compute the topological ordering of each node recursively '''        
        in_edges = self.g.es.select(_target_in = [v])
        for e in in_edges:
            s = e.source 
            if self.g.vs[s]['topo'] < self.g.vs[v]['topo'] + 1:
                self.g.vs[s]['topo'] =  self.g.vs[v]['topo']+1   
                self.__topoOrder(s)


    def __topoSort(self):
        ''' assign output as level 1 and increase by one towards pi '''
        for v in self.g.vs:
            v['topo'] = 0

        self.topolabel[1] = set()
        for out in self.g['po']:
            out = self.g['vToIndex'][out]
            self.g.vs[out]['topo'] = 1
            self.topolabel[1].add(out) 
        for out in self.g['po']:
            if self.debug: print('out:',out)
            if self.debug: print('index of out:',self.g['vToIndex'][out])
            self.__topoOrder(self.g['vToIndex'][out])

        for v in self.g.vs:
            if v['topo'] not in self.topolabel.keys():
                self.topolabel[v['topo']] = set()
            
            self.topolabel[v['topo']].add(v.index )

    def __generateGrid(self, display = False ):
        ''' populates a grid from printing the location of the 
            gates and the inputs '''
        grid = [['--' for i in range(self.c)] for r in range(self.maxrow)]
        for gate,pos in self.placed.items():
            pos = pos[0]
            grid[pos[0]][pos[1]] = gate 
        for gate, inputs in self.inputsOfGate.items():
            for p in inputs : 
                grid[p[1]][p[2]] = p[0]

        for gate, pivots in self.pivotLoc.items():
            for p in pivots:
                if p[0] != None:
                    grid[p[0][0]][p[0][1]] = 'I'+str(gate) 

                grid[p[1][0]][p[1][1]] = 'C'+str(gate) 

        emptyDev = 0
        for row in grid:
            emptyDev = emptyDev + row.count('--')
            for col in row:
                if display : print("%5s"%(str(col)),end='')
            if display: print('',end='\n')
        return emptyDev
        
    def map(self,r,c,g,ins_file=None):
        if self.debug: print(r)
        self.r = r
        self.c = c
        self.g = g
        # initialize the crossbar with an empty row
        self.maxrow = 0
        self.crossbar[self.maxrow] = [i for i in range(self.c)]
        self.maxrow = self.maxrow+1 

        self.__topoSort()

        maxLevel = max(self.topolabel.keys())
        self.maxLevel = maxLevel
        if self.debug: print('max level of the graph:',maxLevel)
        placementType = self.__placeOutputs()
        if self.debug: print('placed outputs :')
        for k,v in self.placed.items():
            if self.debug: print(k,v)
        for i in range(1, maxLevel+1):

            gateList = list(self.topolabel[i])

            print('mapping inputs at level:',i,'out of ', maxLevel, ' #gates:', len(gateList))
            if self.debug: print('gateList:', gateList)
            #pdb.set_trace()    
            # place the first gate in the level 
            gate = gateList[0] 
            if self.debug: print('placing:', gate)
            loc = self.__placeInputs(gate)
            # place the rest of the gates
            for gate in gateList[1:]:
                if self.debug: print('placing:',gate)
                loc = self.__placeInputs(gate,loc)

        for gate,placement in self.placed.items():
            if self.debug: print('placed ',gate, placement, self.g.vs[gate]['gateType'])
            if self.g.degree(gate,type='in') != 0:
                if self.debug: print('inputs:', self.inputsOfGate[gate])
        self.__optimizeGrid()
        self.__schedule()
        if self.debug: print('\n\n\n')
        if self.debug: print('Complete placement: ')
        if self.debug: self.__generateGrid(True)

        print("verified:",self.__verify())
        if self.debug: print('Mapping stats :', self.getStats())
    def __optimizeGrid(self, opt=None):
        ''' performs optimization on the intial grid placement '''
        # identify the negated outputs of gate inherently present 
        # as output of inv1 gate.
        invertsInGraph = dict() 
        for v in self.g.vs:
            if v['gateType'] == 'inv1':
                in_edges = self.g.es.select(_target_in = [v.index])
                for e in in_edges:
                    s = e.source 
                    invertsInGraph[s] = v.index
        print(invertsInGraph)
        print(self.pivotLoc.keys())
        for gate in self.pivotLoc.keys():
            
            if gate in invertsInGraph.keys():
                print(gate) 

        sys.exit(0)
    def __schedule(self, opts=None):
        ''' creates a schedule based on the current mapping '''
        clk = 0
        maxLevel = max(self.topolabel.keys())
        # assign the primary inputs 

        for i in range(maxLevel-1,0,-1):
            gateList = list(self.topolabel[i])
            parallelGates = []
            parallelLoc = [] 
            if self.debug: print('\n\nparallelLoc for level:', i)
            # assign the first copy of the gate 
            for g in gateList:
                locOut = self.placed[g]
                locIn = set()
                dirAlloc = None
                if g in self.inputsOfGate.keys() and len(self.inputsOfGate[g]) > 0:
                    if self.debug: print('g :',locOut, self.inputsOfGate[g], self.inputsOfGate[g][0], locOut[0])
                    if self.inputsOfGate[g][0][1] == locOut[0][0] :
                        dirAlloc = 'r'
                        index = 1
                    else:
                        dirAlloc = 'c'
                        index = 0
                    locOut = locOut[0][index]

                    for inp_id,r,c in self.inputsOfGate[g]:
                        if index == 0:
                            locIn.add(r)
                        else:
                            locIn.add(c)

                    if self.debug :print('scheduling:',g,self.inputsOfGate[g], locOut, dirAlloc) 
                else:
                    continue


                clkAssigned = False 
                for i in range(len(parallelLoc)):
                    if locOut == parallelLoc[i][0] and locIn == parallelLoc[i][1] and dirAlloc == parallelLoc[i][2]:
                        parallelGates[i].append(g) 
                        clkAssigned = True 
                        break 

                if not clkAssigned: 
                    parallelLoc.append([locOut, locIn, dirAlloc])
                    parallelGates.append([g])

                if self.debug: print('||loc:',g,locIn,locOut, parallelLoc) 

            m = -1 
            for gates in parallelGates: 
                clk = clk + 1
                self.schedule[clk] = []
                for g in gates:
                    self.schedule[clk].append(['g',g])
                if m < len(gates):
                    m = len(gates) 
            if self.debug:print('max parallel:', m, len(gateList))

            parallelLoc = []
            parallelGates = [] 
            copyLoc = []
            copyGates = []

            # assign the pivots of the gate 
            for g in gateList:
                if g not in self.pivotLoc.keys():
                    continue 
                for pivoti in range(len(self.pivotLoc[g])):
                    iLoc, cLoc, t = self.pivotLoc[g][pivoti]
                    if iLoc == None : #this is the original copy
                        continue 
                    if self.debug: print('pivot:',cLoc,iLoc,t, g, self.placed[g])                
                    # check for parallel operation of invert operations
                    if iLoc[0] == t[0]:
                        dirAlloc = 'r'
                        index = 1
                    else:
                        dirAlloc = 'c' 
                        index = 0
                        
                    clkAssigned = False 
                    for i in range(len(parallelLoc)):
                        if parallelLoc[i][0] == t[index] and parallelLoc[i][1] == iLoc[index] and parallelLoc[i][2] == dirAlloc: 
                            parallelGates[i].append([g,pivoti])
                            clkAssigned = True 
                            break
                    if not clkAssigned:
                        parallelLoc.append([t[index],iLoc[index],dirAlloc ])
                        parallelGates.append([[g, pivoti]]) 

                    # check for parallel operations of copy operation 
                    if cLoc[0] == iLoc[0]:
                        dirAlloc = 'r'
                        index = 1
                    else:
                        dirAlloc = 'c'
                        index = 0


                    clkAssigned = False 
                    for i in range(len(copyLoc)):
                    
                        if copyLoc[i][0] == iLoc[index] and copyLoc[i][1] == cLoc[index] and copyLoc[i][2] == dirAlloc:
                            copyGates[i].append([g,pivoti])
                            
                            clkAssigned = True 
                            break
                    if not clkAssigned:
                        copyLoc.append([iLoc[index],cLoc[index], dirAlloc])
                        copyGates.append([[g, pivoti]]) 



            #schedule inverts, followed by copy
            for inverts in parallelGates:
                clk = clk + 1
                self.schedule[clk] = []
                for g,pivoti in inverts:
                    self.schedule[clk].append(['i',g,pivoti])
 
            for copies in copyGates:
                clk = clk+1
                self.schedule[clk] = []
                for g,pivoti in copies:
                    self.schedule[clk].append(['c',g,pivoti])           
        self.clk = clk
        for clk, gates in self.schedule.items():
            if self.debug: print(clk,':',gates)

    def __freeLoc(self, loc):
        self.crossbar[loc[0]].append(loc[1])

    def __getLoc(self,t,val,dim2=None):

        if t == 'row' : 
            if val >= self.c:
                print('Invalid col requested', val)
                return None
            # find a free row in specified col 
            for i in iter(self.crossbar):
               if val in self.crossbar[i]:
                   self.crossbar[i].remove(val)
                   return (i,val) 
            # none of the existing rows  has free device at "col= val"
            self.crossbar[self.maxrow] = [i for i in range(self.c)]
            self.maxrow = self.maxrow + 1
            self.crossbar[self.maxrow-1].remove(val)
            return (self.maxrow - 1, val) 

        elif t == 'col' : 
            
            # find a free column in specified row --- can return None if allocation fails
            if val not in self.crossbar.keys():
                if val == self.maxrow:
                    self.crossbar[self.maxrow] = [i for i in range(self.c)]
                    self.maxrow = self.maxrow + 1
                    col = self.crossbar[val][0]
                    self.crossbar[self.maxrow-1].remove(col)
                    return (val,col) 
                else:
                    return None
            if self.crossbar[val] != list():
                col  = self.crossbar[val][0]
                self.crossbar[val].remove(col)
                return (val,col)
            else:
                # could not find any free device 
                return None
        elif t == 'rc' : 
            # find if the device is free at location r,c 
            if dim2 in self.crossbar[val]:
                self.crossbar[val].remove(dim2)
                return (val,dim2)
            else:
                return None # device at location is not available 
        else:
            return None # invalid request

    def __placeOutputs(self):
        ''' place the outputs horizontally '''

        gates = 0
        for gate in self.g['po']:
            index = self.g['vToIndex'][gate]
            l = self.__getLoc('col',int(gates/self.c))
            if l == None:
                print(gates, int(gates/self.c), self.c)
                print('could not place output')
                sys.exit(1)
            self.placed[index] = [l] 
            gates = gates+1


        

    def __getGateInput(self,v):
        inputs = []
        pivots = []
        in_edges = self.g.es.select(_target_in = [v])
        alloc = True 
        allocType = 'row'
        inp = list() 
        for e in in_edges:
            s = e.source 
            if s in self.placed.keys() and self.g.degree(s,type='in') != 0: #this is a pivot 
                pivots.append(s)
            else:
                inputs.append(s) 

        return list(set(inputs)),list(set(pivots)) 

    def __placeInputs(self,gate,loc = None):
        inputs,pivots = self.__getGateInput(gate) 
        if self.debug: print(inputs, pivots)
        loc = None 
        # TODO : correct when loc is provided
        if loc == None:
            '''place the inputs of the gate without constraints --- horizontally first, else vertically '''
            
            alloc = True 
            allocType = 'col'
            inp = []
            allocated = []
            for s in pivots:
                pivot,copyGate,newAlloc = self.__allocatePivot('col',gate,s)
                if copyGate == None:
                    alloc = False 
                    break
                else:
                    # TODO : verifying correctness : disable later 
                    if not( copyGate[0] == self.placed[gate][0][0]): 
                        print('invalid allocation of pivot :', gate,self.placed[gate], copyGate, allocType)
                        sys.exit(0)
                    allocated.append(pivot)
                    allocated.append(copyGate) 
                    if self.debug: print('copyGate : ', copyGate)
                    inp.append((s, copyGate[0],copyGate[1]))
                    if s not in self.pivotLoc.keys():
                        self.pivotLoc[s] = []
                    self.pivotLoc[s].append((pivot,copyGate,self.placed[s][0]))
            if alloc :
                for v in inputs:
                
                    l = self.__getLoc('col', self.placed[gate][0][0])
                    if l == None : 
                        alloc = False 
                        break 
                    else:
                        inp.append((v,l[0],l[1]))
                        allocated.append(l)


            if  not alloc:
                # free all allocated locations if the allocation did not succeed.
                for l in allocated:
                    if l == None:
                        continue
                    self.__freeLoc(l)

                allocType = 'row'
                inp = [] 
                alloc = True
                for s in pivots:
                    pivot, copyGate,newAlloc = self.__allocatePivot('row',gate,s)
                    if copyGate == None:
                        print('Allocation for pivot %d of gate %d failed' % (s,gate))
                        alloc = False 
                        break
                    else:
                        if not( self.placed[gate][0][1] == copyGate[1]):
                            print('invalid allocation of pivot :', gate,self.placed[gate], copyGate, allocType)
                            sys.exit(0)
                        allocated.append(pivot)
                        allocated.append(copyGate) 
                        if self.debug: print('copyGate : ', copyGate)
                        inp.append((s, copyGate[0],copyGate[1]))
                        if s not in self.pivotLoc.keys():
                            self.pivotLoc[s] = []
                        self.pivotLoc[s].append((pivot,copyGate, self.placed[s][0]))

                for v in inputs:
                    #print(gate,'row:' , self.placed[gate][0])  
                    l = self.__getLoc('row', self.placed[gate][0][1])
                    if l == None : 
                        
                        print('Allocation for input %d of gate %d failed' % (v,gate))
                        alloc = False 
                        break 
                    else:
                        inp.append((v,l[0],l[1]))
            if not alloc:
                print('Allocation for gate: %d failed' % (gate))
                sys.exit(1)
                return None
            else:
                self.inputsOfGate[gate] = inp 
                
                loc = set()
                for i in inp:
                    loc.add((i[1],i[2]))
                    if self.debug: print('check iloc:', i)
                    if i[0] not in self.placed.keys():
                        self.placed[i[0]] = [(i[1],i[2])]
                return [(allocType,loc)]
        
        # check if any set in loc allows placement -- take care of the pivots.
        for l in loc:
            alloc = True 
            allocType = l[0]
            if allocType == 'row':
                index = 0
            elif allocType == 'col':
                index = 1
            dim2 = self.placed[gate][0][1-index]
            if self.debug: print('dim2:', dim2, self.placed[gate])
            # pos contains the positions 
            pos = list()
            for p in l[1]:
                pos.append(p[index])
            # check if the number of inputs 
            if len(l[1]) != len(inputs) + len(pivots):
                alloc = False 
                continue 
            # check if the pivots can be placed 
            inp = []
            allocated = []
            if pivots != list():
                for p in pivots:
                    l = self.__allocatePivot('rc', gate, p, pos, dim2)
                    if l == None:
                        alloc = False
                        break 
                    else:
                        inp.append((p,l[0],l[1]))
                        allocated.append(l)
                        pos.remove(l[index])
                if not alloc:
                    continue 

            # check if the inputs can be` placed 
            if alloc:
                localAllocted = []
                for p in pos : 
                    if allocType == 'row':
                        r,c = p,dim2 
                    else:
                        r,c = dim2,p 
                    if self.debug: print(r,c, p, dim2)
                    l = self.__getLoc('rc', r,c)
                    if l != None:
                       localAllocted.append(l)
                    else:
                        alloc = False 
                        break 
                if not alloc:
                    for l in localAllocted:
                        self.__freeLoc(l)
                else:
                    for i in range(len(inputs)):
                        inp.append((i,localAllocted[i][0], localAllocted[i][1]))
            else:
                for l in allocated:
                    self.__freeLoc(l) 

        if not alloc : 
            locNew = self.__placeInputs(gate)
            loc.append(locNew[0])
        return loc 
        
    def __probeLoc(self, allocType, dim1, dim2):
        ''' get a free location '''
        loc = self.__getLoc(allocType,dim1,dim2)
        if loc != None:
            self.__freeLoc(loc)
        return loc 
        
    def __allocatePivot(self, allocType, G, I, pos=None, dim2=None):
        # G = target gate for which input have to be placed
        # I = input gate which is has to be copied 
        gLoc = self.placed[G][0]
        iLoc = self.placed[I][0]
        
        if self.debug: print('gLoc:', gLoc , 'iLoc:',iLoc , allocType)
        '''disable optimization '''
        pos = None
        dim2 = None
        ''' allocate a pivot 
        if allocType == 'row' :
                gateDim = self.placed[1]
                pivotDim = self.placed[0]
        elif allocType == 'col':
                gateDim = self.placed[0]
                pivotDim = self.placed[1]'''
        allocated = []
        if pos == None and dim2 == None: # regular pivot without constraints 
            if allocType == 'row':

                if gLoc[1] == iLoc[1] : # target and input gate are in same col 
                    return None, iLoc, False # No negation used  
                else:
                    alloc = False 
                    while not alloc:

                        #print('gLoc row:' , gLoc)  
                        t = self.__getLoc('row',gLoc[1])
                        if t == None:
                            print('location not found in column ', gLoc[1])
                            break
                        allocated.append(t)
                        if t[0] == iLoc[0] : # copy location and original share the same row 
                            p = self.__getLoc('col', t[0])
                            if p == None:
                                continue
                            return p,t,True
                        else:
                            #check if p1 is available 
                            p1 = self.__probeLoc('rc', iLoc[0], t[1])
                            if p1 == None:
                                p1 = self.__probeLoc('rc',t[0], iLoc[1])
                        
                                if p1 == None:
                                   continue 
                                else:
                                    p1 = self.__getLoc('rc', t[0],iLoc[1])
                                    alloc = True 
                            else:
                                p1 = self.__getLoc('rc', iLoc[0], t[1])
                                alloc = True 
                            for loc in allocated[:-1]:
                                self.__freeLoc(loc)
                            return p1,t,True 
                if not alloc:
                    for loc in allocated[:-1]:
                        self.__freeLoc(loc)
                    return None, None, False 

            elif allocType == 'col':
                if gLoc[0] == iLoc[0]: # copy/target gate and input gate in same row!
                    return None, iLoc,False 
                else:
                    alloc = False 
                    while not alloc:
                        t = self.__getLoc('col',gLoc[0]) # locate 
                        if t == None:
                            break 
                        allocated.append(t)
                        if self.debug: print('target copy location(col):', t)
                        if t[1] == iLoc[1]:
                            p = self.__getLoc('row', t[1])

                            if p == None:
                                break
                            else:
                                return p,t,True 
                        else:
                            if self.debug: print('gloc:', gLoc, 'iloc:', iLoc)
                            p1 = self.__probeLoc('rc',t[0], iLoc[1])
                            if p1 == None:
                                p1 = self.__probeLoc('rc',iLoc[0], t[1])
                                if p1 == None:
                                    continue 
                                p1 = self.__getLoc('rc', iLoc[0],t[1])
                                alloc = True 
                            else:
                                p1 = self.__getLoc('rc',t[0], iLoc[1])
                                alloc = True
                            if alloc:
                                for loc in allocated[:-1]:
                                    self.__freeLoc(loc)
                                return p1,t,True 
                    if not alloc:
                        for loc in allocated:
                            self.__freeLoc(loc)
                        return None,None,False     


        else: # location constrained pivot 
            if allocType == 'row' :
                gateDim = self.placed[1]
                print('Constraint pivots not supported')
                sys.exit(0)
    def printStats(self, out_file=None):
        ''' prints statistics about the benchmark and the mapping '''
        print('i/o %d/%d' % (len(self.g['pi']), len(self.g['po'])))

    def __isvalidLoc(self,gate,r,c):
        if self.debug: print(gate,self.placed[gate][0], r,c, gate in self.pivotLoc.keys())
        if self.placed[gate][0] == (r,c):
            return True
        elif self.g.degree(gate,type='in') == 0: # is primary input 
            return True
        elif gate in self.pivotLoc.keys():
            if self.debug: print(self.pivotLoc[gate])
            for inv,cp,orig in self.pivotLoc[gate]:
                if self.debug: print((r,c), cp)
                if cp == (r,c):
                    return True 

        return False 
            
    def __isInp(self,gate,inGate):
        ''' check if the inGate is the input of gate '''
        in_edges = self.g.es.select(_target_in = [gate])
        for e in in_edges:
            s = e.source 
            if s == inGate:
                return True
        return False 

    def __verify(self):
        ''' verify the correctness of mapping ''' 

        ''' verify all the pivots '''
        for gate, p in self.pivotLoc.items():
            pivots = copy.deepcopy(p)
            posLoc = set() 
            posLoc.add(self.placed[gate][0])
            l = len(pivots) 
            for i in range(l):
                rem = [] 
                for j in range(len(pivots)):
                    inv,cp,orig = pivots[j]
                    if orig in posLoc:
                        if inv == None or inv[0] == cp [0] == orig[0] \
                                or inv[1] == cp[1] == orig[1] \
                                or (orig[0] == inv[0] and inv[1] == cp[1] )\
                                or (orig[1] == inv[1] and inv[0] == cp[0] ):
                            rem.append(j)
                            posLoc.add(cp)
                        else:
                            print('verification failed :', gate, inv, cp, orig)
                            return False 

                if self.debug: print("remove:",rem,'pivot list:', pivots)
                for i in sorted(rem, reverse=True):
                    del(pivots[i])

                if pivots == list():
                    break 
        if pivots != list():
            print('verification failed:', gate, pivots)
        ''' verify gates in topological ordering from the outputs to the inputs '''
        for gate,locl in self.placed.items():
            loc = locl[0] 

            inp = self.inputsOfGate[gate]
            if len(inp) == 0: #primary input 
                continue
            if len(inp) == 1: # single input gate
                inp = inp[0]
                if not((loc[0] == inp[1] or loc[1] == inp[2]) \
                        and self.__isvalidLoc(inp[0], inp[1],inp[2])\
                         and self.__isInp(gate,inp[0])):
                    print('invalid single input :',gate, self.placed[gate],self.inputsOfGate[gate])
                    print('valid loc:', self.__isvalidLoc(inp[0],inp[1],inp[2]))
                    print('valid inp:', self.__isInp(gate,inp[0]))
                    return False
            else:
                index = -1
                if inp[0][1] == inp[1][1]:
                    index = 0
                elif inp[0][2] == inp[1][2] :
                    index = 1
                else:
                    print('invalid input', gate, self.inputsOfGate[gate])
                    return False 
                for gid,r,c in inp:
                    gloc = (r,c) 
                    if not (loc[index] == gloc[index] \
                            and self.__isvalidLoc(gid,r,c)\
                            and self.__isInp(gate,gid)):
                        if index == 0:
                            allocType = 'same row' 
                        else:
                            allocType = 'same col'
                        print('invalid input:', gate,self.placed[gate], gid,r,c, allocType, index)
                        print('valid loc:', self.__isvalidLoc(gid, r,c))
                        print('valid inp:', self.__isInp(gate,gid))
                        print('all inputs:', self.inputsOfGate[gate])
                        return False 
        return True

    def __showSchedule(self):
        ''' display the schedule as an animation '''
        print('TODO')

    def getStats(self):
        ''' returns a string with the placement details 
            #pi,#po,#gates,level,delay,speedup,r,c,#devices,#util '''
        stats = ''
        pi = len(self.g.vs.select(_indegree = 0))
        stats = stats + str(pi)+','
        stats = stats + str(len(self.g['po'])) + ','
        stats = stats + str(len(self.g.vs)-pi) + ','
        stats = stats + str(self.maxLevel) + ','
        stats = stats + str(self.clk) + ',' 
        stats = stats + "{0:.2f}".format(1.0*len(self.g.vs)/self.clk)+','
        util = self.maxrow*self.c - self.__generateGrid()
        stats = stats + str(self.maxrow) + ','
        stats = stats + str(self.c) + ',' 
        stats = stats + str(util)  + ','
        stats = stats + "{0:.2f}".format(1.0*util/(self.maxrow * self.c))
        return stats 


