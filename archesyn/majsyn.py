import datetime
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
        if self.__debug:print('-------')
        for c in self.__compNetwork:
            if self.__debug:print('{}--{} {}'.format(c[0],c[1],c[2]))
        if self.__debug:print('---**---')


        self.__purge()
        print('Created majority network with {} comparators'.format(\
            len(self.__compNetwork)))

        if self.__debug:print('-------')
        for c in self.__compNetwork:
            if self.__debug:print('{}--{} {}'.format(c[0],c[1],c[2]))
        if self.__debug:print('----**---')
        return self.__compNetwork

    def writeNetwork(self,outfile):

        N = len(self.__a)
        compN = len(self.__compNetwork)
        output = 'majority'
        outf = open(outfile,'w')
        # header
        outf.write('//Benchmark written by "arche" on {}\n'.format(datetime.datetime.now()))
        outf.write('// Majority-{} constructed with {} Majority-3 nodes\n'.format(N, len(self.__compNetwork)*2))
        outf.write('module maj{} (\n'.format(N))
        for i in range(N):
            outf.write('v{} , '.format(i))
        outf.write(output+' );\n')

        outf.write('input ')
        for i in range(N-1):
            outf.write('v{} , '.format(i))
        outf.write('v{} ;\n'.format(N-1))

        outf.write('output majority;\n')

        outf.write('wire ')
        s = ''
        for i in range(compN*2-2):
            s = s + 'cm{} , '.format(i)
        outf.write(s[:-2]+' ;\n\n')

        # network
        varTrack = ['v{}'.format(i) for i in range(N)]
        c = 0
        for comp in self.__compNetwork[:-1]:
            print(comp)
            in1 = comp[0]
            in2 = comp[1]

            inp1 = varTrack[in1]
            inp2 = varTrack[in2]

            out1 = 'cm{}'.format(c)
            c = c+1
            out2 = 'cm{}'.format(c)
            c = c+1
            assert(c < 2*compN-1)

            if comp[2]: # ASCENDING 
                outf.write('assign {} = {} & {};\n'.format(out1,inp1,inp2))
                outf.write('assign {} = {} | {};\n'.format(out2,inp1,inp2))
            else:
                outf.write('assign {} = {} & {};\n'.format(out2,inp1,inp2))
                outf.write('assign {} = {} | {};\n'.format(out1,inp1,inp2))
                
            varTrack[in1] = out1
            varTrack[in2] = out2 

        print(self.__compNetwork[-1])
        comp = self.__compNetwork[-1]
        inp0 = varTrack[comp[0]]
        inp1 = varTrack[comp[1]]

        majIndex = int(N/2)
        if (comp[0] == majIndex and comp[2] == True) \
            or (comp[1] == majIndex and comp[2] == False): #this is the input 
            outf.write('assign majority = {} & {} ;\n'.format(inp0,inp1))
        else:    
            outf.write('assign majority = {} | {} ;\n'.format(inp0,inp1))
        

        # tail
        outf.write('endmodule')
        outf.close()


    def __purge(self):
        N = len(self.__a)
        if N%2 == 0 :
            print('Majority does not exist for even number of inputs')
            return 

        majIndex = int(N/2)
        touched = [False for i in range(N)]
        touched[majIndex] = True 
        purgeArr = []
        i = 0
        for comp in reversed(self.__compNetwork):
            if self.__debug: print('i:{} {} touched:{}'.format(i,comp,touched))
            if touched[comp[0]] or touched[comp[1]]:
                touched[comp[0]] = True 
                touched[comp[1]] = True 
            else:
                print('purging {} -> {}'.format(i, len(self.__compNetwork)-1-i))
                purgeArr.append(len(self.__compNetwork)-1-i)
                
            if i % 10 == 0 and (False not in touched):
                break 
            i = i+1 


        print('Purged {}/{} comparators'.format(len(purgeArr),len(self.__compNetwork)))
        purgeArr.sort()
        #print('purge arr:',purgeArr)
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
        for i in range(5,10,4):
            net = bs.getNetwork(i)
            bs.writeNetwork('maj{}.v'.format(i))
            f.write(str(i)+','+str(len(net))+'\n')
            
    #print(net)