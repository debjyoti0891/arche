import json
class SHA3ins:

    def __init__(self,prefix=''):
        self.nothing = 0
        self.prefix = prefix

    def Rotate(self, c, fp):

        t = 63-c
        for i in range(0, 64):
            if t < 0:
                t+=64
            fp.write("1 %d " % t)
            t -= 1
        fp.write("\n\n")

    def Load(self, fp, cyc):

        """
        Loads the initial SHA-3 states into the SHA-3 state logical compartment of the DCM 
        """

        fp.write("// Loads the initial SHA-3 states into the SHA-3 State logical compartment of the DCM\n\n\n")

        for j in range(0, 25):

            fp.write("Apply 25 0 01 000000 ")
            cyc += 1
            self.Rotate(0, fp)

            fp.write("\nRead 25\n\n")
            cyc += 1

            fp.write("Apply %d 1 01 000000 "% j)
            cyc += 1
            self.Rotate(0, fp)
    
            #Stores state j in non inverted form

            fp.write("Apply 25 0 00 000000 ") #Resetting wl 25
            cyc += 1
            self.Rotate(0, fp)

        return cyc

    def Theta(self, fp, cyc):

        """
        Implements Theta step of SHA3
        """

        # ---- 5 times 5-input XOR ----- #

        for i in range(0, 5):

            fp.write("Read %d\n\n"% i)    # Read A[i, 0]
            cyc += 1

            fp.write("Apply 26 1 01 000000 ")
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read 26\n\n")
            cyc += 1

            fp.write("Apply 29 1 01 000000 ")
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 30 1 01 000000 ")
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 31 1 01 000000 ")
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read %d\n\n"% (i+5))    # Read A[i, 1]
            cyc += 1

            fp.write("Apply 29 1 01 000000 ")    #a + ~b
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 30 1 00 000000 ")    #a.~b    
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 31 1 00 000000 ")    #a.~b
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read 29\n\n")
            cyc += 1

            fp.write("Apply 30 1 01 000000 ")    #a XOR b    
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 31 1 01 000000 ")    #a XOR b    
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read %d\n\n"% (i+10))    # Read A[i, 2]
            cyc += 1

            fp.write("Apply 25 1 01 000000 ")    
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read 25\n\n")
            cyc += 1

            fp.write("Apply 27 1 01 000000 ")    
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 28 1 01 000000 ")    
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read %d\n\n"% (i+15))    # Read A[i, 3]
            cyc += 1

            fp.write("Apply 27 1 01 000000 ")    #c + ~d    
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 28 1 00 000000 ")    #c.~d    
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read 27\n\n")
            cyc += 1

            fp.write("Apply 28 1 01 000000 ")    #c XOR d    
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read 28\n\n")
            cyc += 1

            fp.write("Apply 31 1 00 000000 ")    #(aXORb).~(cXORd)    
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 30 1 01 000000 ")    #(aXORb) + ~(cXORd)    
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read 30\n\n")
            cyc += 1

            fp.write("Apply 31 1 01 000000 ")    #(aXORb)XOR(cXORd)    
            cyc += 1
            self.Rotate(0, fp)

            for l in range(25, 31):    #Resetting wl 25 to 30
                fp.write("Apply %d 0 00 000000 "% l)
                cyc += 1
                self.Rotate(0, fp)

            fp.write("Read 31\n\n")
            cyc += 1

            fp.write("Apply 27 1 01 000000 ")
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read 27\n\n")
            cyc += 1

            fp.write("Apply 30 1 01 000000 ")
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read %d\n\n"% (i+20))    # Read A[i, 4]
            cyc += 1

            fp.write("Apply 31 1 00 000000 ")    #(aXORbXORcXORd).~e
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 30 1 01 000000 ")    #(aXORbXORcXORd)+~e
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read 30\n\n")
            cyc += 1

            fp.write("Apply 31 1 01 000000 ")    #(aXORbXORcXORd)XOR~e
            cyc += 1
            self.Rotate(0, fp)

            # One 5 input XOR calculated and stored in wl 31. This is copied to UX and Computation memory is reset
            fp.write("Apply %d 0 00 000000 "% (32+2*i))    #Reset UX
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read 31\n\n")
            cyc += 1

            fp.write("Apply %d 1 01 000000 "% (32+2*i))    #Reset UX
            cyc += 1
            self.Rotate(0, fp)

            #Reset Computation Memory
            fp.write("Apply 27 0 00 000000 ")
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 30 0 00 000000 ")
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 31 0 00 000000 ")
            cyc += 1
            self.Rotate(0, fp)

        # Shifting of ri to generate si and calculation of mi

        for i in range(0, 5):

            fp.write("Read %d\n\n"% (32+2*((i+1)%5)))
            cyc += 1

            fp.write("Apply 25 1 01 00000 ")    #Shifted copy from UX to Computation Memory
            cyc += 1
            self.Rotate(1, fp)

            fp.write("Read %d\n\n"% (32+2*((i+4)%5)))
            cyc += 1

            fp.write("Apply 28 1 01 00000 ")
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 29 1 01 00000 ")    #Direct copy from UX to computation memory
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read 25\n\n")
            cyc += 1

            fp.write("Apply 28 1 01 00000 ")    #ri+1 + ~ si
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 29 1 00 00000 ")    #ri+1.~ si
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read 28\n\n")
            cyc += 1

            fp.write("Apply 29 1 01 00000 ")    #ri+1 XOR si
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply %d 0 00 00000 "% (33+2*i))    #Reset UX
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Read 29\n\n")
            cyc += 1

            fp.write("Apply %d 1 01 00000 "% (33+2*i))    #Copy result to UX in inverted form
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 25 0 00 00000 ")    
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 28 0 00 00000 ")    
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply 29 0 00 00000 ")    
            cyc += 1
            self.Rotate(0, fp)

        # ----- Updation of Words ------ #

        # The following code updates each word in the SHA-3 state

        for i in range(0, 5):

            for j in range(0, 25, 5):

                a = j+i

                # ----- XNOR ----- #

                fp.write("Read %d\n\n"% (33+2*i))
                cyc += 1

                fp.write("Apply 25 1 01 000000 ")    #Copy mj
                cyc += 1
                self.Rotate(0, fp)

                fp.write("Read 25\n\n")
                cyc += 1

                fp.write("Apply 28 1 01 000000 ")    #Copy ~mj
                cyc += 1
                self.Rotate(0, fp)

                fp.write("Apply 29 1 01 000000 ")    #Copy ~mj
                cyc += 1
                self.Rotate(0, fp)

                fp.write("Read %d\n\n"% a)
                cyc += 1

                fp.write("Apply 29 1 00 000000 ")    #Copy ~mj.~wi
                cyc += 1
                self.Rotate(0, fp)

                fp.write("Apply 28 1 01 000000 ")    #Copy ~mj+~wi
                cyc += 1
                self.Rotate(0, fp)

                fp.write("Read 28\n\n")
                cyc += 1

                fp.write("Apply 29 1 01 000000 ")    #Copy mjXNORwi
                cyc += 1
                self.Rotate(0, fp)

                # Reset current SHA-3 State word

                fp.write("Apply %d 0 00 000000 "% a)
                cyc += 1
                self.Rotate(0, fp)

                # Copy new state to SHA-3 memory partition

                fp.write("Read 29\n\n")
                cyc += 1

                fp.write("Apply %d 1 01 000000 "% a)    #mjXORwi
                cyc += 1
                self.Rotate(0, fp)

                # Reset computation memory

                fp.write("Apply 25 0 00 00000 ")    
                cyc += 1
                self.Rotate(0, fp)

                fp.write("Apply 28 0 00 00000 ")    
                cyc += 1
                self.Rotate(0, fp)

                fp.write("Apply 29 0 00 00000 ")    
                cyc += 1
                self.Rotate(0, fp)

        return cyc

    def RhoPi(self, fp, cyc):

        rot_c = [1,  3,  6,  10, 15, 21, 28, 36, 45, 55, 2,  14,
        27, 41, 56, 8,  25, 43, 62, 18, 39, 61, 20, 44]
        keccak_piln = [10, 7,  11, 17, 18, 3, 5,  16, 8,  21, 24, 4,
        15, 23, 19, 13, 12, 2, 20, 14, 22, 9,  6,  1]

        i = 0
        j = 0
        loc = 0
        c = 0

        """
        The following code implements Rho and Pi stages
        """

        a = 1
    
        fp.write("Read %d\n\n"% a)
        cyc += 1

        fp.write("Apply %d 1 01 000000 "% (25+loc))
        cyc += 1
        self.Rotate(0, fp)

        loc = (loc+1)%2

        while i < 24:
    
            j = keccak_piln[i]

            fp.write("Read %d\n\n"% j)
            cyc += 1

            fp.write("Apply %d 0 00 000000 "% (25+loc))    #Resets Computation memory
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply %d 1 01 000000 "% (25+loc))
            cyc += 1
            self.Rotate(0, fp)

            loc = (loc+1)%2

            fp.write("Read %d\n\n"% (25+loc))
            cyc += 1

            fp.write("Apply %d 0 00 000000 "% j)    #Resets SHA-3 state location where shifted word is to be copied
            cyc += 1
            self.Rotate(0, fp)

            fp.write("Apply %d 1 01 000000 "% j)    #Copies shifted word
            cyc += 1
            self.Rotate(rot_c[i], fp)

            i += 1

        fp.write("Apply 25 0 00 000000 ")
        cyc += 1
        self.Rotate(0, fp)

        fp.write("Apply 26 0 00 000000 ")
        cyc += 1
        self.Rotate(0, fp)

        return cyc

    def Chi(self, fp, cyc):

        """
        The following code implements Chi stage
        """

        for i in range(0, 5):

            # ---- Reset UX Partition ---- #

            for k in range(32, 42):
                fp.write("Apply %d 0 00 000000 "% k)
                cyc += 1
                self.Rotate(0, fp)

            # ---- Copy SHA-3 states to CM and UX ---- #

            for j in range(0, 5):
    
                fp.write("Read %d\n\n"% (5*i+j))
                cyc += 1

                fp.write("Apply %d 1 01 000000 "% (32+2*j))
                cyc += 1
                self.Rotate(0, fp)

                fp.write("Apply %d 1 01 000000 "% (33+2*j))
                cyc += 1
                self.Rotate(0, fp)

                fp.write("Apply %d 1 01 000000 "% (25+j))
                cyc += 1
                self.Rotate(0, fp)

            # ---- Compute ~wj.wk ---- #

            for j in range(0, 5):

                fp.write("Read %d\n\n"% (32+2*((j+2)%5)))
                cyc += 1

                fp.write("Apply %d 1 00 000000 "% (25 + (j+1)%5))
                cyc += 1
                self.Rotate(0, fp)

            # ---- Compute XNOR in UX ---- #

            for j in range(0, 5):

                fp.write("Read %d\n\n"% (25 + (j+1)%5))
                cyc += 1

                fp.write("Apply %d 1 01 000000 "% (32+2*j)) #~wi+~(~wk.wk)
                cyc += 1
                self.Rotate(0, fp)

                fp.write("Apply %d 1 00 000000 "% (33+2*j)) #~wi.~(~wk.wk)
                cyc += 1
                self.Rotate(0, fp)

                fp.write("Read %d\n\n"% (32+2*j))
                cyc += 1

                fp.write("Apply %d 1 01 000000 "% (33+2*j)) #XNOR computation
                cyc += 1
                self.Rotate(0, fp)

            # ---- Reset SHA-3 copy Ui ---- #

            for j in range(0, 5):

                fp.write("Apply %d 0 00 000000 "% (5*i+j)) 
                cyc += 1
                self.Rotate(0, fp)

                fp.write("Read %d\n\n"% (33+2*j))
                cyc += 1

                fp.write("Apply %d 1 01 000000 "% (5*i+j)) 
                cyc += 1
                self.Rotate(0, fp)

            # ---- Reset Computation Memory ---- #

            for j in range(0, 5):

                fp.write("Apply %d 0 00 000000 "% (25+j)) 
                cyc += 1
                self.Rotate(0, fp)


        return cyc

    def Iota(self, fp, cyc):

        """
        The following code implements Iota stage
        """

        fp.write("Read 0\n\n")
        cyc += 1

        fp.write("Apply 28 1 01 000000 ")
        cyc += 1
        self.Rotate(0, fp)

        fp.write("Apply 29 1 01 000000 ")
        cyc += 1
        self.Rotate(0, fp)

        fp.write("Apply 28 0 01 000000 ")
        cyc += 1
        self.Rotate(0, fp)

        fp.write("Apply 29 0 00 000000 ")
        cyc += 1
        self.Rotate(0, fp)

        fp.write("Read 28\n\n")
        cyc += 1

        fp.write("Apply 29 1 01 000000 ")
        cyc += 1
        self.Rotate(0, fp)

        fp.write("Read 29\n\n")
        cyc += 1

        fp.write("Apply 0 0 00 000000 ")
        cyc += 1
        self.Rotate(0, fp)

        fp.write("Apply 0 1 01 000000 ")
        cyc += 1
        self.Rotate(0, fp)

        fp.write("Apply 28 0 00 000000 ")
        cyc += 1
        self.Rotate(0, fp)

        fp.write("Apply 29 0 00 000000 ")
        cyc += 1
        self.Rotate(0, fp)

        return cyc

    def Keccak(self):

        cyc = 0

        fp = open(self.prefix+"Keccak-f1600.ins", "w+")

        cyc = self.Load(fp, cyc)

        for i in range(0, 24):

            cyc = self.Theta(fp, cyc)
            cyc = self.RhoPi(fp, cyc)
            cyc = self.Chi(fp, cyc)
            cyc = self.Iota(fp, cyc)

        return cyc

        fp.close()
        
    def genConfig(self):
        if '/' in self.prefix:
            prefix = self.prefix[self.prefix.rfind('/')+1:]
        else:
            prefix = self.prefix
        
        config = dict()
        config['dim'] = {'m':42, 'n':64}
        config['filename'] = {'input':prefix+"Keccak-f1600.inp",\
                'ins_mem':prefix+'Keccak-f1600.ins',\
                'output': prefix+'Keccak-f1600'}
        config['simulation'] = {'cycles': 0,  'print_ins': 1, 'verbose': 0}
        with open(self.prefix+'config.json','w') as outfile:
            json.dump(config, outfile,indent=4)
        
    
    


