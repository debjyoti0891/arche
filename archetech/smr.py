
from __future__ import print_function
from z3 import *
import sys
import itertools
import math

def boolP(s):
    if(s):
        return 1
    else:
        return 0
        
def optiRegAlloc(g,V,out,N,T,verbose=False):
    if N > V:
        print('Reducing number of available registers to number of nodes')
        N = V
    print("Generating Constraints:")
    print("#Nodes: %d, #PO: %d" % (V, len(out)), end="")
    print(" #Devices: %d, #Cycles: %d" % (N,T))
    
       # remove nodes that are leaves/pi
    piPurge = True
    if piPurge:
        purge = set()
        for node,predList in g.items():
            if predList == list():
                purge.add(node)
        for node in purge:
            g.pop(node,None)
        for node in g.keys():
            predSet = set(g[node])
            g[node] = list(predSet-purge)
    vertices = list(g.keys())
    # assignment variables assigned_v_t
    assigned = dict()
    for v in vertices:
        assigned[v] = [ Bool("assigned_%s_%s" % (v, t)) for t in range(T+1) ] 



    s = Solver()
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
        
    feasible = s.check() 
    model = None
    print('Solver result:',feasible)
    print(s.statistics())
    if(feasible == sat):
        m = s.model()
        model = m
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
        if oneShot :
            print('First Alloc:')
            for t in range(T+1):
                if verbose: print("t%3d|"%(t),end="")
                for v in vertices:
                    if verbose: print(' %3d'% ( boolP(m[firstAlloc[v][t]])), end="")
                if verbose: print("",end="\n")
 
    return feasible, model

def minRegAlloc(g,V,out,T=None,lim=None,verbose=False):
    if T == None or T <= 0:
        T = int(V*math.log(V))
    N = V

    count = 0
    bottom = 1
    top = N
    feasible,solution = optiRegAlloc(g, V, out, top, T, verbose)
    succReg = None
    succSolution = None
    if feasible != sat:
        print('Trivial allocation failed. Check netlist\n')
        return None,None
    else:
        print('Trivial allocation successful.')
        succReg = N
        succSolution = solution 
    while top >= bottom:
        mid = int((top+bottom)/2)
        count = count + 1
  
        feasible,solution = optiRegAlloc(g, V, out, mid, T, verbose)
        # check if number of iterations was exhausted
        if lim != None and count >= lim:
            if feasible == sat:
                return mid,solution
            else:
                return succReg,succSolution
        
        if feasible == sat:
            succReg = mid 
            succSolution = solution
            top = mid-1
        else:
            bottom = mid+1
    for v,li in g.items():
        print(v,"<" , end = '')
        for p in li:
            print(p, ' ', end = '')
        print()


    return succReg, succSolution

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
    

