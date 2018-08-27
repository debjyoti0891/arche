# coding=utf-8
"""
Arche 
"""
import os
import atexit
import readline
from cmd2 import Cmd, make_option, options, set_use_arg_list

# custom packages 
import archeio.hdlread
import archeio.graphio 
import archetech.smr
import archetech.techmagic  


history_file = os.path.expanduser('~/.arche_history')
if not os.path.exists(history_file):
    with open(history_file, "w") as fobj:
        fobj.write("")
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
    techMapper = None 

    def __init__(self):
        self.settable.update({'row': 'Number of crossbar rows'})
        self.settable.update({'col': 'Number of crossbar columns'})
        self.settable.update({'dev': '1S1R or VTEAM'})
        Cmd.__init__(self)
    
    @options([make_option('-t', '--tech', type="int",  action="store",  help='map using technology [TECH] ReVAMP [0], MAGIC [1], SAT MAGIC[2]'),
    make_option('-d', '--display', action='store_true', help='print intermediate results'),
    make_option('-c', '--cycles', type="int", action='store', help='constraint on number of cycles available for mapping'),
    make_option('-i', '--iterations', type="int", action='store', help='constraint on number of iterations to find minimum number of devices [0 = unconstrained]'),
    make_option('-m', '--minimum', action='store_true', help='find minimum number of devices required for mapping')])
    def do_map(self, arg, opts=None):
        ''' maps the loaded netlist '''
        if self.debug : print(opts.tech, opts.display) 
        if (len(self.graphDb) == 0):
            print('load a mapped netlist before mapping ')
        else:
            print('tech:',opts.tech) 
            if opts.tech == 1:
                self.techMapper = archetech.techmagic.TechMagic(self.debug)
                self.techMapper.map(self.row, self.col, self.graphDb[-1])
            elif opts.tech == 2:
                if opts.cycles == None and not opts.minimum:
                    print(' the option --cycles must be specified for SAT based mapping')
                    return
                
                if len(archeio.graphio.getOutputs(self.graphDb[-1])) == 0:
                    print('Error: Input netlist does not have an output')
                    return
                if not opts.minimum:
                    feasible,solution = archetech.smr.optiRegAlloc(archeio.graphio.getPredList(self.graphDb[-1]),\
                    len(self.graphDb[-1].vs),\
                    archeio.graphio.getOutputs(self.graphDb[-1]),\
                    self.col,\
                    opts.cycles,\
                    opts.display)
                else: 
                    minReg,solution= archetech.smr.minRegAlloc(archeio.graphio.getPredList(self.graphDb[-1]),\
                    len(self.graphDb[-1].vs),\
                    archeio.graphio.getOutputs(self.graphDb[-1]),\
                    opts.cycles,\
                    opts.iterations,\
                    opts.display)
                    print('Min reg needed :', minReg)


    @options([make_option('-f', '--file', type="string", help='write mapping stats to file')])
    def do_ps(self, arg, opts=None):
        ''' print the statistics of mapping '''
        if self.debug : print(opts.file) 
        if (self.techMapper == None):
            print('Map a circuit before printing stats')
        else:
            if opts.file != None:
                with open(opts.file,'a') as f:
                    f.write(self.graphFile[-1]+','+self.techMapper.getStats()+'\n')
            print('benchmark,#pi,#po,#gates,#level,delay,speedup,r,c,#devices, utilization')
            print(self.graphFile[-1],self.techMapper.getStats())


    def do_read(self,arg, opts=None):
        ''' Read a mapped verilog netlist file '''
        print('read file :' , arg)
        self.graphFile.append(arg)
        g = archeio.hdlread.read_mappedverilog(arg)
        if self.debug : print(g['pi'])
        self.graphDb.append(g) 

    def do_showgraph(self,arg,opts=None):
        ''' write the graph in .gml format'''
        if len(self.graphDb) <= 0:
            print('No graphs loaded')
        else:
            g = self.graphDb[-1]
            if arg == None:
                arg = 'graph.gml'
            #g.write_edgelist(arg)
            g.save(arg,format='gml')
            # TODO : generate a ps out of the gml
            # gmltogv graph.gml bla.dot
            # dot -Tps bla.dot -o graph.ps 



    def _onchange_dev(self, old, new):
        # change the voltage params based on device
        if new == '1S1R':
            print('1S1R devices')
        elif new == 'VTEAM':
            print('VTEAM devices')
        else:
            print('invalid device')
            self.dev = old


if __name__ == '__main__':
    stdin = open('in')
    c = ArcheTech()
    c.cmdloop()
