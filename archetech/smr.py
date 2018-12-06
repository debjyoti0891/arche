
from __future__ import print_function
from z3 import *
import copy
import datetime
import logging
import sys
import itertools
import math
import time

assigned_ = dict()
vertices_ = list() 
T_  = 0
model_ = None

def boolP(s):
    if(s):
        return 1
    else:
        return 0
        
def optiRegAlloc(g,V,out,N,T,logfile=None,verbose=False,timeLimit=None):
    global assigned_,vertices_,T_,model_
    if N > V:
        print('Reducing number of available registers to number of nodes')
        N = V
    print("Generating Constraints ", datetime.datetime.now())
    print("#Nodes: %d, #PO: %d" % (V, len(out)), end="")
    print(" #Devices: %d, #Cycles: %d" % (N,T))
    if timeLimit != None:
        print('Time limit: %d' % timeLimit) 
    g = copy.deepcopy(g) 
       # remove nodes that are leaves/pi
    piPurge = True
    #for v,l in g.items():
    #    print(v,'<',l)
    #print('vertices:', g.keys(), out)
    if piPurge:
        purge = set()
        for node,predList in g.items():
            if predList == list():
                purge.add(node)
        for node in purge:
            if node not in out: #out driven by BUF
                g.pop(node,None)
        for node in g.keys():
            predSet = set(g[node])
            g[node] = list(predSet-purge)
    vertices = list(g.keys())
    # assignment variables assigned_v_t
    assigned = dict()
    for v in vertices:
        assigned[v] = [ Bool("assigned_%s_%s" % (v, t)) for t in range(T+1) ] 

    logging.info("Considered nodes : %s, Devices: %s" % (len(vertices),N))


    #s = Solver()
    s = Then('simplify','smt').solver()
    #if timeLimit != None:
        #s.set('timeout', timeLimit )
        
    # all vertices are not assigned at the start
    for v in vertices:
       s.add(assigned[v][0] == False) 

    #final configuration 
    for v in out:
        s.add(assigned[v][T] == True)


    # register allocation 
    for t in range(1,T+1):
        for v in vertices:
            andTerm = []
            
            for p in g[v]:
                #print('T',t,'|',v,'<-',p)
                andTerm.append(assigned[p][t])
                andTerm.append(assigned[p][t-1])
            s.add(Or(Not(assigned[v][t]),Or(assigned[v][t-1],And(andTerm))))

    # constraint on number of allocations
    for t in range(1,T+1):
        alloc = []
        for v in vertices:
            alloc.append(assigned[v][t])
        #print(N,alloc)
        alloc.append(N)
        f = AtMost(*alloc)
        s.add(f)

    #force one-shot computation 
    oneShot = True
    firstAlloc = dict()
    if oneShot:
        for v in vertices:
            firstAlloc[v] = [ Bool("falloc_%s_%s" % (v, t)) for t in range(T+1) ]
        for v in vertices:
            s.add(firstAlloc[v][0] == False)
        for t in range(1,T+1):
            for v in vertices:
                s.add(firstAlloc[v][t] == Or(firstAlloc[v][t-1], And(Not(assigned[v][t]), assigned[v][t-1])))
                s.add(Implies(firstAlloc[v][t-1], Not(assigned[v][t])))
    print('Started solving ', datetime.datetime.now())         
    feasible = s.check() 
    model = None
    print('Solver result:',feasible)
    print(s.statistics())
    cycle = None
    if(feasible == sat):
        vertices_ = copy.deepcopy(vertices)
        assigned_ = copy.deepcopy(assigned)
        T_ = T
        m = s.model()
        model = m
        model_ = s.model()
        if verbose: print("Assignment q->v")
        if verbose: print('t   |',end='')
        for v in vertices:
            if verbose: print(" %3d" % v, end="")
        if verbose: print("")
        for t in range(T+1):
            if verbose: print("t%3d|"%(t),end="")
            for v in vertices:
                if verbose: print(' %3d'% ( boolP(m[assigned[v][t]])), end="")
            if verbose: print("",end="\n")
        #if oneShot :
        #    print('First Alloc:')
        #    for t in range(T+1):
        #        if verbose: print("t%3d|"%(t),end="")
        #        for v in vertices:
        #            if verbose: print(' %3d'% ( boolP(m[firstAlloc[v][t]])), end="")
        #        if verbose: print("",end="\n")
        # if verbose: writeSolution() 
        cycle, magic, reset = writeSolution()
    return feasible, model, cycle