class SHA3inp:

    def __init__(self,prefix=''):
        self.nothing = 0
        self.prefix = prefix

    def stringToBinary(self, s):
        
        if (len(s) <= 0):
            return 0
        binary = []
        #binary.append('\0')
        for i in range(len(s)):
            ch = s[i]
            for j in range(7, -1, -1):
                if (ord(ch) & (1 << j)):
                    binary.append('1')
                else:
                    binary.append('0')
        return binary

    def sponge(self, binaryinp, b):

        if (len(binaryinp) <= 0):
            return 0

        binary = []
        binary = binaryinp[:]
        #print(binary)

        length = len(binary)
        bytes = int(length/8)

        s = []

        for i in range(0, bytes):
            for j in range(0, 4):
                t = binary[8*i+j]
                binary[8*i+j] = binary[8*(i+1)-j-1]
                binary[8*(i+1)-j-1] = t

        #print(binary)

        for i in range(0, b):            
            if i < length:
                s.append(binary[i])

            elif i == length:
                s.append('0')
            elif i == length+1:
                s.append('1')
            elif i == length+2:
                s.append('1')
            elif i == b-1:
                s.append('1')
            else:
                s.append('0')

        return s

    def genInp(self,inputstr=None):

        RC = ["0000000000000000000000000000000000000000000000000000000000000001",
                        "0000000000000000000000000000000000000000000000001000000010000010",
                        "1000000000000000000000000000000000000000000000001000000010001010",
                        "1000000000000000000000000000000010000000000000001000000000000000",
                        "0000000000000000000000000000000000000000000000001000000010001011",
                        "0000000000000000000000000000000010000000000000000000000000000001",
                        "1000000000000000000000000000000010000000000000001000000010000001",
                        "1000000000000000000000000000000000000000000000001000000000001001",
                        "0000000000000000000000000000000000000000000000000000000010001010",
                        "0000000000000000000000000000000000000000000000000000000010001000",
                        "0000000000000000000000000000000010000000000000001000000000001001",
                        "0000000000000000000000000000000010000000000000000000000000001010",
                        "0000000000000000000000000000000010000000000000001000000010001011",
                        "1000000000000000000000000000000000000000000000000000000010001011",
                        "1000000000000000000000000000000000000000000000001000000010001001",
                        "1000000000000000000000000000000000000000000000001000000000000011",
                        "1000000000000000000000000000000000000000000000001000000000000010",
                        "1000000000000000000000000000000000000000000000000000000010000000",
                        "0000000000000000000000000000000000000000000000001000000000001010",
                        "1000000000000000000000000000000010000000000000000000000000001010",
                        "1000000000000000000000000000000010000000000000001000000010000001",
                        "1000000000000000000000000000000000000000000000001000000010000000",
                        "0000000000000000000000000000000010000000000000000000000000000001",
                        "1000000000000000000000000000000010000000000000001000000000001000" ]

        fp2 = open(self.prefix+"Keccak-f1600.inp", "w+")
        if inputstr == None:
            print("Input string: ", end = '')
            x = str(input())
        else:
            x = inputstr
        fp2.write('// Hashing '+x+'\n')
        out = self.stringToBinary(x)
        #print("Bin: ", end = '')
        #print(out)

        sp = self.sponge(out, 1600)
        #print("Sponge: ", end = '')
        #print(sp)

        for i in range(1, 101):

            if i%4 == 1:
                fp2.write("%d "% i)
                for j in range(63, -1, -1):
                    fp2.write("%c"% (sp[64*int(i/4)+j]))
            fp2.write("\n\n")

            if i%4 == 0:
                fp2.write("%d "% i)
                for j in range(0, 64):
                    fp2.write("1")
            fp2.write("\n\n")
    
        RCpos = [1402, 1407, 2712, 2717, 4022, 4027, 5332, 5337, 6642, 6647, 7952, 7957, 9262, 9267, 10572, 10577, 11882, 11887, 13192, 13197, 14502, 14507, 15812, 15817, 17122, 17127, 18432, 18437, 19742, 19747, 21052, 21057, 22362, 22367, 23672, 23677, 24982, 24987, 26292, 26297, 27602, 27607, 28912, 28917, 30222, 30227, 31532, 31537]

        for i in range(0, 24):

            c = RCpos[2*i]

            fp2.write("%d "% c)
            for j in range(0, 64):
                fp2.write("%c"% (RC[i][j]))
            fp2.write("\n\n")

            c = RCpos[2*i+1]

            fp2.write("%d "% c)
            for j in range(0, 64):
                fp2.write("1")
            fp2.write("\n\n")

        fp2.close()
        
if __name__ == '__main__':
    prefix = 'SHA3/'
    ins = SHA3ins(prefix)
    inp = SHA3inp(prefix)

    ins.Keccak()
    inp.genInp()
    
    ins.genConfig()
