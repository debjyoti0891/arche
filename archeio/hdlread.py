from igraph import *
import sys

def read_mappedverilog(fname, debug = False):
    ''' the method reads a mapped verilog generated using abc 
        and maps it to a igraph data structure ''' 
    f = open(fname)
    gateTypes = ['inv1', 'nor2', 'nor3', 'nor4']
    directAssign = ['one', 'buf']
    variables = set()
    gates = []
    ckt_inputs = []
    ckt_outputs = []
    oneOut = list() 
    zeroOut = list()
    directOut = dict() 
    trivialOut = set()
    f = open(fname)
    while True:

        l = f.readline() 
        if l == '':
            break
        if debug : print(l)
        l = l.strip()
        if l.find('//') >= 0:
            l = l[l.find('//')+2:]
            if l == '':
                continue 
        w = l[: l.find(' ')]

        if w in gateTypes:
            g = gateTypes.index(w)
            if debug : print(l)
            l = l[l.find('(')+1: l.rfind(')')] 
            l = l.split(',')
            inputs = []
            for gatevar in l:
                gatevar = gatevar.strip()
                v =  gatevar[gatevar.find('(')+1: gatevar.rfind(')')]
                variables.add(v.strip())

                inputs.append(v.strip())
            #print(inputs)
            gates.append([g,inputs])
        elif w in directAssign:
            if w == 'one' or  w == 'zero':
                inp = l[l.find(' ')+1: l.find('(')]
                out = l[l.rfind('(')+1 : l.find(')')]
                if w == 'one':
                    oneOut.append(out) 
                else:
                    zeroOut.append(out) 

                if debug : print(inp,out)
                trivialOut.add(out)
            elif w == 'buf':
                l = l[l.find('.a')+2:]
                pi = l[l.find('(')+1: l.find(')')]
                l = l[l.find('.O')+2:]
                po = l[l.find('(')+1: l.find(')')]
                if debug : print(pi,po)
                directOut[po] = pi 
        elif w == 'input':
            l = l[l.find(' ')+1:]
            while True:
                l = l.strip()
                if l[-1] == ';' or l[-1] == ',':
                    v = l[:-1]
                else:
                    v = l
                v = v.split(',') 
                if debug : print(v)
                for pi in v:
                    ckt_inputs.append(pi.strip())
                
                if l.rfind(';') >= 0:
                    break 
                l = f.readline() 
                if l == '':
                    print('invalid output statement')
                    break 

        elif w == 'output':
            l = l[l.find(' ')+1:]
            while True:
                l = l.strip()
                if l[-1] == ';' or l[-1] == ',':
                    v = l[:-1]
                else:
                    v = l
                v = v.split(',') 
                if debug : print(v)
                for po in v:
                    ckt_outputs.append(po.strip())
                
                if l.rfind(';') >= 0:
                    break 
                l = f.readline() 
                if l == '':
                    if debug : print('invalid output statement')
                    break 
            '''
            l = l[l.find(' ')+1:l.rfind(';')]
            l = l.split(',')
            l = [v.strip() for v in l]
            ckt_outputs = ckt_outputs + l
            '''
    #print(ckt_inputs)
    #print(ckt_outputs)
    ''' assign gates numbering '''
    gateMap = dict()
    i = 0
    varList = list(variables)
    varList.sort() 
    for v in varList:
        gateMap[v] = i
        i = i+1
    pout = list(directOut.keys())
    pout.sort()
    for po in pout:
        pi = directOut[po]
        if po not in gateMap.keys():
            gateMap[po] = i
            i = i+1
        if pi not in gateMap.keys():
            gateMap[pi] = i
            i = i+1
    if debug : print(type(zeroOut))
    zeroOut.sort()
    for po in zeroOut:
        if po not in gateMap.keys():
            gateMap[po] = i
            i = i+1
    oneOut.sort()
    for po in oneOut:
        if po not in gateMap.keys():
            gateMap[po] = i
            i = i+1
    for k in gateMap.keys():
        print('gatemapkey:',k)
    d = True
    ckt_outputs = set(ckt_outputs)
    actual_out = list(ckt_outputs.difference(trivialOut))
    actual_out.sort()
    if debug : print('Circuit output:',ckt_outputs, actual_out) 
    ''' populate graph '''
    g = Graph(directed=True)
    g.add_vertices(i)
    g['pi'] = ckt_inputs 
    g['po'] = actual_out 
    g['zeroOut'] = zeroOut 
    g['oneOut'] = oneOut

    for inp in gates:
        
        out = gateMap[inp[1][-1]]
        for i in range(len(inp[1])-1):
            if debug: print(inp[1][-1], out, '<-',inp[1][i], gateMap[inp[1][i]])
            v = gateMap[inp[1][i]]
            g.add_edges([(v,out)])
        g.vs[out]['gateType'] = gateTypes[inp[0]]
    if debug: print('direct maps:')
    for po,pi in directOut.items():
        gateOut = gateMap[po]
        gateIn = gateMap[pi] 
        g.add_edges([(gateOut, gateIn)]) 
        g.vs[gateOut]['gateType'] = 'buf' 
    #g.write_gml('test.gml')
    #layout = g.layout("kamada_kawai")
    #plot(g, layout = layout)
    g['vToIndex'] = gateMap
    return g

if __name__ == "__main__":
    fname = sys.argv[1]
    read_mappedverilog(fname);

