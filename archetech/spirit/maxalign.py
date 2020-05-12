import collections 
import datetime
from z3 import *
import sys 
import os 


def splitList(vList):
    problems = [[]]

    if len(vList) <= 1:
        return [vList]
    
    problems[0].append(vList[0])
    for val in vList[1:]:
        valset = set(val)
        selected = False
        for i in range(len(problems)):
            problem = problems[i]
             
            for pval in problem:
               pvalset = set(pval)
               if pvalset.intersection(valset) != set():
                    problems[i].append(val)
                    selected = True 
                    break
            if selected:
                break
        if not selected:
            problems.append([val]) 
    return problems 

def maxAlignHeuristic(vList, ignore='-', debug=False):
    # 
    # sort the keys with number of occurances
    # and place them aligned 
    for val in vList:
        if debug: print(val)

    key_dict = collections.defaultdict(int)
    key_loc_dict = dict()
    # check if all the items have the same length
    for i in range(len(vList)):

        len_ignore = vList.count(ignore)
        if len_ignore > 0:
            len_set = 1
        else:
            len_set = 0
        if len(vList[i]) - len_ignore != len(set(vList[i])) - len_set:
            print('Elements should be unique in the list ')
            print(vList)
            return False, None 

        
        for j in vList[i]:
            if j is not ignore:
                key_dict[j] += 1
                if j not in key_loc_dict.keys():
                    key_loc_dict[j] = [i]
                else:
                    key_loc_dict[j].append(i)
    
    # sort the keydict 
    ordered_keys = sorted(key_dict, key=key_dict.get, reverse=True)

    # output matrix 
    locs = len(vList)
    list_len = len(vList[0])
    aligned_out = [[ignore for i in range(list_len)] for j in range(locs)]

    if debug: print(key_loc_dict, key_dict)
    if debug: print(ordered_keys)

    for k in ordered_keys:
        free_loc = dict()

        for i in range(list_len):
            aligned = True 
            for loc in key_loc_dict[k]:
                if aligned_out[loc][i] is not ignore:
                    aligned = False 
                    continue 
                
                free_loc[loc] = i 
            if aligned:
                for loc in key_loc_dict[k]:
                    aligned_out[loc][i] = k 
                break 
        
        if not aligned:
            for loc in key_loc_dict[k]:
                aligned_out[loc][free_loc[loc]] = k
    
    for val in aligned_out:
        if debug: print(val)
    # assert validity 
    for i in range(len(aligned_out)):
        #print('{} {} {}'.format(set(aligned_out[i]), set(vList[i]), set(aligned_out[i]) == set(vList[i])))
        assert set(aligned_out[i]) == set(vList[i]), '{} {}'.format(vList[i], aligned_out[i])

    return True, aligned_out
     



             


def maxAlign(vList, debug = False):

    elements = set() 
    # check if all the items have the same length
    for i in range(len(vList)-1):
        if len(vList[i]) != len(vList[i+1]):
            print('List items {} and {} must have the same length'.format(i,i+1))
            return None 
        
        for j in vList[i]:
            elements.add(j)
    
    for j in vList[-1]:
        elements.add(j)
    eToVarMap = dict()
    elements = list(elements)
    i = 0
    for e in elements:
        eToVarMap[e] = i
        i = i+1 

    problems = splitList(vList)
    print('problems: {} '.format(problems))
    rows = len(vList)
    bins = len(vList[0])
    print('Number of unique elements: {}'.format(len(elements)))
    print('Number of bins: {}'.format(bins))
    print('Solving SAT : {}'.format(datetime.datetime.now()))

    # Each bucket must have on item 

    buckets = [[Int("assigned_%s_%s" % (r, b)) for b in range(bins)] for r in range(rows)]

    s = Optimize() #
    #s = Then('simplify','smt').solver()
    # constraints on assignent 
    for r in range(rows):
        
        for b in range(bins):
            orList = []
            for val in vList[r]:
                orList.append(buckets[r][b] == eToVarMap[val]) # only available elements can be assigned
            #print(orList)
            s.add(Or(orList))
        s.add(Distinct(buckets[r])) # each row cannot have duplicates 
        
    # check the number of aligned values 
    aligned = []
    for b in range(bins):

        for r1 in range(rows):
            for r2 in range(r1+1,rows):
                aligned.append(Int('a_%s_%s_%s' % (r1,r2,b)))
                s.add(aligned[-1] == If((buckets[r1][b] == buckets[r2][b]),0,1))
    
    cost = Int('cost')
    s.add(cost == Sum(aligned))
    h = s.minimize(cost)
    s.set('timeout', 60000 )
    feasible = s.check()
    s.lower(h)
    print('Completed solving SAT : {}'.format(datetime.datetime.now()))
    if debug: print(feasible)
    result = None 
    if(feasible == sat):
        model =  s.model()
        if debug: print('-----')
        result = []
        for r in range(rows):
            result.append([])
            for b in range(bins):
                if debug: print('{} '.format(model[buckets[r][b]]), end = '')
                result[-1].append(elements[model[buckets[r][b]].as_long()])
            if debug:  print(' ', end='\n')


        for var in aligned:
            if debug: print('aligned:',var,model[var])

        if debug: print('Cost: {}'.format(model[cost]))
    if feasible != sat:
        result = vList 
    return True, result
    






if __name__ == '__main__':
    #v = [[1,2,3,4], [1,3,4,5], [3,4,2,6], [4,3,6,1]]
    #v = [['a', 'b', 'c', 'd'], ['x', 'a', 'b', 'y'], ['a','e','x','y']]
    # v = ['abcde','xabce', 'bcdea','fghst','fdswe','fxyed','lkjhg','jhgfd']
    # succ,res = maxAlign(v)
    # print('Succ:{} :{}'.format(succ,res))

    # v = [['a', 'b', 'c', 'd'], ['x', 'a', 'b', 'y'], ['m','n','o','p'], ['m', 'q','r','s']]
    # v.sort()

    # succ,res = maxAlign(v)
    # print('Succ:{} :{}'.format(succ,res))

    v = [['a', 'b', 'c', 'd'], ['x', 'a', 'b', '-'], ['-','n','a','p'], ['x', 'd','-','b']]
    maxAlignHeuristic(v, '-', False)
