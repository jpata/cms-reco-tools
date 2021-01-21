#!/bin/bash
NTHREADS=4

echo "started QCD wf 11671.0"
runTheMatrix.py -l 11671.0 -w upgrade --command="--nThreads $NTHREADS -n 600 --customise Validation/Performance/TimeMemoryInfo.py --lazy_download" >& run11671.0_600.log &

echo "started TTbar PU 25ns wf 11834.0"
runTheMatrix.py -l 11834.0 -w upgrade --command="--nThreads $NTHREADS -n 100 --customise Validation/Performance/TimeMemoryInfo.py --lazy_download" >& run11834.0_100.log &

echo "started QCD 3TeV wf 11630.0"
runTheMatrix.py -l 11630.0 -w upgrade --command="--nThreads $NTHREADS -n 400 --customise Validation/Performance/TimeMemoryInfo.py --lazy_download" >& run11630.0_400.log &

#if [ "x${1}" == "xALL" ]; then 
#    echo "started 2 e/2 gamma/2 mu guns: 10802.0,10803.0,10804.0,10805.0,10807.0,10809.0"
#    runTheMatrix.py -l 10802.0,10803.0,10804.0,10805.0,10807.0,10809.0 -w upgrade --useInput all --command="-n 1000 --lazy_download" -j 12 >& runGuns2018.log &
#fi