def writeSolution(verbose=False):
    solution = dict()
    for t in range(T_+1):
        solution[t] = list()
        for v in vertices_:
            solution[t].append( boolP(model_[assigned_[v][t]]))
    needed_step = list()
    # eliminate steps without any computation
    for t in range(1,T_+1):
        if solution[t-1] != solution[t]:
            needed_step.append(t)
    for v in vertices_:
        if verbose: print(v,' ',end='')
    if verbose: print("")
    stack = list()
    reg = 0 
    alloc = dict()
    for v in range(len(vertices_)):
        alloc[v] = None
    insSeq = list() # type, node, device 
    for i in range(len(needed_step)):
        if verbose: print(solution[t])
        
        if i!= 0:
            for v in range(len(vertices_)):
                if alloc[v]  != None and (solution[needed_step[i]][v] == 0) :
                    insSeq.append(['Reset',vertices_[v], alloc[v]])
                    print(len(insSeq),'Reset',vertices_[v], alloc[v])
                    stack.append(alloc[v])
                    alloc[v] = None
        for v in range(len(vertices_)):
            if (i == 0 or alloc[v] == None) and solution[needed_step[i]][v] == 1:
                if stack != list():
                    allocReg = stack.pop()
                else:
                    reg = reg+1
                    allocReg = reg
                alloc[v] = allocReg 
                insSeq.append(['MAGIC',vertices_[v], alloc[v]])
                print(len(insSeq),'MAGIC',vertices_[v], alloc[v])
    print('----------')
                
    # eliminate redundant resets    
    eliminateComp = list()
    for i in range(len(insSeq)):

        if insSeq[i][0] == 'Reset':
            used = False
            for j in range(i+1, len(insSeq)):
                if insSeq[j][0] == 'MAGIC' and insSeq[j][2] == insSeq[i][2]:
                    used = True
                    break
            if not used:
                eliminateComp.append(i) 
    print(eliminateComp)
    for i in reversed(eliminateComp):
        insSeq.pop(i)
    i = 0
    magicCount = 0
    resetCount = 0 
    old = None
    for ins in insSeq:
        if not (old == 'Reset' and ins[0] == 'Reset'):
            i = i+1
        print('[%3d] %s %4d [Dev %3d]' % (i,ins[0],ins[1],ins[2]))
        old = ins[0]
        if ins[0] == 'MAGIC':
            magicCount = magicCount+1

        elif ins[0] == 'Reset':
            resetCount = resetCount+1

    print("Cycles: %s MAGIC count: %s Reset count: %s, Devices: %s" % (i,magicCount, resetCount,reg))
    logging.info("Cycles: %s MAGIC count: %s Reset count: %s, Devices: %s" % (i,magicCount, resetCount,reg))
    return i,magicCount,resetCount


