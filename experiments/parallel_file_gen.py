import glob
import os 
import sys

if len(sys.argv) < 5:
    print('usage: python3 parallel_file_gen.py dir/ [blif|v] testdir logfile')
    sys.exit(0)

benchdir = sys.argv[1]
filetype = sys.argv[2]
testdir = sys.argv[3]
logfile = sys.argv[4]
files = glob.glob(benchdir+'*.'+filetype)

outf = open('parallelfile.sh', 'w')
# create test_directory 
t = 10

for k in [4]:
    for spacing in [2]:
        for dims in [(256,256)]:
            for f in files:
                t = t+1
                dirpath = '{}/test{}/'.format(testdir,t)
                outf.write('mkdir {}; python3 sac_experiment.py  {} {} {} {} {} {} {} \n '.format(dirpath, f, dirpath, dims[0], dims[1], k,  logfile, spacing))
                # try:
                #         os.makedirs(dirpath)
                # except OSError:
                #     print ("Creation of the directory %s failed" % dirpath)
                # else:
                #     print ("Successfully created the directory %s" % dirpath)

outf.close() 