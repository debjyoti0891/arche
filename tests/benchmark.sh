#!/bin/bash

# This files generates the simulation reports for all the files 
# specified by the input directory

# ./benchmark.sh benchDir timeLimit
abcInput="abcIn.txt"
archeInput="archeIn.txt"
archeLog="example.log"
statsFile="archeStat.txt"

benchLog="synthesis_benchmark.log"
reportLog="synthesis_report.log" #specified in helper.py
dash="======================================================="
dashSmall="------------------------------------------------------"

# header of benchmark.log
echo "$dash" > $benchLog
echo "Arche ReRAM Technology Mapping Benchmarking ToolSuite v1.0" >> $benchLog
echo "Author : Debjyoti Bhattacharjee"           >> $benchLog
echo "$dash" >> $benchLog
echo "Benchmarking started at `date`" >> $benchLog
echo "$dashSmall" >> $benchLog

# get target directory
if [ "$1" != "" ]; then
    targetDir=$1
else
    targetDir="`pwd`/"
fi
echo "Benchmark directory : $targetDir " >>$benchLog

workDir="gen_files"
mkdir -p $workDir
echo "$dash" >> $reportLog
echo "Starting Batch processing :  `date`" >> $reportLog
echo "$dash" >> $reportLog

# get list of .v files in target directory
i=0
for file in `ls -Sr ${targetDir}map*.v`
do
    echo "" >> $benchLog
    echo "$dash" >> $benchLog
    echo "BenchMark File : $file" >> $benchLog
    echo "$dash" >> $benchLog
    

    b=$(basename $file )
    echo "base : $b"
    # generate local file with same name but without comments
    grep -o '^[^/^/]*' "$file" > ./"$workDir/$b"
    echo "$b" >> $archeLog 
    echo "setlog -f log_$b" > $archeInput
    echo "set col $2 " >> $archeInput 
    echo "set row 100 " >> $archeInput 
    echo "read $workDir/$b" >> $archeInput 
    echo "rowsat -m -t $2 " >> $archeInput 
    echo "quit" >> $archeInput 
    #python3 arche.py < $archeInput 
    cat $archeInput > in_$b
    echo "Technology mapping completed successfully."  >> $benchLog  
    echo "Processing Finish time : `date`" >> $benchLog  
    echo "$dashSmall" >> $benchLog
    
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
