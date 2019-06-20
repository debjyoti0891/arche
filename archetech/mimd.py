import copy
from igraph import *
import datetime
import logging
import sys
import itertools
import math
import time
from z3 import *

import archeio.solution



class MIMD:
    ''' This implements  a technology mapping scheme for MAGIC 
        
        Each function is assigned a single row for execution. However,
        multiple functions can be assigned together, one per row. By 
        executing multiple instances of the same function, SIMD can be
        achieved as well. 
        
        Complexity of controller has to be evaluated as well. 
        '''
        

    def __init__(self,graphs,devLimit=None,reuse=False):
        
        self.__graphs = graphs
        self.__devLimit = devLimit 
        self.__reuse = reuse 
        self.__graphCount = 0
        self.__sol = archeio.solution.Solution()
        
    def readGraph(self,edgeFiles):
        ''' reads a graph in edge list format 
            
            The nodes are numbered from 0 onwards. igraph core
            might have issues if there are missing nodes. 
        '''
        for edgeFile in edgeFiles:
            graph= Graph.Read_Ncol(edgeFile, directed=True)   
            
            self.__graphs.append(graph)
            
            if self.__sol.getParam('vertices') == None:
                self.__sol.addParam('vertices', [])
            
            vertices = self.__sol.getParam('vertices')
            vertices.append(len(graph.vs))
            self.__sol.addParam('vertices', vertices)
            if len(graph.vs) > 100:
                print('Benchmark size is too large %d' % (vertics))
                return None
            
        self.__graphCount = len(self.__graphs)
        return self.__graphCount
    
    
    def checkSolution(self, solution):
        ''' Does a feasibility check of the given solution 
            solution file format [for k graphs]
            cycle color node_graph_1 ... node_graph_k 
            Mark empty slots with single dash [-]
        '''
        schedule = dict()
        
        graphSolutions = [dict() for i in range(self.__graphCount)]
        result = True 
        # load the solution 
        with open(solution) as f:
            
            for l in f:
                line = l[:-1]
                if line.find('//') >= 0:
                    line = line[:line.find('//')]
                    if line == '':
                        continue 
                line = line.split()
                cycle = line[0]
                if len(line) != self.__graphCount+2:
                    print('Error: Invalid line. Number of nodes in line is invalid')
                    print(l)
                    result = False
                #print(line,cycle)    
                for i in range(len(line[2:])):
                    if line[i+2] != '-':
                        #check if one node is assigned more than once
                        if line[i+2] in graphSolutions[i].keys():
                            print('Error: Multiple assignemt to node %s' % (line[i+2]))
                            result = False
                        else:
    
                            graphSolutions[i][line[i+2]] = [int(cycle), line[1]]
                
                schedule[int(cycle)] = line[1:]
             
                    
                    

        for i in range(self.__graphCount):
            graph = self.__graphs[i]
            colorset = set()
            for v in graph.vs:
                # check if all nodes have been assigned a time slot 
                if v['name'] not in graphSolutions[i].keys():
                    print('Error: Solution for vertex %s in graph %d not found' \
                        % (v['name'],i))
                    result = False 
                    
                # check for precedence constraints in the individual graph 
                for p in graph.neighbors(v,IN):
                    #print(v.index ,'<-',p)
                    pname = graph.vs[p]['name']
                    
                    if graphSolutions[i][v['name']][0] <= graphSolutions[i][pname][0]:
                        print('Error: Invalid ordering of nodes %s <- %s' % \
                            (v['name'],pname))
                        result = False 
                color = graphSolutions[i][v['name']][1] 
                if color in colorset:
                    print('Error: Multiple use of same color %s for graph %d ' % (color,i))
                    result = False 
                colorset.add(color)
        
        
        # check if parallel executions are valid
        # > number of precessors are same
        # > color set of predecessors is identical
        cycles = list(schedule.keys())
        cycles.sort()
        for cycle in cycles:
            operation = schedule[cycle]
            predColorSet = []
            
            for i in range(self.__graphCount):
                graph = self.__graphs[i]
                vname = operation[i+1]
                if vname == '-':
                    continue
                colorSet = set()
                v = graph.vs.find(name=vname)
                for p in graph.neighbors(v,IN):
                    pname = graph.vs[p]['name']
                    colorSet.add(graphSolutions[i][pname][1])
            
                predColorSet.append([colorSet,i,vname])
            
            for c in range(len(predColorSet)-1):
                if predColorSet[c][0] != predColorSet[c+1][0]:
                    print('Error: Invalid parallel operation for %s [graph %d] and %s [graph %s]' % (predColorSet[c][2],predColorSet[c][1],\
                    predColorSet[c+1][2],predColorSet[c+1][1]))
                    result = False 
        
        if result == False:
            return False
        print('Solution is valid')
        return True 
        
        
    def genMinSolution(self,outf = None,timelimit = None,printSol=None):
        minDelay, maxSteps = self.graphStats()
        self.__sol.addParam('minDelay', minDelay)
        self.__sol.addParam('maxDelay', maxSteps)
        
        minval = minDelay 
        maxval = maxSteps 
        
        solDelay = None 
        solDev = None
        
        delay, devices = self.genSolution(outf,timelimit,printSol,maxval)
        if delay == None:
            print('Trivial solution failed. Target delay : %d' % (maxval))
            self.__sol.addParam('trivial',False)
            return None,None
            
        self.__sol.addParam('trivial',True)    
        solDelay, solDev = delay, devices
        
        print('Trivial solution passed')
        while minval < maxval:
            midval = int( (minval+maxval)/2)
            print('Solving %d target delay [%d %d]' % (midval, minval,maxval))
            delay, devices = self.genSolution(outf,timelimit,printSol,midval)
            
            if delay == None:
                print('Solution failed for target delay %d' % (midval))
                minval = midval + 1
            else:
                print('Solution found  for target delay %d with %d device' % (delay, devices))
                solDelay, solDev = delay, devices
                maxval = midval - 1
                
        self.__sol.addParam('delay', solDelay)
        self.__sol.addParam('devices', solDev)
        
        return solDelay, solDev
            
         
    
    def genSolution(self, outf = None, timelimit = None, printSol=None, targetDelay=None): 
        
        minDelay, maxSteps = self.graphStats()
        # create the variables for ni and ci
        colorVars = dict()
        timeVars  = dict()
        degreeGroups = dict() 

        # z3 solver
        #s = Optimize() 
        s = Solver()
        if timelimit != None:
            s.set("timeout", timelimit)
            print('Timelimit of sat solving set to %d ms' % (timelimit))
        
        cost = Int('delay')
        if targetDelay == None:
            targetDelay = int(0.8*maxSteps)
        # bound the cost TODO: remove if using optimize!!!
        s.add(cost == targetDelay )
        print('Min delay: %d Max delay : %d Permitted: %d' % (minDelay, maxSteps, targetDelay))
        
        for i in range(self.__graphCount):
            graph = self.__graphs[i]
            colorVars[i] = dict()
            timeVars[i] = dict()
            for v in graph.vs:
                colorVars[i][v['name']] = Int('c_'+v['name']+'_'+str(i))
                timeVars[i][v['name']] = Int('t_'+v['name']+'_'+str(i))
                
                s.add(colorVars[i][v['name']] > 0, colorVars[i][v['name']] <= maxSteps)
                s.add(timeVars[i][v['name']] > 0, timeVars[i][v['name']] <= maxSteps)
                s.add(cost> timeVars[i][v['name']])
            #print(graph.degree(type='in'))
            
            for v in graph.vs:
                #precedence constraints 
                for p in graph.neighbors(v,IN):
                    pname = graph.vs[p]['name']
                    s.add(timeVars[i][v['name']] > timeVars[i][pname])

            
            #distinct 
            #print('colorvars;',colorVars[i])
            dColors = Distinct(*colorVars[i].values())
            s.add(dColors)
            dTime = Distinct(*timeVars[i].values())
            s.add(dTime) 
            '''
            
            # adding n^2 distiction constraints 
            l = list(colorVars[i].values())
            dis = list()
            for vali in range(len(l)):
                for valj in range(vali+1,len(l)):
                   dis.append(Not(l[vali] == l[valj]))
            s.add(And(*dis))
            '''            
            #[s.add(ci != cj) for ci in colorVars[i].values() for cj in colorVars[i].values if ci != cj]
        #h = s.minimize(cost)
    
        #self.printSolution(s,colorVars, timeVars, 'solved.txt')
        
        for i in range(self.__graphCount):
            graphi = self.__graphs[i]
            degi = graphi.degree(type='in')
            for j in range(i+1, self.__graphCount):
                graphj = self.__graphs[j] 
                
                degj = graphj.degree(type='in')

                for di in range(len(degi)):
                    viname = graphi.vs[di]['name']
                    
                    for dj in range(len(degj)):
                        vjname = graphj.vs[dj]['name']
                        # nodes without same column 
                        # can never be executed in parallel
                        s.add(
                            Implies(colorVars[i][viname] != colorVars[j][vjname], timeVars[i][viname] != timeVars[j][vjname]))  
                            
                             
                        if degi[di] != degj[dj] or \
                             (len(graphi.neighbors(graphi.vs[di],IN)) != \
                             len(graphj.neighbors(graphj.vs[dj],IN)) ):
                            s.add(timeVars[i][viname] != timeVars[j][vjname])
                        elif degi[di] != 0: #two nodes might be executed in parallel 
                           
                            
                            #print('parallel ', degi[di],':', viname, vjname)
                            predi = graphi.vs(graphi.neighbors(graphi.vs[di],IN))
                            predj = graphj.vs(graphj.neighbors(graphj.vs[dj],IN))
                            #for perm in itertools.permutations(predj):
                                #print(di,dj,perm, predi)

                            orClause = False
                            
                            for perm in itertools.permutations(predj):
                                andClause = True 
                                for k in range(len(perm)):
                                    pi = predi[k]['name']
                                    pj = perm[k]['name']
                                    #print(colorVars[i][pi], colorVars[j][pj])
                                    andClause = And(andClause,\
                                     colorVars[i][pi]==colorVars[j][pj])
                                orClause = Or(orClause, andClause)
                            
                            s.add(Implies(timeVars[i][viname] == timeVars[j][vjname],
                            And(orClause, colorVars[i][viname] == colorVars[j][vjname])))
                            '''
                            s.add(If(orClause,
                                timeVars[i][viname] == timeVars[j][vjname],
                                timeVars[i][viname] != timeVars[j][vjname]))    
                            '''
        
        #h = s.minimize(cost)
        
        
        delay, devices = self.printSolution(s,colorVars, timeVars, outf)
        
        return delay, devices 
        
    def graphStats(self):
        ''' determines the minimum and maximum delay for 
            scheduling the set of given graphs '''
        maxSteps = 0
        maxDegGraph = -1
        degiGraphs = dict()
        g = 0
        for graph in self.__graphs:
            maxSteps = maxSteps + len(graph.vs)
           
            degi = graph.degree(type='in')
            maxdeg = max(degi)
            maxDegGraph = max(maxdeg, maxDegGraph)
            degiGraphs[g] = dict()
            
            for i in range(maxdeg):
                degiGraphs[g][i] = degi.count(i)
            g = g+1
        
        
        minDelay = 0
        for d in range(maxDegGraph):
            maxdelay = 0
            for i in range(g):
                if d in degiGraphs[i].keys():
                    maxdelay = max(maxdelay, degiGraphs[i][d])
            minDelay = minDelay + maxdelay
        
        return minDelay, maxSteps
            
            
    def printSolution(self,s, colorVars, timeVars, outf=None, verbose = True):
        if s.check() == sat:
            m = s.model()
            ''' Print format 
                cycle color g1 g2 ...
             
            '''
            #TODO : update
            timeline = dict()
            maxTime = -1
            maxDevice = -1
            deviceSet = dict()
            for i in range(self.__graphCount):
                graph = self.__graphs[i] 
                deviceSet[i] = set()
                timeline[i] = dict()
                for v in graph.vs:
                    #print("graph" ,i, ": [" , v['name'],']:',m.evaluate(timeVars[i][v['name']]), \
                           # m.evaluate(colorVars[i][v['name']]))
                    timeStep = m[timeVars[i][v['name']]].as_long()
                    device   = m[colorVars[i][v['name']]].as_long()
                    timeline[i][timeStep] = [v['name'], device]
                    maxTime = max(maxTime, timeStep)
                    maxDevice = max(maxDevice, device)
                    deviceSet[i].add(device) 
            
            # reduce device count from the solution 
            # generated by sat
            # enable device sharing across graphs for serial operations
            commonDevice = deviceSet[0]
            deviceUsage = dict()
            
            devMap = dict()
            
                
            for i in range(1,self.__graphCount):
                commonDevice = commonDevice.intersection(deviceSet[i])
            
            # track device usage per graph 
            deviceUsage[0] = len(commonDevice)
            for i in range(1,self.__graphCount):
                deviceUsage[i] = len(commonDevice)
            
            # reassign common devices across graphs
            d = 0  
            for dev in commonDevice:
                d = d+1
                devMap[dev] = d
            
            print('Solution with %d steps found' % (maxTime))
            #print(timeline.keys())
            sol = list()
            for t in range(maxTime):
                sol.append([t+1, '-'] + [ '-' for j in range(self.__graphCount)])
                
                for g in range(self.__graphCount):
                    if t+1 in timeline[g].keys():
                        
                        
                        # do the actual of devices here reassignment     
                        if timeline[g][t+1][1] in commonDevice:
                            
                            timeline[g][t+1][1] = devMap[timeline[g][t+1][1]]
                        else:
                            # increment device id
                              
                            deviceUsage[g] = deviceUsage[g] + 1
                            
                            timeline[g][t+1][1] = deviceUsage[g]
                            
                        if sol[-1][1] != '-' and sol[-1][1] != timeline[g][t+1][1]:
                            print('Invalid solution. Two different device columns used in same cycle')
                            print(timeline[g][t+1][1], sol[-1][1])
                            return    
                            
                        sol[-1][1]   = timeline[g][t+1][1] #device 
                        sol[-1][2+g] = timeline[g][t+1][0] #node
                if verbose: print(t, sol[-1])
        
            
            if outf != None:
                with open(outf,'w') as f:
                    for t in range(maxTime):
                        for val in range(2+self.__graphCount):
                            f.write(str(sol[t][val])+' ')
                        f.write('\n')
            else:
                for t in range(maxTime):
                    for val in range(2+self.__graphCount):
                        if verbose: print('%4s' % (str(sol[t][val])+' '), end = '')
                    if verbose: print('', end='\n')
                    
            # return number of cycles and
            # number of devices required to map 
            maxDevice = max(deviceUsage.values())
            return maxTime, maxDevice
        else:
            print("Failed to solve")
            return None, None 
            
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 mimd.py graph1 graph2 solution')
        sys.exit()
    techMapper = MIMD([])
    techMapper.readGraph([sys.argv[1],sys.argv[2]])
    techMapper.genSolution()
    #techMapper.checkSolution(sys.argv[3])
    
