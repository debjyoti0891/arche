import copy
from igraph import *
import datetime
import logging
import sys
import itertools
import math
import time



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
        
        # z3 solver
        s = Solver() 
        
        maxSteps = 0
        for graph in self.graphs:
            maxSteps = maxSteps + len(graph.vs)
        
        for i in range(self.__graphCount):
            graph = self.__graphs[i]
            colorVars[i] = dict()
            timeVars[i] = dict()
            
            for v in graph.vs:
                colorVars[i][v['name']] = Int('c_'+v['name']+'_'+str(i))
                timeVars[i][v['name']] = Int('t_'+v['name']+'_'+str(i))
                
                s.add(colorVars[i][v['name']] > 0, colorVars[i][v['name']] <= maxSteps)
                s.add(timeVars[i][v['name']] > 0, timeVars[i][v['name']] <= maxSteps)
            #distinct 
            Distinct(list(colorVars[i].values()))
            Distinct(list(timeVars[i].values()))
            
            s.check()
    
            printSolution(s)
            
    def printSolution(s, colorVar, timeVars, outf=None):
        if s.check() == sat:
            m = s.model()
            ''' Print format 
                cycle color g1 g2 ...
             
            '''
            #TODO : update
            
            r = [ [ m.evaluate(X[i][j]) for j in range(9) ]
                  for i in range(9) ]
                  
            print_matrix(r)
        else:
            print("failed to solve")
            
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: python3 mimd.py graph1 graph2 solution')
        sys.exit()
    techMapper = MIMD([])
    techMapper.readGraph([sys.argv[1],sys.argv[2]])
    techMapper.checkSolution(sys.argv[3])
    
