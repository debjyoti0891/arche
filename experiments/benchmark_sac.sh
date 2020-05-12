#!/bin/bash

# This files runs mimd for all the benchmark files 
# specified by the input directory

# ./benchmark.sh benchDir timeLimit

# might need this:
# export $(dbus-launch)
# klipper
abcInput="abcIn.txt"
archeInput="archeIn.txt"
archeLog="example.log"
statsFile="archeStat.txt"

benchLog="synthesis_benchmark.log"
dash="======================================================="
dashSmall="------------------------------------------------------"

# header of benchmark.log
echo "$dash" > $benchLog
echo "Arche ReRAM Technology Mapping Benchmarking ToolSuite v1.0" >> $benchLog
echo "Author : Debjyoti Bhattacharjee"           >> $benchLog
echo "$dash" >> $benchLog
echo "Benchmarking started at `date`" >> $benchLog
echo "$dashSmall" >> $benchLog
echo "`date`" >> logmap 

# get target directory
if [ "$1" != "" ]; then
    targetDir=$1
else
    targetDir="`pwd`/"
fi

# get log file
if [ "$2" != "" ]; then
    logfile=$2
else
    logfile="sac_logs.txt"
fi
echo "Benchmark directory : $targetDir " >>$benchLog
echo "Log file  : $logfile " >>$benchLog

# get work directory
if [ "$3" != "" ]; then
    workDir="$3"
else
    workDir="gen_files/"
fi

# get k 
if [ "$4" != "" ]; then
    k="$4"
else
    k="6"
fi

mkdir -p $workDir

# get list of .v files in target directory
i=0
benchfiles="`ls -Sr ${targetDir}c*.blif`"
spacing=( 0 2 4 6 )
echo $benchfiles

for file1 in $benchfiles
do
            echo "Processing $file1 Start time : `date`" >> $benchLog  
            b1=$(basename $file1 )
            echo "base : $b1"
            echo "$b1" >> $archeLog 
            
            
            for s in "${spacing[@]}"
            do
                python3 sac_experiment.py $file1 $workDir 64 32 $k $logfile $s &
                python3 sac_experiment.py $file1 $workDir 64 64 $k $logfile $s &
                wait 

                python3 sac_experiment.py $file1 $workDir 128 64 $k $logfile $s &
                python3 sac_experiment.py $file1 $workDir 128 128 $k $logfile $s &
                wait 
                  
                echo "Processing Finish time : `date`" >> $benchLog  
                echo "$dashSmall" >> $benchLog
            done
            
            
        
         
    i=$((i+1))
 
done

if [ "$i" == "0" ]; then
  echo "Error : .v files not found in target directory" >> $benchLog
  echo "Exiting... " >> $benchLog
  exit 1
fi

echo "" >> $benchLog
echo "$dash" >> $benchLog
echo "Benchmarking completed at `date`" >> $benchLog
echo "$dash" >> $benchLog
