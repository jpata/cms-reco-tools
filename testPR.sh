#!/bin/bash
set -e

CMSSW=CMSSW_11_2_X_2020-09-21-1100
TAG=OzAmram:CR_local_error_bugfix
PR=31469_2
WORKFLOW=10859.0
THREADS=8
NUMEVENTS=100

cd ~/reco
mkdir -p $PR
cd $PR


#run the PR
scram p -n new CMSSW $CMSSW
cd new
eval `scramv1 runtime -sh`
git cms-merge-topic --unsafe $TAG
git cms-checkdeps -a >& dep.log 
scram b -j $THREADS >& abuild.log 
runTheMatrix.py -l $WORKFLOW --command="-n $NUMEVENTS --nThreads $THREADS"

#run the reference
cd ..
scram p -n orig CMSSW $CMSSW
cd orig
eval `scramv1 runtime -sh`
runTheMatrix.py -l $WORKFLOW --command="-n $NUMEVENTS --nThreads $THREADS"
