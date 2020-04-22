import copy
from heapq import *
import sys
import time
from .solution import Solution

class DetailedMapper:

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


    def computeBenchmark(self, lutGraph, R, C, alloc, schedule, placed):
        ''' Maps the benchmark using RxC size crossbar '''
        
                   
        if self.__debug: print('Allocation: {}'.format(alloc))
        # print the schedule 
        slotMax = max(schedule.keys())
        self.__log.addParam('computeSlots', len(schedule.keys()))
        print('LUT Schedule generated with {} slots'.format(len(schedule.keys())))
        
        for s in range(2,slotMax+1):
            if self.__debug: print('t{} [{}]: {}'.format(s,schedule[s][0],schedule[s][1]))
        # create an empty crossbar
        crossbar = [[1 for j in range(C)] for i in range(R)] 
        start = time.time()
        status,crossbar,newSteps = self.__placeCrossbar(lutGraph, lutGraph['inputs'], crossbar, schedule, alloc)
        if status:
            steps = newSteps 
        else:
            print('Mapping failed')
            return None 
        
        end = time.time()
        if self.__debug: print('Time:',start,end,end-start)
        self.__log.addParam('detailedMapTime', "{:.3f}".format(end-start))
        
        
        # final set of steps to compute positive copy of the outputs 
        # can be omitted for some LUTs
        placedOut = list(alloc.keys())
        out = set()
        for i in lutGraph['outputs']:
            
            v = lutGraph.vs.select(name=i)
            out.add(v[0].index)

            if v[0].index in placedOut:
                success = True
            else:
                outLut = v[0]['lut']
                
                if outLut.isConstant():
                    print('Encounted constant LUT: {} [id: {}]'.format(i,v[0].index))
                    success = True 
                    consOut = self.__log.getParam('constantOut')
                    if consOut == None:
                        consOut = []
                    self.__log.addParam('constantOut', consOut+[i])
                else:
                    success = False 

            assert success, 'Output {}[{}] placement did not succeed'.format(i,v[0].index)
           
        colMap = dict()
        for lut, pos in alloc.items():
            if lut not in out:
                continue 
            if pos[1] not in colMap.keys():
                colMap[pos[1]] = [(lut,pos[0])]
            else:
                colMap[pos[1]].append((lut,pos[0]))
        if self.__debug: print(colMap)
        freeCol = None
        posLUTAlloc = dict()
        for col, luts in colMap.items():
            #find a free column 
            rows = set()
            for l,r in luts:
                rows.add(r)
                if self.__debug: print('lutname: {}'.format(lutGraph.vs[l]['name']))
            freeCol = self.__findRows(crossbar,rows,freeCol)
            if self.__debug: print('New allocation: {} for luts : {}'.format(freeCol,luts))
            flipSteps = []
            if freeCol != None: 
                for l,r in luts:
                    flipSteps.append(['NOT', [(r,col),(r,freeCol)], lutGraph.vs[l]['name']])
                    posLUTAlloc[l] = (r,col)
                    crossbar[r][freeCol] = 'RE_'+lutGraph.vs[l]['name']
                steps.append(flipSteps)
                
            else: # place individual LUTs serially
                for l,r in luts:
                    alloc = False 
                    for i in range(0,R):
                        if crossbar[i][col] == 1:
                            posLUTAlloc[l] = (i,col)
                            crossbar[i][col] = 'RE_'+lutGraph.vs[l]['name']
                            steps.append([['NOT', [(r,col),(i,col)], lutGraph.vs[l]['name']]])
                                         
                    if not alloc:
                        for i in range(0,C):
                            if crossbar[r][i] == 1:
                                posLUTAlloc[l] = (r,i)
                                crossbar[r][i] = 'RE_'+lutGraph.vs[l]['name']
                                steps.append([['NOT', [(r,col),(r,i), lutGraph.vs[l]['name']]]])
                                alloc = False 
                    if not alloc:
                        print('Positive result for {} failed'.format(l))
                        return None 
        if not self.__fastMode:self.__printCrossbar(crossbar, 'Finished placement')
        if not self.__fastMode:self.__showSteps(status,crossbar,steps)
        
        return steps

    def __flattenPath(self,path,goal):
        ''' returns the path from source to goal '''
        if path == None:
            return []
        lim = len(path.keys())
        flattened = []
        prev = -1
        for i in range(lim):
            prev = path[goal]
            if prev == None:
                break 
            flattened.append((prev,goal))
            goal = prev 
        flattened.reverse()

        if prev != None:
            return None 
        else:
            return flattened
        
    def __getFreePos(self, dimType, val, crossbar):
        ''' Returns a list of free devices 
            dimType = 'r' or 'c'
            val = row or column to search
        '''
        freePos = []
        R,C = len(crossbar), len(crossbar[0])
        if dimType == 'c':
            for r in range(R):
                if crossbar[r][val] == 1:
                    freePos.append(r)
        elif dimType == 'r':
            for c in range(C):
                if crossbar[val][c] == 1:
                    freePos.append(c)
            
        return freePos 

    def __getEntryDim(self, entry, entryType):
        ''' Returns the positions with the specified entryType '''
        pos = []
        for i in range(len(entry[0])):

            if entry[0][i] == entryType:
                pos.append(entry[1][i])
        return pos 
        
    def __alignLUT(self, var, path, newCrossbar, newSteps, filledCrossbar):
        i = 0
        for source,dest in path:
            if i % 2 == 0:
                pref = str(var)
            else:
                pref = '~'+str(var)
            if str(newCrossbar[dest[0]][dest[1]]) != '1' :
                print('error in copy')
                sys.exit()
            newCrossbar[dest[0]][dest[1]] = pref
            filledCrossbar[dest[0]][dest[1]] = pref
            
            newSteps.append(['COPY', (source[0],source[1]),(dest[0],dest[1]), pref])
            
            i = i+1
    

    def __verticalCopy(self,label,source,rows,newCrossbar,newSteps,filledCrossbar):
        ''' Copies a variable with "label" vertically across a column '''
         
        for row in rows:
            if str(newCrossbar[row][source[1]]) != '1':
                continue 
            newCrossbar[row][source[1]] = label
            filledCrossbar[row][source[1]] = label
            if source[0] == row:
                continue 
            
            newSteps.append(['COPY', source,(row,source[1]), label])
            

    def __placeInputs(self, vertex, lvar, posLoc, negLoc, col, fiCrossbar, newCrossbar):
        
        newSteps = []
        '''
        if posLoc != []:
            inputMap[lvar] = [(negLoc[0],col), None]
        
        else:
            inputMap[lvar] = [(posLoc[0],col),(negLoc[0],col)]
        '''
        # Update the crossbar --- ignores the actual cost of placing
        for rowIndex in posLoc:
            #rowIndex = self.__getLoc(start,end,blocked,j,'r')
            if self.__debug: print('newpos: var {}  placed at ({},{})'.format(lvar,rowIndex,col))
            newCrossbar[rowIndex][col] = '~'+lvar
            newSteps.append(['INPUT', (rowIndex,col), '~'+lvar])
            fiCrossbar[rowIndex][col] = '~'+str(vertex)                   # update crossbar 
                
        for rowIndex in negLoc:
            #rowIndex = self.__getLoc(start,end,blocked,j,'r')
            if self.__debug: print('newneg: var {}  placed at ({},{})'.format(lvar,rowIndex,col))
            newCrossbar[rowIndex][col] = lvar
            newSteps.append(['INPUT', (rowIndex,col), lvar])
            fiCrossbar[rowIndex][col] = str(vertex)
        return newSteps

    def __placeCrossbar(self, lutGraph, inputs, crossbar, schedule, alloc): #timeslots, alloc, blocked=None):
        ''' Maps a given schedule to the actual crossbar 
            Returns:
                status : `True` if successful, otherwise `False` 
                    if False, schedule might have to be changed or additional reset can be used
                crossbar : Updated crossbar state      
                steps : updated steps 
        '''
        R,C = len(crossbar), len(crossbar[0])
        timeslots = list(schedule.keys())
        timeslots.sort()
        print('Placing crossbar for timeslots {}'.format(timeslots))
        # generating a filled crossbar to be used during mapping.
        # nothing is blocked at the start of evaluation
        fiCrossbar = copy.deepcopy(crossbar)
        for t in timeslots:
            sc = schedule[t]
            if sc[0] == 'luts':
                for lut, startr, startc, resr, resc in sc[1]:
                    if startr == resr:
                        rowLim = resr+1
                    else:
                        rowLim = resr
                    for i in range(startr,rowLim):
                            
                        for j in range(startc,resc+1):
                            if str(fiCrossbar[i][j]) != '1':
                                print('Invalid schedule {}'.format(sc[1]))
                                sys.exit(1)
                                
                            fiCrossbar[i][j] = -1*lut
                    fiCrossbar[resr][resc] = -1*lut 
            elif sc[0] == 'reset':
                break 
        newCrossbar = copy.deepcopy(crossbar)
        newSteps = []
        if self.__debug: self.__printCrossbar(fiCrossbar,'Filled crossbar')   
         
        # location on an input variable in the crossbar
        # [positive_loc, negative_loc]
        inputMap = dict()
        #generate the steps now using the filled crossbar 
        self.__blocked = ['',[]]
        for t in timeslots:
            sc = schedule[t]
            if self.__debug: print('schedule [{}/{}] : {}'.format(t,timeslots,sc))
            if sc[0] == 'luts':
                

                mappingStatus, nC, nS = self.__slotMapper(lutGraph, inputs, newCrossbar, fiCrossbar, sc[1], alloc, self.__blocked)
                if self.__debug: self.__printCrossbar(nC,'Crossbar after mapping {}'.format(t))
                if mappingStatus:
                    newCrossbar = nC
                    for r in range(R):
                        for c in range(C):
                            if str(fiCrossbar[r][c]) == '1' and \
                                str(nC[r][c]) != '1':
                                fiCrossbar[r][c] = nC[r][c] 

                    newSteps = newSteps + nS

                else:
                    return False, crossbar, []
               
            elif sc[0] == 'reset':
                # add the steps for the reset
                
                newSteps.append(['reset', sc[1][2], sc[1][0]])# TODO : check   
                #print(sc[1][0],sc[1][0]=='c',sc[1][0]=='r',newSteps[-1])          
                # free the crossbar 
                if sc[1][0] == 'r':
                    for r in sc[1][2]:
                        for c in range(0,C):
                            newCrossbar[r][c] = 1
                            #print('reset[{}] {}{}'.format(sc[1],r,c))
                elif sc[1][0] == 'c':
                    for r in range(0,R):
                        for c in sc[1][2]:
                            newCrossbar[r][c] = 1 
                            #print('reset[{}] {}{}'.format(sc[1],r,c))  
                self.__blocked[0] = sc[1][0]
                self.__blocked[1] = sc[1][1] # 'r' or 'c', blocked dimensions 
                # generate the blocked crossbar 
                # generate filled crossbar 
                fiCrossbar = copy.deepcopy(newCrossbar)
                for t1 in timeslots:
                    sc = schedule[t1]
                    if t1 <= t:
                        continue 
                    if sc[0] == 'luts':
                        
                        for lut, startr, startc, resr, resc in sc[1]:
                            if startr == resr:
                                rowLim = resr+1
                            else:
                                rowLim = resr
                            for i in range(startr,rowLim):
                                if self.__blocked != None and self.__blocked[0] == 'r' and i in self.__blocked[1]:
                                    continue 
                                    
                                for j in range(startc,resc+1):
                                    if self.__blocked != None and self.__blocked[0] == 'c' and j in self.__blocked[1]:
                                        continue
                                    if str(fiCrossbar[i][j]) != '1':
                                        print('Invalid schedule {}'.format(sc[1]))
                                        sys.exit(1)
                                    fiCrossbar[i][j] = -1*lut
                            fiCrossbar[resr][resc] = -1*lut 
                    elif sc[0] == 'reset':
                        break 
                    
        if not self.__fastMode: self.__printCrossbar(newCrossbar, 'Updated crossbar state :'+str(lut))      
        if self.__debug: print('Steps after place crossbar :')
        for s in newSteps:
            if self.__debug: print(s)
        return True, newCrossbar, newSteps              
    
    
    def __heuristic(self, dest, vertex):
        ''' Estimates the cost of the destination from a given vertex
            The heuristic is admissible. '''    
        (x1, y1) = vertex
        r = dest['r']
        c = dest['c']
        cost = 0
        if x1 in r and y1 in c:
            cost = 0
        elif x1 in r:
            cost = 1
        elif y1 in c:
            cost = 1
        else:
            cost = 2
        return cost 
    
    def __getNeighbours(self,crossbar,vertex,dest={'r':[],'c':[]}):
        ''' get the cells which are free in the row/column of the specified vertex ''' 
        neighbours = list()
        R,C = len(crossbar), len(crossbar[0])
        r,c = vertex[0], vertex[1]
        #self.__printCrossbar(crossbar)
        goalr = dest['r']
        goalc = dest['c']
        # vertical search
        for i in range(R):
            if i != r and (crossbar[i][c] == 1  or \
                (i in goalr and c in goalc)) : # empty cell or goal state
                neighbours.append((i,c))   
        # horizontal search
        for j in range(C):
            if c != j and (crossbar[r][j] == 1 or \
                (r in goalr and j in goalc)): # empty cell or goal state
                neighbours.append((r,j))
        if self.__debug: print('Vertex: {} Neighbours: {}'.format(vertex,neighbours))
        return neighbours 
    
    
    def __a_star_search(self, crossbar, start, dest, pathtype=None):
        '''
            Uses A* algorithm to determine a path from source to dest in the crossbar
            source : a unique cell in the crossbar
            dest : {'r': [], 'c':[]} can be a range of cells in the crossbar
            pathtype: specifies whether the path needs to be odd or even
        '''
        if self.__debug: print('Searching for {} -> {} with {} path'.format(start,dest,pathtype))
        if self.__debug: self.__printCrossbar(crossbar,'A* search')
        searchQ = []
        heappush(searchQ, (0,start))
        
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        goal = False 
        current = None 
        while searchQ != list():
            
            cost, current = heappop(searchQ)
            if self.__debug: print('current: {} \nsearchQ:{} cost:{}'.format(current, searchQ, cost))
            if self.__heuristic(dest,current) == 0: # goal state reached
                goal = True 
                break
            
            for next in self.__getNeighbours(crossbar,current,dest):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.__heuristic(dest, next)
                    heappush(searchQ, (priority, next))
                    
                    came_from[next] = current
        if not goal:
            if self.__debug: print('Path was not found to the target')
            path = None 
        else:
            path = self.__flattenPath(came_from, current)
                
        if pathtype != None and goal :     
            # compute path length type : even | odd 
            if (pathtype == 'even' and cost_so_far[current]% 2 != 0)  or \
                (pathtype == 'odd' and cost_so_far[current] % 2 == 0):
                    # find an additional node in between 
                    pathUpdate = False 
                    for posi in range(len(path)):
                        posBeg, posEnd = path[posi] 
                        if self.__debug: print(posBeg, posEnd)
                        if posBeg[0] == posEnd[0] : # same row 
                            for c in range(len(crossbar[0])):
                                if c not in {posBeg[1], posEnd[1]} and crossbar[posBeg[0]][c] == 1:
                                    path.insert(posi,[posBeg,(posBeg[0],c)])
                                    path.insert(posi+1,[(posBeg[0],c),posEnd])
                                    path.pop(posi+2)
                                    pathUpdate = True 
                                    break 
                        else : # same column
                            for r in range(len(crossbar)):
                                if r not in {posBeg[0], posEnd[0]} and crossbar[r][posBeg[1]] == 1:

                                    path.insert(posi,[posBeg,(r,posBeg[1])])
                                    path.insert(posi+1,[(r,posBeg[1]),posEnd])
                                    path.pop(posi+2)
                                    pathUpdate = True 
                                    break
                        
                        if pathUpdate:
                            if self.__debug: print('Appended path with an extra node for meeting pathtype : %s' % pathtype)
                            break 
                    
        
        if self.__debug: print('Path: {} --> Goal {}'.format(path,goal))
        return goal, path, current

    def __slotMapper(self, lutGraph, inputs, crossbar, filledCrossbar, slot, alloc, blocked=None):
        ''' Attempt to schedule all LUTs in a given slot of the schedule 
            > optimize sharing across the LUTs
            > optimize the A* search costs by using different sources 
            
            Returns:
                status : `True` if successful, otherwise `False` 
                    if False, schedule might have to be changed or additional reset can be used
                crossbar : Updated crossbar state      
                steps : updated steps 
        '''
        colLogic = dict()

        slotLutInputs = []
        for  lut, startr, startc, resr, resc in slot:
            lutObj = lutGraph.vs[lut]['lut']
            if self.__debug:
                print('Terms {}: \n{}'.format(lutObj.output,lutObj.inputs))
                for l in lutObj.logic:
                    print(l)
                    
            slotInputs = []
            for i in range(len(lutObj.inputs)):
                lname = lutObj.inputs[i] # this is name!
                v = lutGraph.vs.select(name=lname)
                lvar = v[0].index
                slotInputs.append(lname)
            slotLutInputs.append(slotInputs)
            
        
        if len(slot) > 1:    
            # multiple LUTs are scheduled in this slot 
            #TODO: Enable for SAT
            #succ,alignedInputs = maxalign.maxAlign(slotLutInputs)
            succ, alignedInputs = True, slotLutInputs
            if not succ:
                print('Alignment failed')
                self.__log.addParam('error', 'alignment of inputs failed')
                return False, None, None 
        else:
            alignedInputs = slotLutInputs

        if self.__debug: print('aligned inputs: {} \n'.format(alignedInputs))
    

        l = 0
        for  lut, startr, startc, resr, resc in slot:
            lutObj = lutGraph.vs[lut]['lut']
            available = []
            for c in range(startc, resc):
                if 'c' not in blocked[0] or c not in blocked[1]:
                    available.append(c)
            rowAvail = []
            for r in range(startr, resr):
                if 'r' not in blocked[0] or r not in blocked[1]:
                    rowAvail.append(r)
            inputDict = dict()

            for  i in range(len(lutObj.inputs)):
                inp = lutObj.inputs[i]
                inputDict[inp] = []

                for v in lutObj.logic:
                    inputDict[inp].append(v[i])
            
            if self.__debug: print('InputDict:',inputDict)

            orderedInputs = alignedInputs[l]
            l = l+1

            # map the aligned inputs to the columns 
            for i in range(len(lutObj.inputs)):
                col = available[i]
                lutInput = orderedInputs[i]

                if col not in colLogic.keys():
                    colLogic[col] = dict()
                
                if lutInput not in colLogic[col].keys():
                    colLogic[col][lutInput] = [[], []] # type row 

                for j in range(len(inputDict[lutInput])):
                    sopType = inputDict[lutInput][j]
                    row = rowAvail[j]
                    colLogic[col][lutInput][0].append(sopType)
                    colLogic[col][lutInput][1].append(row)
        if self.__debug: print('Col logic:',colLogic)

        # now align the inputs across the columns 

        # consider a variable at each time 
        cols = list(colLogic.keys())
        cols.sort()
        newSteps = []
        newCrossbar = copy.deepcopy(crossbar)
        for c in cols:

            for var, varDetails in colLogic[c].items():

                    
                vertex = lutGraph.vs.select(name=var)
                v = vertex[0].index

                

                # do zeroCount, oneCount, dcCount 
                negCount = colLogic[c][var][0].count('0') 
                posCount = colLogic[c][var][0].count('1')
                dcCount = colLogic[c][var][0].count('-')
                
                negLoc = self.__getEntryDim(colLogic[c][var], '0')
                posLoc = self.__getEntryDim(colLogic[c][var], '1')
                dcLoc = self.__getEntryDim(colLogic[c][var], '-')
                outLoc = self.__getFreePos('c',c,filledCrossbar)
                

                pos = posCount > 0 
                neg = negCount > 0
                dc = dcCount > 0 or len(outLoc) > 0 

                # check if v is input or a constant LUT 
                if var in lutGraph['inputs']:
                    inputSteps = self.__placeInputs(v,var,posLoc,negLoc,c,filledCrossbar,newCrossbar)
                    newSteps = newSteps + inputSteps
                    if self.__debug: self.__printCrossbar(newCrossbar, 'After placing inputs, newCrossbar')
                    continue
                elif lutGraph.vs[v]['lut'].isConstant():
                    print('Encounted constant LUT as input {}'.format(var))
                    continue 
                
                startSearch = (alloc[v][0], alloc[v][1]) # this location has the negated value
                # 0 Location
                dest = {'r': list(negLoc), 'c': [c]}
                zeroGoal, zeroPath, zeroDest = self.__a_star_search(filledCrossbar,startSearch, dest, 'odd')
                
                # 1 Location
                dest = {'r': list(posLoc), 'c': [c]}
                oneGoal, onePath, oneDest = self.__a_star_search(filledCrossbar,startSearch, dest, 'even')
                
                # dont care or neighbour locations
                # zero 
                dest = {'r': dcLoc + outLoc, 'c': [c]}
                dcOGoal, dcOPath, dcODest = self.__a_star_search(filledCrossbar,startSearch, dest, 'even')
                # one 
                dest = {'r': dcLoc + outLoc, 'c': [c]}
                dcZGoal, dcZPath, dcZDest = self.__a_star_search(filledCrossbar,startSearch, dest, 'odd')

                if self.__debug:
                    self.__printCrossbar(filledCrossbar, 'filled Crossbar in slotMapper')
                    print('Col{} logic for var {}: {}'.format(c,var,colLogic[c][var]))
                    print('All the paths from ({}.{}):'.format(alloc[v][0], alloc[v][1]))
                    print('Outside loc: {}'.format(outLoc))
                    print('Zero: {} {}'.format(zeroPath, zeroDest))
                    print('One: {} {}'.format(onePath, oneDest))
                    print('DcZ: {} {}'.format(dcZPath, dcZDest))
                    print('DcO: {} {}'.format(dcOPath, dcODest))
                    
                '''
                zeroPath = self.__flattenPath(zeroPath,zeroDest)  
                onePath = self.__flattenPath(onePath,oneDest)
                dcOPath = self.__flattenPath(dcOPath,dcODest)
                dcZPath = self.__flattenPath(dcZPath,dcZDest)
                '''
                infinite = len(crossbar)**2
                if zeroGoal:
                    zCost = len(zeroPath)
                else:
                    zCost = infinite 
                if oneGoal:
                    oCost = len(onePath)
                else:
                    oCost = infinite 
                
                if dcOGoal:
                    dcOCost = len(dcOPath) + 1 
                else:
                    dcOCost = infinite 
                
                if dcZGoal:
                    dcZCost = len(dcZPath) + 1 
                else:
                    dcZCost = infinite 
                # cases for mapping 
                if neg and pos and dc:
                    
                    #find the lowest cost 
                    if oneGoal: 
                        assert(oneGoal==zeroGoal)
                        assert(oneGoal==dcOGoal)
                        assert(oneGoal==dcZGoal)

                        minCost = min([zCost, oCost, dcOCost, dcZCost])
                        if minCost == infinite:
                            print('Search failed')
                            self.__log.addParam('error', 'A* search failed')
                            return False, crossbar, []

                        if minCost == zCost:
                            # update the steps 
                            self.__alignLUT(var, zeroPath,newCrossbar,newSteps,filledCrossbar)

                            #  write to the `1' places  ~var
                            label = '~'+var
                            self.__verticalCopy(label,zeroDest,posLoc, newCrossbar,newSteps,filledCrossbar) 
                                
                            # write to the '0' places `var
                            label = var 
                            src = (posLoc[-1],c)
                            self.__verticalCopy(label,src,negLoc, newCrossbar,newSteps,filledCrossbar) 
                            

                        elif minCost == oCost:
                            # update steps onePath
                            self.__alignLUT(var, onePath,newCrossbar,newSteps,filledCrossbar)

                            # write "0"
                            label = var
                            self.__verticalCopy(label,oneDest, negLoc, newCrossbar,newSteps,filledCrossbar) 
                            
                                
                            # write "1"
                            label = '~'+var
                            src = (negLoc[-1],c)
                            self.__verticalCopy(label,src,posLoc, newCrossbar,newSteps,filledCrossbar) 
                            
                                
                        elif minCost == dcOCost:
                            # update steps dcOPath
                            self.__alignLUT(var, dcOPath,newCrossbar,newSteps,filledCrossbar)

                            # write "0"
                            label = var
                            self.__verticalCopy(label,dcODest, negLoc, newCrossbar,newSteps,filledCrossbar) 
                                
                            # write "1"
                            label = '~'+var
                            src = (negLoc[-1],c)
                            self.__verticalCopy(label,src,posLoc, newCrossbar,newSteps,filledCrossbar) 
                            
                        else:
                            # update steps dcZPath
                            self.__alignLUT(var, dcZPath,newCrossbar,newSteps,filledCrossbar)

                            # write "1"
                            label = '~'+var
                            self.__verticalCopy(label,dcZDest,posLoc, newCrossbar,newSteps,filledCrossbar) 
                                
                            # write "0"
                            label = var 
                            src = (posLoc[-1],c)
                            self.__verticalCopy(label,src,negLoc, newCrossbar,newSteps,filledCrossbar) 

                    else:
                        self.__log.addParam('error', 'A* search failed')
                        return False, crossbar, [] 

                elif  neg and pos:
                    minCost = min([zCost, oCost])
                    if minCost == infinite:
                        print('Search Failed')
                        self.__log.addParam('error', 'A* search failed')
                        return False, crossbar, []


                    if minCost == zCost:
                        # update the steps 
                        self.__alignLUT(var, zeroPath,newCrossbar,newSteps,filledCrossbar)

                        #  write to the `1' places  ~var
                        label = '~'+var
                        self.__verticalCopy(label,zeroDest,posLoc, newCrossbar,newSteps,filledCrossbar) 
                            
                        # write to the '0' places `var
                        label = var 
                        src = (posLoc[-1],c)
                        self.__verticalCopy(label,src,negLoc, newCrossbar,newSteps,filledCrossbar) 
                        

                    elif minCost == oCost:
                        # update steps onePath
                        self.__alignLUT(var, onePath,newCrossbar,newSteps,filledCrossbar)

                        # write "0"
                        label = var
                        self.__verticalCopy(label,oneDest, negLoc, newCrossbar,newSteps,filledCrossbar) 
                        
                            
                        # write "1"
                        label = '~'+var
                        src = (negLoc[-1],c)
                        self.__verticalCopy(label,src,posLoc, newCrossbar,newSteps,filledCrossbar) 
                    

                elif neg and dc:
                    if not dcOGoal:
                        self.__log.addParam('error', 'A* search failed')
                        return False, crossbar, []
                    # update steps dcOPath
                    self.__alignLUT(var, dcOPath,newCrossbar,newSteps,filledCrossbar)

                    # write "0"
                    label = var
                    self.__verticalCopy(label,dcODest, negLoc, newCrossbar,newSteps,filledCrossbar) 
                            

                elif negCount > 1:
                    print()
                    self.__log.addParam('error', 'A* search failed. Only Os')
                    print('This case is too costly! Only 0 entries with x.')
                    return False, crossbar, []
                    
                elif negCount == 1:
                    # update steps zeroPath
                    self.__alignLUT(var, zeroPath,newCrossbar,newSteps,filledCrossbar)


                elif pos and dc:
                    if not dcZGoal:
                        return False, crossbar, []
                    # update steps dcOPath
                    self.__alignLUT(var, dcZPath,newCrossbar,newSteps,filledCrossbar)

                    # write "1"
                    label = '~'+var
                    self.__verticalCopy(label,dcZDest, posLoc, newCrossbar,newSteps,filledCrossbar) 
                    

                elif posCount > 1:
                    self.__log.addParam('error', 'A* search failed. Only 1s')
                    print('This case is too costly! Only 1 entries with x.')
                    return False, crossbar, []
                    
                
                elif posCount == 1:
                    # update steps onePath
                    self.__alignLUT(var, onePath,newCrossbar,newSteps,filledCrossbar)
        # set each value to 0 if the variable does not exist(-) in that row 
        for c in cols:
            varMissingLoc= []
            for var, varDetails in colLogic[c].items():

                
                vertex = lutGraph.vs.select(name=var)
                v = vertex[0].index
                dcLoc = self.__getEntryDim(colLogic[c][var], '-')
                varMissingLoc = varMissingLoc + dcLoc
            if varMissingLoc != []:
                step = ['SETZERO', [], 'col{}'.format(c)]
                for r in varMissingLoc:
                    newCrossbar[r][c] = '0'
                    step[1].append((r,c))
                newSteps.append(step)
        
        
        vNORs = []
        hNORs = []
        # schedule the HNORs 
        for  lut, startr, startc, resr, resc in slot:
            lutObj = lutGraph.vs[lut]['lut']
            cols = []
            
            for c in range(startc, resc+1):
                if 'c' not in blocked[0] or c not in blocked[1]:
                    cols.append(c)

            rowAvail = []

            vNOR = ['VNOR', [], lutGraph.vs[lut]['name']]
            
            for r in range(startr, resr+1):
                hNOR = ['HNOR', [], 'hN'+lutGraph.vs[lut]['name']]
                if 'r' not in blocked[0] or r not in blocked[1]:
                    #rowAvail.append(r)
                    if r != resr:
                        for c in cols:
                            hNOR[1].append((r,c))
                        if hNOR[1] == []:
                            continue 
                        hNORs.append(hNOR)
                    
                    if str(newCrossbar[r][resc]) != '1' :
                        print('error in NOR computation for lut {}'.format(lut))
                        sys.exit()
                    if r != resr:
                        newCrossbar[r][resc] = 'hN'+lutGraph.vs[lut]['name']
                    else:
                        newCrossbar[r][resc] = 'vN'+lutGraph.vs[lut]['name']
                    vNOR[1].append((r,resc))
                
                
                    
            if vNOR[1] != []:
                vNORs.append(vNOR)
        
        newSteps.append(hNORs)

        for v in vNORs:
            if len(v[1]) == 2: # there is a single operation
                v[0] = 'VNOT'
            assert(v  != [])
            newSteps.append(v)     

        if self.__debug: print('newSteps: {}'.format(newSteps))           

        # Schedule VNOR/VNOTs
        
        return True, newCrossbar, newSteps 

    def __printCrossbar(self,crossbar,msg=None):
        ''' print intermediate crossbar state '''
        

        if msg != None:
            print(msg+':')
        if len(crossbar) > 20:
            print('Crossbar dimensions are too big for printing (upto 20x20).')
            return 
        for r in crossbar:
            for c in r:
                print('%9s ' % (c),end='')
            print('',end='\n')
        
    def __findRows(self,crossbar,rows,freeCol):
        ''' returns columns with the `rows` free 
            Checks the freeCol first '''
        if freeCol != None:
            alloc = True 
            for r in rows:
                if crossbar[r][freeCol] != 1:
                    alloc = False 
                    break
            if alloc:
                return freeCol 
        C = len(crossbar[0])
        for col in range(0,C):
            if col == freeCol:
                continue 
            alloc = True  
            for r in rows:
                if crossbar[r][col] != 1:
                    alloc = False 
                    break
            if alloc:
                return col 
        return False 
    