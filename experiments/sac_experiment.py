import sys
import logging

sys.path.insert(1, '../')
from archetech.spirit.sac_mapper import SACMapper
from archetech.spirit.mapping_solution import verifyOutput

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print('usage: python3 sac_experiment.py benchmark benchdir R C k logfile')
        sys.exit(0)
    # for i,val in enumerate(sys.argv):
    #     print(i,val)
    benchmark = sys.argv[1]
    bench_dir = sys.argv[2]
    R = int(sys.argv[3])
    C = int(sys.argv[4])
    k = int(sys.argv[5])
    logfile = sys.argv[6]

    logging.basicConfig(filename=logfile,  level=logging.DEBUG)
    newObj = SACMapper(benchmark,bench_dir,logfile, False, True)
    newObj.mapBenchmark(R,C,k)
    i = benchmark.rfind('/')
    if i>=0:
        benchfile = benchmark[i+1:]
    else:
        benchfile = benchmark 
    outfile = 'Cr_{}_{}_k{}_{}.v'.format(R, C, k, benchfile)
    res,out = verifyOutput(
        benchmark, \
        bench_dir+outfile,
        bench_dir
    )

    if res is not True:
        print('Output file is not identical to input netlist')
        logging.debug(' verification failed for {} and {}'.\
            format(benchmark, bench_dir+outfile))