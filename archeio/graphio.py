

def getPredList(g):
    predG = dict()
    for v in g.vs():
        v = v.index
        predG[v] = list()
        for e in g.es.select(_target_in = [v]):
            s = e.source
            predG[v].append(s)
    return predG

def getOutputs(g):
    outputs = []
    for out in g['po']:                                                    
        outputs.append(g['vToIndex'][out])
    return outputs

