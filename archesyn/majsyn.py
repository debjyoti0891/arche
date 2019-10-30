import math
class BitonicSort:

    def __init__(self):
        self.__a = list()
        self.__asc = True;
        self.__compNetwork = list() #i ,j, direction
    
    
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
                print('comp {}--{} {}'.format(i,i+m,dir))
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