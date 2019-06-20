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
    
    def getSolution(self):
        return self.__solution
    
    def getParam(self,key):
        if key in self.__solution.keys():
            return self.__solution[key]
        else:
            return None 
            
    def startSol(self):
        self.__solution = dict()


def main():
    m1 = Solution()
    m2 = Solution()
    assert m1 is m2
    
    m1.addParam('hello','world')
    m2.addParam('was', 'here')
    print(m2.getSolution())
    m2.startSol()
    print(m1.getSolution())
    


if __name__ == "__main__":
    main()
