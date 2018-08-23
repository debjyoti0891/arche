
from __future__ import print_function
from z3 import *
import sys
import itertools


def boolP(s):
    if(s):
        return 1
    else:
        return 0
        
def optiRegAlloc(g,T,N,V,out,verbose=False):
    if N > V:
        print('Reducing number of available registers to number of nodes')
        N = V
    print("Generating Constraints:")
    print("#Nodes: %d, #PO: %d" % (V, len(out)), end="")
    print(" #Devices: %d, #Cycles: %d" % (N,T))
    
    # assignment variables assigned_v_t
    assigned = [[ Bool("assigned_%s_%s" % (v, t)) for t in range(T+1) ] for v in range(V) ]


    s = Solver()
    # all vertices are not assigned at the start
    for v in range(V):
       s.add(assigned[v][0] == False) 

    #final configuration 
    for v in out:
        s.add(assigned[v][T] == True)


    # register allocation 
    for t in range(1,T+1):
        for v in range(V):
            andTerm = []
            
            for p in g[v]:
                #print('T',t,'|',v,'<-',p)
                andTerm.append(assigned[p][t])
                andTerm.append(assigned[p][t-1])
            s.add(Or(Not(assigned[v][t]),Or(assigned[v][t-1],And(andTerm))))

    # constraint on number of allocations
    for t in range(1,T+1):
        alloc = []
        for v in range(V):
            alloc.append(assigned[v][t])
        #print(N,alloc)
        alloc.append(N)
        f = AtMost(*alloc)
        s.add(f)

    
    print('Solver result:',s.check())
    print(s.statistics())
    if(s.check() == sat):
        m = s.model()
        if verbose: print("Assignment q->v")
        if verbose: print('t   |',end='')
        for v in range(V):
            if verbose: print(" %3d" % v, end="")
        if verbose: print("")
        for t in range(T+1):
            if verbose: print("t%3d|"%(t),end="")
            for v in range(V):
                if verbose: print(' %3d'% ( boolP(m[assigned[v][t]])), end="")
            if verbose: print("",end="\n")

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
    

