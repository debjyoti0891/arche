#!/bin/bash

# This files runs mimd for all the benchmark files 
# specified by the input directory

# ./benchmark.sh benchDir timeLimit
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
echo "Benchmark directory : $targetDir " >>$benchLog

workDir="gen_files"
mkdir -p $workDir

# get list of .v files in target directory
i=0
benchfiles="`ls -Sr ${targetDir}map*.v`"
echo $benchfiles

for file1 in $benchfiles
do
    for file2 in $benchfiles
    do
        echo $file1 $file2 
        
        if [ $file1 != $file2 ]; then 
            archeInput="in_${b1}_${b2}"
            
            echo "" >> $benchLog
            echo "$dash" >> $benchLog
            echo "BenchMark Files : $file1 $file2" >> $benchLog
            echo "$dash" >> $benchLog
            

            b1=$(basename $file1 )
            echo "base : $b1"
            echo "$b1" >> $archeLog 
            
            b2=$(basename $file2 )
            echo "base : $b2"
            echo "$b2" >> $archeLog 
            
            
            echo "setlog -f logmap" > $archeInput
            echo "mimd -f $file1 $file2 -o sol_${b1}_${b2} -t $2 -md -v -cs" >> $archeInput 
            echo "quit" >> $archeInput 
            #python3 arche.py < $archeInput 
            #screen -dm -S "${b1}_${b2}"
            #screen -S ${b1}_${b2} -p 0 -X stuff '../arche.py < ${archeIn.txt}\n'
            #screen -S ${b1}_${b2} -p 0 -X stuff 'exit\n'
            ../arche.py < ${archeInput}
            #screen -dmS ${b1}_${b2} -c "../arche.py < $archeInput"
            echo "Technology mapping completed successfully."  >> $benchLog  
            
            echo "Processing Finish time : `date`" >> $benchLog  
            echo "$dashSmall" >> $benchLog
            
            trash $archeInput
            archeCount=`ps -e | grep arche | wc -l`
            while [ $archeCount -gt 3 ]
            do
                sleep 10
            done
            
        fi 
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