def minRegAlloc(g,V,out,D=None,T=None,optiType=1,lim=None,logfile=None,verbose=False,timeLimit=None):
    ''' optiType = 1 [minimum devices]
                 = 2 [minimum cycles]
                 = 3 [minimum devices followed by minimum cycles] '''    
    if optiType != 2:
        if D == None:
            print('Error: Number of devices must be specified for min cycles.\n')
            return None,None
    
    if T == None or T <= 0:
        T = 2*V 
    N = V
    
    if logfile != None:
        log = True
    else:
        log = False
    
    count = 0

    logger = logging.getLogger(__name__)
    logging.info('#nodes :%d, #reg :%d, #steps :%d' % (V, N, T)) 
    if N > 1024 : # limit the size of the network
        print('The network is too large (%s nodes)' % (V))
        logging.warning('Network too large (%s nodes)' % (V) )
        return -1,None, None  

    start = time.time() 
    if optiType == 2:
        dev = D
    else:
        dev = V
    feasible,solution,cycles = optiRegAlloc(g, V, out, dev, T, None, verbose, timeLimit)
    end = time.time()
    elapsed = (end - start)
    print("Execution time: %d s " % elapsed)
    logging.info("Execution time: %ds" % elapsed) 
    succReg = None
    succSolution = None

    logging.info('Trivial allocation result (%s reg): %s' % (dev,str(feasible)))
    if feasible != sat:
        print('Trivial allocation failed. Check netlist\n')
        return None,None,None
    else:
        print('Trivial allocation successful.')
        succReg = V
        succT = T
        succSolution = solution 
    timeRemaining = 0
    if optiType == 2:
        bottom = 1
        top = T
        dev = D
    else:
        bottom = 1
        top = N
        
                    
    while top >= bottom:
        mid = int((top+bottom)/2)
        count = count + 1
        if optiType == 2:
            T = mid 
        else:
            dev = mid
            
        logging.info('[Pebble game start] #nodes :%d, #reg :%d, #steps :%d' % (V, dev, T)) 
        limit = timeLimit
        if timeLimit != None:
            timeLimit = limit + timeRemaining
            
            print("Allocated time: %d " % timeLimit)
        start = time.time() 
        feasible,solution,cycles = optiRegAlloc(g, V, out, dev, T, verbose, timeLimit)
        end = time.time()

        elapsed = (end - start)
        logging.info("Execution time: %ds" % elapsed) 
        if timeLimit!= None and elapsed - timeLimit < 0:
            timeRemaining = timeLimit - elapsed
        print("Execution time: %d s " % elapsed)
        # check if number of iterations was exhausted
        logging.info('[Pebble game end] Allocation result (%s reg %s steps): %s' % (dev,T,str(feasible)))
        if lim != None and count >= lim:
            if feasible == sat:
                return dev,cycles,solution
            else:
                return succReg,succCycles,succSolution
        
        if feasible == sat:
            succReg = dev 
            succT = T
            succCycles = cycles
            succSolution = solution
            top = mid-1
        else:
            bottom = mid+1
    if optiType == 3:
        return minRegAlloc(g,V,out,succReg,T,2,lim,logfile,verbose,timeLimit)
    if verbose:
        for v,li in g.items():
            print(v,"<" , end = '')
            for p in li:
                print(p, ' ', end = '')
            print()

    
    return succReg, succCycles, succSolution

if __name__ == '__main__':
    
    ''' Example graph
        1 -> 4
        2 -> 4
        4 -> 5
        3 -> 5
    # define the graph 
    g = dict()
    g[3] = [0,1]
    g[4] = [2,3]
    g[1] = []
    g[0] = []
    g[2] = []

    '''
    ''' Example 2 :
        0 -> 1
        2 -> 4
        3 -> 4
        1 -> 5
        3 -> 5
        4 -> 5
    '''
    g = dict()
    '''
    g[5] = [1,3,4]
    g[4] = [2,3]
    g[1] = [0]
    g[2] = g[3] = g[0] = []'''

    '''Example 3 
      0>4
      1>4
      0>3
      3>5
      0>5
      2>5
    '''

    T = 6 # number of cycles 
    N = 4  # number of registers
    V = 7  #number of vertices in the graph
    out = [6]
    for v in range(V):
        g[v] = []
    g[6] = [4,5]
    g[5] = [2,3,0]
    g[3] = [0]
    g[4] = [0,1]
    optiRegAlloc(g,T,N,V,out,False)
    

