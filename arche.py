#!/usr/bin/python3
# coding=utf-8
"""
Arche 
"""
import os
import atexit
import argparse
import datetime
import readline
from cmd2 import Cmd 
import cmd2
import json
import random
from z3 import sat
import time 

# custom packages 
import archeio.hdlread
import archeio.graphio 
import archeio.solution 

import archesim.revamp 
import archesim.bench.gen_SHA3
import archesim.bench.gen_SHA2
import archetech.smr
import archetech.techmagic  
import archetech.mimd
import logging

history_file = os.path.expanduser('~/.arche_history')
if not os.path.exists(history_file):
    with open(history_file, "w") as fobj:
        readline.read_history_file(history_file)
        atexit.register(readline.write_history_file, history_file)

class ArcheTech(Cmd):
    """ Techmapping application for ReRAM crossbar array. """

    prompt = "arche>"
    intro = "Synthesis and technology mapping for emerging technologies"
    row = 16
    col = 16
    dev = '1S1R'
    debug = False
    graphDb = [] 
    graphFile = []
    __sol     = archeio.solution.Solution()
    __logFile = None
    techMapper = None 

    def __init__(self,persistent_history_file=history_file):
        super().__init__()
        self.settable.update({'row': 'Number of crossbar rows'})
        self.settable.update({'col': 'Number of crossbar columns'})
        self.settable.update({'dev': '1S1R or VTEAM'})
        Cmd.__init__(self)

    mapParser = argparse.ArgumentParser()
    mapParser.add_argument('-t', '--tech', type=int,  action="store",  help='map using technology [TECH] ReVAMP [0], MAGIC [1], SAT MAGIC[2]')
    mapParser.add_argument('-d', '--dir', action='store_true', help='specifies output directory [optional]')
    mapParser.add_argument('-v', '--verbose', action='store_true', help='print intermediate results')
    @cmd2.with_argparser(mapParser)
    def do_map(self, args):
        if self.debug : print(args.tech, args.verbose) 
        if (len(self.graphDb) == 0):
            print('load a mapped netlist before mapping ')
        else:
            print('tech:',args.tech) 
            if args.tech == 1:
                self.techMapper = archetech.techmagic.TechMagic(self.debug)
                self.techMapper.map(self.row, self.col, self.graphDb[-1])
         


    rowsatParser = argparse.ArgumentParser()
    rowsatParser.add_argument('-c', '--col', type=int, action='store', help='specify number of devices in a column [ignored by -m flag]')
    rowsatParser.add_argument('-d', '--dir', action='store_true', help='specifies output directory [optional]')
    rowsatParser.add_argument('-f', '--filename', type=str, help='write mapping stats to file')
    rowsatParser.add_argument('-i', '--iterations', type=int, action='store', help='constraint on number of iterations to find minimum number of devices [0 = unconstrained]')
    rowsatParser.add_argument('-md', '--mindev', action='store_true', help='find minimum number of devices required for mapping')
    rowsatParser.add_argument('-ms', '--minstep', action='store_true', help='find minimum number of steps required for mapping')
    rowsatParser.add_argument('-s', '--steps', type=int, action='store', help='constraint on number of cycles available for mapping')
    rowsatParser.add_argument('-t', '--timelimit', type=int, action='store', help='constraint on runtime of sat solver')
    rowsatParser.add_argument('-v', '--verbose', action='store_true', help='print intermediate results')
    @cmd2.with_argparser(rowsatParser)      
    def do_rowsat(self, args):
        '''maps the loaded net)list '''
        print(args.filename, args.timelimit)
        if args.steps == None and not (args.mindev or args.minstep):
            print(' the option --cycles must be specified for SAT based mapping')
            return

        if len(archeio.graphio.getOutputs(self.graphDb[-1])) == 0:
            print('Error: Input netlist does not have an output')
            return
        logging.info('min reg allocation command execution start')
        if args.col != None:
            col = args.col
        else:
            col = self.col
        if not (args.mindev or args.minstep) :
            feasible,model,solution = archetech.smr.optiRegAlloc(archeio.graphio.getPredList(self.graphDb[-1]),\
                    len(self.graphDb[-1].vs),\
                    archeio.graphio.getOutputs(self.graphDb[-1]),\
                    col,\
                    args.steps,\
                    args.filename,\
                    args.verbose,\
                    args.timelimit)
            if feasible == sat:
                print('Solution obtained %d devices %d steps' % (args.col, args.steps))
                minReg = args.col
                steps = args.steps
            else:
                print('Solution could not be obtained')
                minReg = -1
                steps = -1
        else: 
            if args.mindev and args.minstep:
                optiType = 3
            elif args.minstep:
                optiType = 2;
            else :
                optiType = 1;    
                 
            minReg,steps,solution= archetech.smr.minRegAlloc(archeio.graphio.getPredList(self.graphDb[-1]),\
            len(self.graphDb[-1].vs),\
            archeio.graphio.getOutputs(self.graphDb[-1]),\
                col,\
                args.steps,\
                optiType,\
                args.iterations,\
                args.filename,\
                args.verbose,\
                args.timelimit)
            
            if args.mindev and args.minstep:
                print('Min devices : %d Min steps : %d'% (minReg,steps))
            elif args.minstep:
                print('Devices : %d Min Steps : %d'% (minReg,steps))
            else :
                print('Min Devices : %d Steps : %d'% (minReg,steps))    
            logging.info('Min sat allocation command execution complete')
            logging.info('Devices: %d, Cycles: %s, Optitype : %s' % (minReg,steps,optiType)) 
    psParser = argparse.ArgumentParser()
    psParser.add_argument('-f', '--filename', type=str, help='write mapping stats to file')
    @cmd2.with_argparser(psParser)
    def do_ps(self, args):
        ''' print the statistics of mapping '''
        if self.debug : print(args.filename) 
        if (self.techMapper == None):
            print('Map a circuit before printing stats')
        else:
            if args.filename != None:
                with open(args.file,'a') as f:
                    f.write(self.graphFile[-1]+','+self.techMapper.getStats()+'\n')
            print('benchmark,#pi,#po,#gates,#level,delay,speedup,r,c,#devices, utilization')
            print(self.graphFile[-1],self.techMapper.getStats())
    
    crossbarParse = argparse.ArgumentParser()
    crossbarParse.add_argument('-d', '--dir', type=str, help='write output files to directory')
    crossbarParse.add_argument( '--delay', action='store_true', help='minimize delay of technology mapping with word length constraint')
    crossbarParse.add_argument( '--area', action='store_true', help='minimize delay of technology mapping with crossbar dimension constraint')
    crossbarParse.add_argument( '-f', '--file', type=str, help='write the instructions to the specified directory')
    @cmd2.with_argparser(crossbarParse)
    def do_mapcrossbar(self, args):
        ''' Maps a netlist to a crossbar using ReVAMP instructions ''' 
        if args.file == None:
            print('Error: Benchmark must be specified using --file option')
            return
        if args.delay:
            print('Mapping with word length %d' % (self.col))
        else :
            print('Mapping with crossbar dimension %dX%d' %(self.row, self.col))
   
   
    revParser = argparse.ArgumentParser()
    revParser.add_argument('-f', '--file', type=str, help='ReVAMP simulation configuration file')
    @cmd2.with_argparser(revParser)
    def do_revamp(self, args):
        ''' Simulate a benchmark using the ReVAMP architecture ''' 
        
        if args.file != None:
            crossbar = archesim.revamp.ReVAMP()
            crossbar.simulateConfig(args.file)
        else:
            print('Simulation configuration file must be specified')
            return None
        
    shaParser = argparse.ArgumentParser()
    shaParser.add_argument('-t', '--text', type=str, help='Text to be hashed')
    shaParser.add_argument('-g', '--gen', type=str, help='Valid option: sha2,sha3')
    shaParser.add_argument('-d', '--dir', type=str, help='Output directory')
    @cmd2.with_argparser(shaParser)
    def do_sha(self, args):
        ''' Generate instructions for hashing a given text on ReVAMP ''' 
        
        if args.text == None:
            print('Error: Text to be hashed must be specified')
            return 
        if args.gen == None:
            args.gen = 'sha3'
        
        if args.dir == None:
            print('Error: Output directory must be specified ')
            return   
        else:
            if args.dir[-1] != '/':
                args.dir = args.dir+'/'
                
        prefix = args.dir + 'h'+'{date:%Y-%m-%d_%H:%M:%S}'.format( date=datetime.datetime.now())
        if args.gen == 'sha3':
            

            ins = archesim.bench.gen_SHA3.SHA3ins(prefix)
            inp = archesim.bench.gen_SHA3.SHA3inp(prefix)

            ins.Keccak()
            inp.genInp(args.text)
            
            ins.genConfig()
        elif args.gen == 'sha2':
            
            sha2obj = archesim.bench.gen_SHA2.SHA2512(prefix,args.text,True)
        else:
            print('Error: Invalid hashing algorithm specified. Supported: sha2, sha3')

        
            
          
        
            
    logParser = argparse.ArgumentParser()
    logParser.add_argument('-f', '--filename', type=str, help='write mapping stats to file')
    @cmd2.with_argparser(logParser)
    def do_setlog(self, args):
        ''' set the log file name ''' 
        print('set log file :', args.filename)
        
        if args.filename != None:
            logging.basicConfig(filename=args.filename,  level=logging.DEBUG)  
        else:
            print('Filename must be specified')
        self.__logFile = args.filename

    def do_read(self,arg ):
        ''' Read a mapped verilog netlist file '''
        print('read file :' , arg)
        self.graphFile.append(arg)
        g = archeio.hdlread.read_mappedverilog(arg,self.debug)
        if self.debug : print(g['pi'])
        self.graphDb.append(g) 

    def do_showgraph(self,arg):
        ''' write the graph in .gml format'''
        if len(self.graphDb) <= 0:
            print('No graphs loaded')
        else:
            g = self.graphDb[-1]
            if arg == None:
                arg = 'graph.gml'
            g.write_edgelist(arg)
            #g.save(f,format='gml')
            # TODO : generate a ps out of the gml
            # gmltogv graph.gml bla.dot
            # dot -Tps bla.dot -o graph.ps 

    mimdParser = argparse.ArgumentParser()
    mimdParser.add_argument('-f','--files', type=str, nargs='+')
    mimdParser.add_argument('-o','--output', type=str)
    mimdParser.add_argument('-md', '--mindev', action='store_true')
    mimdParser.add_argument('-t', '--timelimit', type=int)
    mimdParser.add_argument('-cs', '--checksol', action='store_true')
    mimdParser.add_argument('-v', '--verbose', action='store_true')
    @cmd2.with_argparser(mimdParser)
    def do_mimd(self,arg):
        ''' maps two or more functions using MAGIC operation.
            Each function is mapped to  a single row.
            The method uses Z3 to maximimze parallel operations for the input functions and reduce delay. Secondary goal to minimize number of colors used. '''
        if arg.files == None or len(arg.files) < 2:
            print('two or more benchmark files required for mimd')
            return 
        if arg.output == None:
            print('Output file must be specified')
            return 
        print(arg.files, arg.output, arg.mindev, arg.checksol)
        self.__sol.startSol()
        self.__sol.addParam('arg', 'mimd')
        self.__sol.addParam('files',arg.files)
        self.__sol.addParam('minDev', arg.mindev)
        self.__sol.addParam('checksol',arg.checksol)
        self.__sol.addParam('outfile',arg.output)
        self.__sol.addParam('timelimit', arg.timelimit)
        start = time.time()
        for f in arg.files:
            self.do_read(f)
       
        # convert the files into edge lists 
        edgeLists = []
        i = 0
        for g in self.graphDb[len(self.graphDb)-len(arg.files):]:
            i = i +1
            edgeLists.append('/tmp/edge_'+str(i)+'_'+str(time.time())+'_'+str(random.randint(1,100)))
            g.write_edgelist(edgeLists[-1])
        
        #call mimd instance
        techMapper = archetech.mimd.MIMD([])
        readStatus = techMapper.readGraph(edgeLists)
        if readStatus == None:
            self.__sol.addParam('failed', True)
        else:
            if not arg.mindev:
                techMapper.genSolution(arg.output, arg.timelimit, arg.verbose)
            else:
                techMapper.genMinSolution(arg.output, arg.timelimit, arg.verbose)
                
            if arg.checksol:
                techMapper.checkSolution(arg.output)
        end = time.time()
         
        self.__sol.addParam('time',"%.2f"%(end-start))
        #print(self.__sol.getSolution())   
        
        
        if self.__logFile != None:
            with open(self.__logFile, 'a') as fp:
                json.dump(self.__sol.getSolution(), fp)
                fp.write('\n')     
        
        
        
    def _onchange_dev(self, old, new):
        # change the voltage params based on device
        if new == '1S1R':
            print('1S1R devices')
        elif new == 'VTEAM':
            print('VTEAM devices')
        else:
            print('invalid device')
            self.dev = old
     
    def cmdloop_with_keyboard_interrupt(self):
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print('Keyboard Interrupt Received. Quitting\n')
            sys.exit(0)
if __name__ == '__main__':
    #stdin = open('in')
    c = ArcheTech()
    c.cmdloop_with_keyboard_interrupt()
