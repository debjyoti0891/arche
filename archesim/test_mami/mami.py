#!/usr/bin/python3

import sys
import json
import copy

class MAMI:

    def __init__(self):
        ''' Initializes -
        mxn crossbar [list]
        n-bit long read buffer [list]
        simulation memory [dictionary].
        simulation input [dictionary]
        simulation clock [int]
        '''
        self.voltage = list()

    def __setupSim(self):
        self.sim_type = 'mami'
        self.crossbar = []
        m = self.m
        n = self.n

        for i in range(m):
            wordlines = [0 for i in range(n)]
            self.crossbar.append(wordlines)

        self.read_buffer = [0 for i in range(n)]
        self.PIR = [0 for i in range(n)]
        self.DMR = [0 for i in range(n)]

        self.simulation_mem = dict()
        self.primary_input = dict()

        self.simulation_inp = dict()
        self.__clk = 0

        self.m = m
        self.n = n

        self.ins_file = None
        self.inp_file = None
        self.varin  = None
        self.varout = None
        self.gen_pwl = False

    def loadConfig(self,config_file):
        config_error = 'Config load failed:'
        with open(config_file) as json_file:
            config = json.load(json_file)
        if config == None or config == dict():
            print('Config load from file failed.\nRetry with proper file')
            sys.exit(1)
        # initialize crossbar state
        if 'dim' not in config.keys():
            print(config_error+'Crossbar dimensions missing')
            sys.exit(1)
        else:
            self.m = int(config['dim']['m'])
            self.n = int(config['dim']['n'])
            self.__setupSim()

        # load instructions and PIR
        if 'filename' not in config.keys():
            print(config_error+'filename key missing.')
            sys.exit(1)
        else:
            self.ins_file = config['filename']['ins_mem']
            self.out_file = config['filename']['output']
            if 'input' in config['filename'].keys():
                self.inp_file = config['filename']['input']
            if 'varin' in config['filename'].keys():
                self.varin = config['filename']['varin']
            
            if 'varout' in config['filename'].keys():
                self.varout = config['filename']['varout']
                
        # simulate
        if 'simulation' not in config.keys():
            #default simulation params
            self.cycle = 0
            self.verbose = 1
            self.print_ins = 1
            
        else:

            if 'cycles' not in config['simulation'].keys():
                self.cycle = 0
            else:
                self.cycle = config['simulation']['cycles']

            if 'verbose' not in config['simulation'].keys():
                self.verbose = 0
            else:
                self.verbose = config['simulation']['verbose']

            if 'print_ins' not in config['simulation'].keys() or \
                config['simulation']['print_ins'] == 0:
                self.print_ins = None
            else:
                self.print_ins = config['simulation']['print_ins']

            if 'gen_pwl' not in config['simulation'].keys() or \
                    config['simulation']['gen_pwl'] == 0:
                self.gen_pwl = False
            else:
                self.gen_pwl = True
        
        if 'voltage' in config.keys():
            self.voltage_spec =  config['voltage']
        else:
            self.voltage_spec = None
              # write stats

    def simulateConfig(self, config_file):
        self.loadConfig(config_file)
        self.loadProgram(self.ins_file) 
        if self.inp_file == None:
            print(' Error : Input file not specified [input] ')
            sys.exit(1)
        self.loadPI(self.inp_file)
        print('Simulation started for:' , self.cycle,' cycles')
        self.simulate(self.cycle, self.verbose, self.print_ins,self.voltage_spec)

        # generate output voltage files
        if self.gen_pwl:
            self.writeVoltage(self.out_file)

    def __getLine(self,file_h):
        while True:
            l = next(file_h, None)
            if l == None:
                return l
            l = l.strip()
            comment = l.find('//')
            if comment >= 0:
                l = l[:comment]
            if l == '':
                continue
            else:
                return l

    def __writeLogicMaj(self, crossbar, source, ins, clk, out_f):
        ''' TODO : update '''
        ws = None 
        ''' t Apply dir addr s wb ws val v val v val '''
        if ins[5] == '00':
            ws = '0'
        elif ins[5] == '01':
            ws = '1'
        elif ins[5] == '11':
            ws = source[len(crossbar)-int(ins[6]) - 1]
    
        new_cross = [i for i in crossbar]
        for i in range(len(crossbar)):
            index = len(crossbar)-1 - i
            prefix = 't'+str(clk)+'_'+ins[1]+'_'+str(self.__ins_count)+'_'
            v = ins[7+2*i]
            val = ins[7+2*i+1]
            if v == '0' : # NOP
                continue
            bl =  str(source[index])
            neg = False 
            if bl == '0':
                bl = '1'
            elif bl == '1':
                bl = '0'
            elif bl == '':
                print("Invalid read")
                print("Source: " , source)
                print("Instruction : ", ins)
                sys.exit(0)
            else:
                neg = True 
                bl = '~'+bl 
            c = [str(crossbar[index]), str(ws) , bl]
            c.sort()
            

            prefix = prefix + str(index)
            if c[0] == '0':
                if c[1] == '0':
                    new_cross[index] = '0'
                elif c[1] == '1':
                    new_cross[index] = prefix
                    # assignment
                    if not neg:
                        out_f.write('.names ' + c[2] + ' ' + prefix +'\n')
                        out_f.write('1 1\n')
                    else:
                        out_f.write('.names ' + c[2][1:] + ' ' + prefix + '\n')
                        out_f.write('0 1\n')
                else:
                    new_cross[index] = prefix
                    # AND
                    if not neg:
                        out_f.write('.names '+c[1]+' '+c[2]+' '+prefix+'\n')
                        out_f.write('11 1\n')
                    else:
                        out_f.write('.names '+c[1]+' '+c[2][1:]+' '+prefix+'\n')
                        out_f.write('10 1\n')
            elif c[0] == '1':
                if c[1] == '1':
                    new_cross[index] = '1'
                else:
                    new_cross[index] = prefix
                    # OR
                    if not neg:
                        out_f.write('.names '+c[1]+' '+c[2]+' '+prefix+'\n')
                        out_f.write('00 0\n')
                    else:
                        out_f.write('.names '+c[1]+' '+c[2][1:]+' '+prefix+'\n')
                        out_f.write('01 0\n')

            else:
                new_cross[index] = prefix
                # MAJ
                if not neg:
                    out_f.write('.names '+c[0]+' '+c[1]+' '+c[2]+' '+prefix+'\n')
                    out_f.write('11- 1\n')
                    out_f.write('1-1 1\n')
                    out_f.write('-11 1\n')
                else:
                    out_f.write('.names '+c[0]+' '+c[1]+' '+c[2][1:]+' '+prefix+'\n')
                    out_f.write('11- 1\n')
                    out_f.write('1-0 1\n')
                    out_f.write('-10 1\n')


        return new_cross 

    def __writeLogicMagic(self, crossbar, ins, clk, out_f):
        ''' t Magic dir addr k i_1 i_2 ... i_k o '''
        prefix = 't'+str(clk)+'_'+ins[1]+'_'+str(self.__ins_count)+'_'
        new_cross = [i for i in crossbar]
        k = int(ins[4])
        inputs = []
        for i in ins[5:-1]:
            inputs.append(len(crossbar)-int(i)-1)
        output = len(crossbar) - int(ins[-1]) -1  
        
        if crossbar[output] != '0' and crossbar[output] != '1':
            print('Attempted MAGIC write on a dirty cell')
            print('Crossbar state:' ,  crossbar)
            print('Instruction :' , ins)
            sys.exit(0)
        new_cross[output] = prefix
        out_f.write('.names ')
        for i in inputs:
            out_f.write(crossbar[i]+' ')
        out_f.write(prefix+'\n')
        for i in range(len(inputs)):
            out_f.write('0')
        out_f.write(' 1\n')
        return new_cross

    def __writeHeader(self, out_file):
        out_file.write('.model top\n')
        # get inputs
        var_in = open(self.varin)
        var_out = open(self.varout)
        var_in_set = set()
        while(True):
            l = self.__getLine(var_in)
            if l == None:
                break
            var_in_set.update(set(l.split()[1:]))
        var_in_set = var_in_set - set(['0','1'])
        out_file.write('.inputs ')
        for var in var_in_set:
            out_file.write(var + ' ')
        out_file.write('\n')

        # get outputs 
        var_out_set = set()
        while True:
            l = self.__getLine(var_out)
            if l == None:
                break
            l = l.split()[1:]

            for i in range(0,len(l),3):
                var_out_set.add(l[i])
        var_out_set = var_out_set - set(['0','1'])
        out_file.write('.outputs ')
        for var in var_out_set:
            out_file.write(var + ' ')
        out_file.write('\n')

        var_in.close()
        var_out.close()


    def genBlif(self, config_file):
        ''' TODO : update '''
        self.loadConfig(config_file)
        ''' read each instruction 
            ---> check corresponding varin -> update if t_var_in < curr_clk
            ---> check corresponding varout -> update if t_var_in < curr_clk
            ---> write blif item '''
        out_blif = open(self.out_file+'.blif','w')
        self.__writeHeader(out_blif)
        var_in = open(self.varin)
        var_out = open(self.varout)
        curr_clk = 0
        in_clk = 0
        out_clk = 0
        # clk, inputs
        curr_in = [(None,None), (None, None)]
        # clk, outputs
        curr_out = [(None,None), (None, None)]
        # crossbar state 
        crossbar = [[0 for j in range(self.n)] for i in range(self.m)]
        dmr = None
        ins_f = open(self.ins_file)
        self.__ins_count = 0
        while True:
            ins = self.__getLine(ins_f)
            if ins == None:
                break
            #curr_clk = curr_clk+1
            self.__ins_count = self.__ins_count + 1
            if not self.__checkValid(ins):
                print('Invalid Instruction')
                print(curr_clk,' : ', ins)
                sys.exit(1)
            ins = ins.split()
            curr_clk = int(ins[0])
            opcode = ins[1]
            compute_dir = ins[2]
            addr = int(ins[3])


            ''' check varin '''
            if in_clk < curr_clk:
                input_line = self.__getLine(var_in)
                if input_line != None: # the line is valid
                    input_line = input_line.split()
                    in_clk = int(input_line[0])
                    curr_in[0] = curr_in[1]
                    curr_in[1] = (in_clk, input_line[1:])
                    
            ''' check varout '''
            if out_clk < curr_clk:
                input_line = self.__getLine(var_out)
                if input_line != None: # the line is valid
                    input_line = input_line.split()
                    out_clk = int(input_line[0])
                    curr_out[0] = curr_out[1]
                    curr_out[1] = (out_clk, input_line[1:])
                    
            ''' decode the instruction and write to the blif file ''' 
            print(ins)
            if curr_in[1][0] != None and curr_in[1][0] <= curr_clk:
                pir = curr_in[1][1]
            elif curr_in[0][0] != None:
                pir = curr_in[0][1]
            else:
                pir = None
            print(ins) 
            if opcode == 'Read':
                if compute_dir == '0':
                    dmr = copy.deepcopy(crossbar[addr])
                else:
                    dmr = []
                    for i in range(self.m):
                        dmr.append(crossbar[i][addr])
                for i in range(max(self.m,self.n)-len(dmr)):
                    dmr.append('')

            elif opcode == 'Apply': 
                if ins[4] == '0': #s 
                    source = pir
                else:
                    source = dmr
                if compute_dir == '0':
                    wl = addr
                    crossbar[wl] = self.__writeLogicMaj(crossbar[wl], source, ins, curr_clk, out_blif)
                else:
                    crossbar_bl = []
                    for i in range(self.m):
                        crossbar_bl.append(crossbar[i][addr])
                    crossbar_bl = self.__writeLogicMaj(crossbar_bl, source, ins, curr_clk, out_blif)
                    for i in range(self.m):
                        crossbar[i][addr] = crossbar_bl[i]
            elif opcode == 'Magic':
                if compute_dir == '0':
                    crossbar[wl] = self.__writeLogicMagic(crossbar[wl], source, ins, curr_clk, out_blif)
                else:
                    crossbar_bl = []
                    for i in range(self.m):
                        crossbar_bl.append(crossbar[i][addr])
                    crossbar_bl = self.__writeLogicMagic(crossbar_bl,  ins, curr_clk, out_blif)
                    for i in range(self.m):
                        crossbar[i][addr] = crossbar_bl[i]
            # Edit from here
            if curr_clk == curr_out[0][0]:
                print('out found :', curr_clk, curr_out[0][0])
                for i in range(int(len(curr_out[0][1])/3)):
                    out = curr_out[0][1][3*i]
                    r = int(curr_out[0][1][3*i+1])
                    c = int(curr_out[0][1][3*i+2])
                    out_blif.write('.names '+crossbar[r][c]+' '+out+'\n')
                    out_blif.write('1 1\n')
            elif curr_clk == curr_out[1][0]:
                print('out found :', curr_clk, curr_out[1][0])
                for i in range(int(len(curr_out[1][1])/3)):
                    out = curr_out[1][1][3*i]
                    r = int(curr_out[1][1][3*i+1])
                    c = int(curr_out[1][1][3*i+2])
                    out_blif.write('.names '+crossbar[r][c]+' '+out+'\n')
                    out_blif.write('1 1\n')
            print(curr_clk, ins)
            print(in_clk, curr_in)
            print(out_clk, curr_out)
        out_blif.write('.end\n')
        out_blif.close()
        var_in.close()
        var_out.close() 

    def __addInstruction(self,instruction):
        ''' Decodes an instruction to wordline
        and bit line inputs and adds it to
        simulation memory '''


        ''' Instruction types :
            t Read dir addr 
            t Apply dir addr s ws wb (v val_1) .. (v val_n)
            t Magic dir addr k i_1 i_2 ... i_k o 
            t Init dir addr b_1b_2...b_k

            t       = clock cycle
            dir     = direction of compute
                0 : wordline
                1 : bitline 
            addr    = wordline/bitline addr 
            s       = source select
                0 : PIR
                1 : DMR
            ws      = wordline source select
                00 : 0
                01 : 1
                10 : Invalid
                11 : either DMR or PIR based on s
            wb, val_1,..,val_n,i_1,..,i_k = wordline/bitline address (>=0 , < n)
            v       = valid flag
            b_i     = single bit
        '''
        valid = self.__checkValid(instruction)
        if not valid:
            print('Error : Invalid instruction')
            print(instruction)
            sys.exit(1)
        if self.__clk in self.simulation_mem.keys():
            self.simulation_mem[self.__clk].append(instruction)
        else:
            self.simulation_mem[self.__clk] = [instruction]

    def __checkValidAddr(self, compute_dir, address):
        valid = True 
        address = int(address)
        if compute_dir  == '0' and (address >= self.m or address < 0):
            print('Invalid read address', address)
            valid = False
        elif compute_dir == '1' and (address >= self.n or address < 0):
            print('Invalid read address',address)
            valid = False
        elif compute_dir != '0' and compute_dir != '1':
            print('Compute direction:', compute_dir)
            print('Invalid compute direction')
            valid = False
        return valid

    def __checkValid(self,ins):
        ''' check if an instruction is valid'''
        ins = ins.split()
        clock = int(ins[0])
        opcode = ins[1]
        compute_dir = ins[2]
        addr = int(ins[3])
        valid = True
        m = self.m
        n = self.n
        if not self.__checkValidAddr(compute_dir, addr):
            print('Invalid address')
            return False
        #elif clock != 1 and (self.__clk != clock or self.__clk != clock+1):
        #    print('Invalid clock cycle')
        #    return False
        # TODO : add checking for clock cycle sanity
        if opcode == 'Apply':
            if compute_dir == '0':
                exp_len = 7 + 2*n
            else:
                exp_len = 7 + 2*m

            if len(ins) != exp_len:
                valid = False
                print('Invalid number of elements in instruction')
                print('Expected:',exp_len)
                return valid
            s = ins[4]
            ws = ins[5]
            wb = int(ins[6])
            if s != '1' and s != '0':
                print(' Invalid source select flag')
                valid = False
            elif ws not in ['00', '01', '11']:
                print(' Invalid wordline select')
                valid = False
            elif ws == '11' and (compute_dir == '0' and wb >= n) \
                    or (compute_dir == '1' and wb >= m) \
                    or wb < 0:
                print(' Invalid wordline input address')
            else:
                for i in range(7,exp_len,2):
                    v = int(ins[i])
                    val = int(ins[i+1])
                    if (v != 0 and v!= 1) or val < 0 \
                            or (compute_dir == '0' and val >= n) \
                            or (compute_dir == '1' and val >= m):
                        valid = False
                        print('Invalid valid,addr pair (',v,',',val,')')
                    if not valid:
                        break
        elif opcode == 'Magic':
            k = int(ins[4])
            if clock in self.simulation_mem.keys():
                old_ins = self.simulation_mem[clock][0]
                old_ins = old_ins.split()
                old_k = int(old_ins[4]) 
                if k != old_k:
                    print('Different number of inputs for parallel instructions')
                    valid = False
                else:
                    for i in range(5, 5+k+1):
                        if old_ins[i] != ins[i]:
                            print('Inputs are not aligned for parallel instructions')
                            valid = False
                            break
            else:
                if k < 0 or (compute_dir == '0' and k + 1 >= n) \
                        or (compute_dir == '1' and k+1 >= m):
                    print('Invalid number of inputs in Magic instruction')
                    valid = False
                else:
                    for i in range(5, 5+k+1):
                        valid = self.__checkValidAddr(compute_dir, ins[i])
                        if not valid:
                            break

                
        elif opcode != 'Read':
            print('Invalid opcode')
            valid = False
        if valid:
            self.__clk = clock
        return valid

    def loadProgram(self,program_file):
        ''' loads program from program_file
        and adds the instructions to simulation memory

        Program file format:
        t opcode operands
        Any content after "//" is ignored
        '''

        f = open(program_file)
        for ins in f:
            ins = ins [:-1]
            comment_start = ins.find('//')
            if  comment_start == 0:
                continue
            elif comment_start > 0:
                ins = ins[:comment_start]
            #print('len',len(ins))
            if len(ins) == 0:
                continue
            self.__addInstruction(ins)

        f.close()

    def loadPI(self,primary_in_file):
        # clock primary_in_values
        f = open(primary_in_file)
        for l in f:
            l = l [:-1]
            comment_start = l.find('//')
            if  comment_start == 0:
                continue
            elif comment_start > 0:
                l = l[:comment_start]
            #print('len',len(ins))
            if len(l) == 0:
                continue

            w = l.split()
            if l == '' or l == '\n':
                continue
            if len(w[1]) != max(self.n,self.m):
                print('Invalid Primary Input in clock :', w[0])
                print(w)
                sys.exit(1)
            else:
                binOnly = True
                for b in w[1]:
                    if b!= '0' and b!= '1':
                        print(' Primary input should be in binrary')
                        binOnly = False
                        break
                if not binOnly:
                    print(w)
            self.primary_input[int(w[0])] = w[1]

        #print('Primary input data:',self.primary_input)
        f.close()


    def printInstructionMemory(self,clk=None):
        if clk == None:
            for i in range(1,self.__clk+1):
                for ins in self.simulation_mem[i]:
                    print('Cycle', i, ':', ins)

        else:
            for ins in self.simulation_mem[clk]:
               print('Cycle', clk, ':', ins) 

    def update_crossbar(self,clk,voltage_spec = None):
        ''' TODO '''
        ins = self.simulation_mem[clk]
        print(ins)
        opcode = ins[0]
        w = int(ins[1])
        if voltage_spec != None:
            curr_vol = [0.0 for i in range(self.m+self.n)]

        if opcode == 'Read':
            self.DMR = copy.deepcopy(self.crossbar[w])
            print('DMR:',self.DMR)
            if voltage_spec != None:
                curr_vol[w] = voltage_spec['1']

        elif opcode == 'Apply':
            s = ins[2]
            ws = ins[3]
            wb = int(ins[4])
            #print('s',s, type(s))
            if(s == '0') : # PIR input
                #print(clk,self.primary_input.keys())
                if(clk in self.primary_input.keys()):
                    self.PIR = list(self.primary_input[clk])
                    print('Loading to PIR', self.PIR)
                in_reg = self.PIR
            else:
                in_reg = self.DMR
            #rev_in_reg = [len(in_reg)-1-i for i in range(len(in_reg))]
            #in_reg = rev_in_reg

            print('In reg:',in_reg)
            w_in = ''
            if ws == '00':
                w_in = 0

            elif ws == '01':
                w_in = 1
            elif ws == '11':
                w_in = in_reg[ws]
            #print(w_in,voltage_spec)
            curr_vol[w] = voltage_spec[str(w_in)]

            b_in = []
            bl = 0
            for i in range(5,len(ins),2):
                v = ins[i]
                b = ins[i+1]
                #print('b', b, in_reg)
                if v == '1':
                    b_in = b_in+ [in_reg[self.n-1-int(b)]] 
                    curr_vol[self.m + bl] = voltage_spec[str(in_reg[self.n-1-int(b)])]
                else:
                    b_in = b_in + ['NOP']
                bl = bl+1

            #print(ins,w,s,ws,wb,w_in,b_in,in_reg)
            for i in range(self.n):
                print('device:',self.n-1-i,'wl:',w_in,'bl',b_in[i])
                if str(w_in) == '0' and str(b_in[i]) == '1':
                    self.crossbar[w][i] = 0
                elif str(w_in) == '1' and str(b_in[i]) == '0':
                    self.crossbar[w][i] = 1

        if voltage_spec != None:
            self.voltage.append(curr_vol)

    def printCrossbarState(self,msg=None):
        if msg != None:
            print('Crossbar State [',msg,'] :')
        else:
            print('Crossbar state:')
        for i in range(self.m-1,-1,-1):
            for j in range(0,self.n):
                print(self.crossbar[i][j],end='')
            print('',end='\n')


    def simulate(self, clk=0, verbose = -1, print_ins = None, voltage_spec = None):
        ''' simulate the crossbar computation for n cycles.
            If n = -1, run simulation for __clk cycles '''

        if clk == 0:
            clk = self.__clk

        for clock in range(1,clk+1):

            self.update_crossbar(clock,voltage_spec)

            if verbose == 0:
                if print_ins != None:
                    self.printInstructionMemory(clock)
                else:
                    print('Simulation Clk :',clock)
                self.printCrossbarState()

            elif verbose > 0 and clock%verbose == 0:

                if print_ins != None:
                    self.printInstructionMemory(clock)
                else:
                    print('Simulation Clk :',clock)
                self.printCrossbarState()


    def writeVoltage(self,out_fname):
        ''' TODO : change       '''
        #print('write:',self.voltage)
        steps = len(self.voltage)

        if steps == 0 or self.voltage_spec == None:
            print('Error: writeVoltage failed.\nRetry after design simulation with voltage spec.')
            sys.exit(1)

        for vi in range(self.m + self.n):

            f = open(out_fname+'V_'+str(vi)+'_pwl','w')
            period = self.voltage_spec['period']
            delta = self.voltage_spec['delta']
            state = 0
            clock = 10
            volt = self.voltage_spec['1']
            # initial delay
            f.write(str(0)+'\t'+str(volt)+'\n')
            f.write(str(clock*10**-9)+'\t'+str(volt)+'\n')
            for t in range(steps):

                clock = clock+delta
                volt = self.voltage[t][vi]
                f.write(str(clock*10**-9)+'\t'+str(volt)+'\n')

                clock = clock+period
                f.write(str(clock*10**-9)+'\t'+str(volt)+'\n')

            f.close()




if __name__ == '__main__':

    if len(sys.argv) == 5:
        #TODO : update
        sys.exit(1)
        crossbar = MAMI(int(sys.argv[1]),int(sys.argv[2]))
        crossbar.loadProgram(sys.argv[3])
        crossbar.loadPI(sys.argv[4])
        crossbar.printInstructionMemory()
        crossbar.simulate(0,0)
    elif len(sys.argv) == 2:
        crossbar = MAMI()
        #crossbar.simulateConfig(sys.argv[1])
        crossbar.genBlif(sys.argv[1])
    else:
        print('Invalid command line arguments ')
        print('python3 mami.py config.json')
