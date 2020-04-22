import os 
import csv 
import json
# singleton for experiment params 
class Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class Solution(metaclass=Singleton):
    """
    Example class.
    """
    __solution = dict()
    
    def addParam(self,key,val):
        self.__solution[key] = val
    
    def appendParam(self, key, val):
        assert key in self.__solution.keys(), 'Paramter {} does not exist in the solution'.format(key)
        assert isinstance( self.__solution[key], list), 'Type ({}) of value of paramter {} is not a list. in the solution'.format(type(self.__solution[key]),(key))
        self.__solution[key].append(val)

    def getSolution(self):
        return self.__solution
    
    def getParam(self,key):
        if key in self.__solution.keys():
            return self.__solution[key]
        else:
            return None 
            
    def initSolution(self):
        self.__solution = dict()

    def writeJsonSolution(self,logfile, checkError=False):
        ''' write the log in json format to file '''
        if checkError:
            if 'error' in self.__solution.keys() and \
                self.__solution['error'] != '':
                self.__solution['finished'] = False 
        
        with open(logfile, 'a+') as f:
            f.write(json.dumps(self.__solution)+'\n')

    def writeSolution(self, outf, overwrite=False):
        if not self.__solution:
            print('Warning: no solution data available to write')
            return 
            
        if not os.path.isfile(outf):
            write_header = True 
        else:
            write_header = False 
            # check if the header is same as the current dict keys  
            with open(outf, 'r') as f:
                d_reader = csv.DictReader(f)

                #get fieldnames from DictReader object and store in list
                headers = d_reader.fieldnames
                if sorted(self.__solution.keys())  != sorted(headers):
                    print('Warning: Write conflict detected in output file.')
                    prefix = outf[:outf.rfind('.')]
                    outf = prefix+'_1.csv'
                    print('Writing to {}'.format(outf))
                    write_header = True 
        if overwrite:
            write_header = True 
            mode = 'w'
        else:
            mode = 'a'
        print('Writing solution to {}'.format(outf))
        with open(outf, mode) as f:
            outk = []
            outv = []
            for k in sorted(self.__solution.keys()):
                outk.append(k)
                outv.append(self.__solution[k])
            v = []
            for val in outk:
                v.append(str(val))
            if write_header:
                f.write(','.join(v))
                f.write('\n')
            v = []
            for val in outv:
                v.append(str(val))
            res = ','.join(v)
            if res == '':
                print('Warning: no solution data available to write')
            else:
                f.write(res)
                f.write('\n')
        



        

        


def main():
    m1 = Solution()
    m2 = Solution()
    assert m1 is m2
    
    m1.addParam('param1','world')
    m2.addParam('param2', 'here')
    print(m2.getSolution())
    m1.writeSolution('hello.csv')

    m2.initSolution()
    print(m1.getSolution())
    m1.writeSolution('hello.csv')
    
    


if __name__ == "__main__":
    main()

# json to csv? via pd

