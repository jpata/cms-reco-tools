#!/bin/bash
set -e

CMSSW=CMSSW_11_3_X_2021-01-28-2300
TAG=hatakeyamak:SwitchFromSimPFToPFTICL
PR=32766
WORKFLOW=4.53
THREADS=1
NUMEVENTS=100

cd ~/reco
mkdir -p $PR
cd $PR

#run the reference
scram p -n orig CMSSW $CMSSW
cd orig
eval `scramv1 runtime -sh`

#~/tools/extendedTests2021.sh
#runTheMatrix.py -l $WORKFLOW --command="-n $NUMEVENTS --nThreads $THREADS"

cd ..

#get the PR, compile
scram p -n new CMSSW $CMSSW
cd new
eval `scramv1 runtime -sh`
git cms-merge-topic --unsafe $TAG
git cms-checkdeps -a >& dep.log 
scram b -j $THREADS >& abuild.log

~/tools/extendedTests2021.sh

#copy the reference workflow
cp -R ../orig/$WORKFLOW_* ./

rerun only RECO part
cd $WORKFLOW_*
cmsRun step3_*.py >& step3_*.log
cmsRun step4_*.py >& step4_*.log
cd ../..

#run JR comparison (precompiled using validate_main.cpp && Makefile)
mkdir comparisonJR
cd comparisonJR
~/tools/validate ../new/$WORKFLOW_*/step3.root ../orig/$WORKFLOW_*/step3.root all > log

#run DQM comparison (multithreaded plots)
cd ..
mkdir comparisonDQM
cd comparisonDQM
mkdir plots
python ~/tools/validateJP.py --fn-new ../new/$WORKFLOW_*/DQM_*.root --fn-ref ../orig/$WORKFLOW_*/DQM*.root -j $THREADS \
  --require CorrOverGen --require GenMETTrue > log

#run an event-by-event diff using FWLite
cd ..
mkdir comparisonFWLite
cd comparisonFWLite
python ~/tools/fwlite_diff.py ../new/$WORKFLOW_*/step3.root > new.txt
python ~/tools/fwlite_diff.py ../orig/$WORKFLOW_*/step3.root > orig.txt 
