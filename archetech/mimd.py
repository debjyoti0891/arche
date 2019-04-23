import copy
from igraph import *
import datetime
import logging
import sys
import itertools
import math
import time
from z3 import *



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
        
    def readGraph(self,edgeFiles):
        ''' reads a graph in edge list format 
            
            The nodes are numbered from 0 onwards. igraph core
            might have issues if there are missing nodes. 
        '''
        for edgeFile in edgeFiles:
            graph= Graph.Read_Ncol(edgeFile, directed=True)   
            self.__graphs.append(graph)
        self.__graphCount = len(self.__graphs)
            
    def readSolution(self,solFile):
        pass 
    
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

    def genSolution(self):
        
        
        # create the variables for ni and ci
        colorVars = dict()
        timeVars  = dict()
        degreeGroups = dict() 

        # z3 solver
        s = Optimize() 
        
        maxSteps = 0
        for graph in self.__graphs:
            maxSteps = maxSteps + len(graph.vs)
        cost = Int('delay')

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
            print(graph.degree(type='in'))
            
            for v in graph.vs:
                #precedence constraints 
                for p in graph.neighbors(v,IN):
                    pname = graph.vs[p]['name']
                    s.add(timeVars[i][v['name']] > timeVars[i][pname])

              
            #distinct 
            s.add(Distinct(list(colorVars[i].values())))
            s.add(Distinct(list(timeVars[i].values())))
            
        for i in range(self.__graphCount):
            graphi = self.__graphs[i]
            degi = graphi.degree(type='in')
            for j in range(i+1, self.__graphCount):
                graphj = self.__graphs[j] 
                
                degj = graphi.degree(type='in')

                for di in range(len(degi)):
                    viname = graphi.vs[di]['name']
                    
                    for dj in range(len(degj)):
                        vjname = graphj.vs[dj]['name']
                            
                        if degi[di] != degj[dj] or \
                             (len(graphi.neighbors(graphi.vs[di],IN)) != \
                             len(graphj.neighbors(graphj.vs[dj],IN)) ):
                            s.add(timeVars[i][viname] != timeVars[j][vjname])
                        elif degi[di] != 0: #two nodes might be executed in parallel 
                            
                            predi = graphi.vs(graphi.neighbors(graphi.vs[di],IN))
                            predj = graphj.vs(graphj.neighbors(graphj.vs[dj],IN))
                            for perm in itertools.permutations(predj):
                                print(di,dj,perm, predi)

                            orClause = False
                            
                            for perm in itertools.permutations(predj):
                                andClause = True 
                                for k in range(len(perm)):
                                    pi = predi[k]['name']
                                    pj = perm[k]['name']
                                    print(colorVars[i][pi])
                                    print(colorVars[j][pj])
                                    andClause = And(andClause,\
                                     colorVars[i][pi]==colorVars[j][pj])
                                orClause = Or(orClause, andClause)
                            
                            s.add(If(orClause,
                                timeVars[i][viname] == timeVars[j][vjname],
                                timeVars[i][viname] != timeVars[j][vjname]))    
        h = s.minimize(cost)
    
        self.printSolution(s,colorVars, timeVars)
            
    def printSolution(self,s, colorVars, timeVars, outf=None):
        if s.check() == sat:
            m = s.model()
            ''' Print format 
                cycle color g1 g2 ...
             
            '''
            #TODO : update
            
            for i in range(self.__graphCount):
                graph = self.__graphs[i] 

                for v in graph.vs:
                    print("graph" ,i,":",m.evaluate(timeVars[i][v['name']]), \
                            m.evaluate(colorVars[i][v['name']]))
                  
        else:
            print("failed to solve")
            
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python3 mimd.py graph1 graph2 solution')
        sys.exit()
    techMapper = MIMD([])
    techMapper.readGraph([sys.argv[1],sys.argv[2]])
    techMapper.genSolution()
    techMapper.checkSolution(sys.argv[3])
    
