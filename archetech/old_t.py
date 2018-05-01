import sys
from igraph import *


class TechMagic:
        
    def __init__(self, debug=False):
        self.r = 0
        self.c = 0
        self.g = None
        self.ins = []
        self.topolabel = dict()

        self.crossbar = dict()
        self.maxrow = 0
        self.placed = dict()
        self.pivotLoc = dict() # pivot[gateId] = [(pivotloc, copyLoc)]
        self.inputsOfGate = dict()
        self.debug = debug

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

    def map(self,r,c,g,ins_file=None):
        if self.debug: print(r)
        self.r = r
        self.c = c
        self.g = g
        # initialize the crossbar with an empty row
        self.crossbar[self.maxrow] = [i for i in range(self.c)]
        self.maxrow = self.maxrow+1 

        self.__topoSort()

        maxLevel = max(self.topolabel.keys())
        if self.debug: print('max level of the graph:',maxLevel)
        self.__placeOutputs()
        if self.debug: print('placed outputs :')
        for k,v in self.placed.items():
            if self.debug: print(k,v)
        for i in range(1, maxLevel+1):

            gateList = list(self.topolabel[i])
            if self.debug: print('gateList:', gateList)
            
            # place the first gate in the level 
            g = gateList[0] 
            loc = self.__placeInputs(g)
            # place the rest of the gates
            for g in gateList[1:]:
                loc = self.__placeInputs(g,loc)

            for gate,placement in self.placed.items():
                if self.debug: print('placed ',gate, placement)

    def __freeLoc(self, loc):
        self.crossbar[loc[0]].append(loc[1])

    def __getLoc(self,t,val,dim2=None):

        if t == 'row' : 
            if val >= self.c:
                print('Invalid col requested', val)
                return None
            # find a free row in specified col 
            for i in self.crossbar.keys():
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
        ''' place the outputs vertically '''
        for gate in self.g['po']:
            index = self.g['vToIndex'][gate]
            self.placed[index] = [self.__getLoc('row',0)]


        

    def __getGateInput(self,v):
        inputs = []
        pivots = []
        in_edges = self.g.es.select(_target_in = [v])
        alloc = True 
        allocType = 'row'
        inp = list() 
        for e in in_edges:
            s = e.source 
            if s in self.placed.keys(): #this is a pivot 
                pivots.append(s)
            else:
                inputs.append(s) 
            inputs.append(s)
        return inputs,pivots 

    def __placeInputs(self,gate,loc = None):
        inputs,pivots = self.__getGateInput(gate) 
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
                    allocated.append(pivot)
                    allocated.append(copyGate) 
                    inp.append((s, copyGate[0],copyGate[1]))

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
                    self.__freeLoc(l)

                allocType = 'row'
                inp = [] 
                alloc = True
                for s in pivots:
                    l = self.__allocatePivot('row',gate,s)
                    inp.append((s,l[0],l[1]))
                for v in inputs:
                        l = self.__getLoc('row', self.placed[gate][0][1])
                        if l == None : 
                            alloc = False 
                            break 
                        else:
                            inp.append((v,l[0],l[1]))
            if not alloc:
                print('Allocation for gate: %d failed' % (gate))
                return None
            else:
                self.inputsOfGate[gate] = inp 
                
                loc = set()
                for i in inp:
                    loc.add((i[1],i[2]))
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
        gLoc = self.placed[G][0]
        
        iLoc = self.placed[I][0]
        #print('gLoc:', type(gLoc), 'iLoc:',iLoc)
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
                        t = self.__getLoc('row',gLoc[0])
                        if t == None:
                            break
                        allocated.append(t)
                        if t[0] == iLoc[0] : # copy location and original share the same row 
                            p = self.__getLoc('col', t[0])
                            if p == None:
                                break 
                            return t,p,True
                        else:
                            #check if p1 is available 
                            p1 = self.__probeLoc('rc', iLoc[0], tLoc[1])
                            if p1 == None:
                                p1 = self.__probeLoc('rc', tLoc[0], iLoc[1])
                        
                                if p1 == None:
                                   continue 
                                else:
                                    p1 = self.__getLoc('rc', tLoc[0],iLoc[1])
                                    alloc = True 
                            else:
                                p1 = self.__getLoc('rc', iLoc[0], tLoc[1])
                                alloc = True 
                            for loc in allocated[:-1]:
                                self.__freeLoc(loc)
                            return p1,t,True 
                if not alloc:
                    for loc in allocated[:-1]:
                        self.__freeLoc(loc)
                    return None, None, False 

            elif allocType == 'col':
                if gLoc[0] == iLoc[0]:
                    return None, iLoc,false 
                else:
                    alloc = False 
                    while not alloc:
                        t = self.__getLoc('col',gLoc[1])
                        if t == None:
                            break 
                        allocated.append(t)

                        if t[1] == iLoc[1]:
                            p = self.__getLoc('row', t[1])
                            if p == None:
                                break
                            else:
                                return t,p,True 
                        else:
                            p1 = self.__probeLoc('rc', gLoc[0], iLoc[1])
                            if p1 == None:
                                p1 = self.__probeLoc('rc',iLoc[0], gLoc[1])
                                if p1 == None:
                                    continue 
                                p1 = self.__getLoc('rc', iLoc[0],gLoc[1])
                                alloc = True 
                            else:
                                p1 = self.__getLoc('rc',gLoc[0], iLoc[1])
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
    def printStats(self, out_file=None):
        ''' prints statistics about the benchmark and the mapping '''
        print('i/o %d/%d' % (len(self.g['pi']), len(self.g['po'])))

    def __place(self,g,r,c,level):
        ''' places the inputs of the gate at level r,c ''' 
        if self.debug: print('place')



