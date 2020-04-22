def topoOrdering(graph, inputs, verbose = False):
    ''' Performs a topological ordering of the graph 
    
        return topoOrder, vertexLevel

        topoOrder (dict): topoOrder[level] = [v1, v2, ...]
        vertexLevel (dict): vertexLevel[v1] = level
    '''

    vertexLevel = dict()
    processed = set()
    processQ = list()
    bfs = list()
    
    for v in inputs:
        vertexLevel[v] = 0
        processQ.append(v)
        
    while processQ != []:
        v = processQ.pop()
        for s in graph.successors(v):
            present = s in vertexLevel.keys()
            if not present or (present and vertexLevel[s] < vertexLevel[v]+1) :
                vertexLevel[s] = vertexLevel[v] + 1
                processQ.append(s)

    
    topoOrder = dict()
    for v, level in vertexLevel.items():
        if level not in topoOrder.keys():
            topoOrder[level] = []
        topoOrder[level].append(v)
        
    if verbose: 
        for l in range(max(topoOrder.keys())):
            print('level {:5d}:  '.format(l), end='')
            for v in topoOrder[l]:
                print(v, end=' ')
            print('',end='\n')
    return topoOrder, vertexLevel