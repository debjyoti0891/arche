import math
class BitonicSort:

    def __init__(self):
        self.__a = list()
        self.__asc = True;
        self.__compNetwork = list() #i ,j, direction
        self.__debug = False 
    
    def getNetwork(self,n):
        self.sort([-i for i in range(n)])
        print('Created sorting network with {} comparators'.format(\
            len(self.__compNetwork)))
        self.__purge()
        print('Created majority network with {} comparators'.format(\
            len(self.__compNetwork)))
        return self.__compNetwork
    
    def __purge(self):
        N = len(self.__a)
        if N%2 == 0 :
            print('Majority does not exist for even number of inputs')
            return 

        majIndex = int(N/2)-1
        touched = [False for i in range(N)]
        touched[majIndex] = True 
        purgeArr = []
        i = 0
        for comp in reversed(self.__compNetwork):
            if touched[comp[0]] or touched[comp[1]]:
                touched[comp[0]] = True 
                touched[comp[1]] = True 
            else:
                purgeArr.append(N-1-i)
                
            if i % 10 == 0 and (False not in touched):
                break 
            i = i+1 
        print('Purged {}/{} comparators'.format(len(purgeArr),len(self.__compNetwork)))
        purgeArr.sort()
        for i in reversed(purgeArr):
            self.__compNetwork.pop(i)
            
    def sort(self, arr):
        self.__compNetwork = []
        self.__a = arr 
        print('input: {}'.format(self.__a))
        self.bitonicSort(0, len(arr), self.__asc)
        print('sorted: {}'.format(self.__a))
        
    def bitonicSort(self, lo, n, dir, level=1):
        if n > 1:
            #print('bsort {}-{} [{}@ level{}]'.format(lo,n,dir,level))
            m = int(n/2)
            self.bitonicSort(lo,m,not dir,level+1)
            self.bitonicSort(lo+m, n-m, dir,level+1)
            self.bitonicMerge(lo,n,dir,level+1)
    
    def bitonicMerge(self,lo,n,dir,level=1):
        if n > 1:
            #print('bmerge {}-{} [{}@ level{}]'.format(lo,n,dir,level))
            lim = int(math.floor(math.log(n,2)))
            if 2**lim == n:
                m = 2**(lim-1)
            else:
                m = 2**lim 
            for  i in range(lo, lo+n-m):
                if self.__debug: print('comp {}--{} {}'.format(i,i+m,dir))
                self.__compNetwork.append([i,i+m,dir])
                self.compare(i, i+m, dir)
            self.bitonicMerge(lo, m, dir,level+1)
            self.bitonicMerge(lo+m, n-m, dir,level+1)
            
    def compare(self,i,j,dir):
        if (dir == (self.__a[i] > self.__a[j])):
            self.exchange(i,j)
    
    def exchange(self,i,j):
        self.__a[i],self.__a[j] = self.__a[j],self.__a[i]
            
        
if __name__ == '__main__':
    bs = BitonicSort()
    bs.sort([1,5,2,3,4])
    
    
    with open('majres.csv','w') as f:
        for i in range(5,1002,2):
            net = bs.getNetwork(i)
            f.write(str(i)+','+str(len(net))+'\n')
            
    #print(net)