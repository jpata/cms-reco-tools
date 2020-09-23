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

#run the reference
scram p -n orig CMSSW $CMSSW
cd orig
eval `scramv1 runtime -sh`
runTheMatrix.py -l $WORKFLOW --command="-n $NUMEVENTS --nThreads $THREADS"
cd ..

#get the PR, compile
scram p -n new CMSSW $CMSSW
cd new
eval `scramv1 runtime -sh`
git cms-merge-topic --unsafe $TAG
git cms-checkdeps -a >& dep.log 
scram b -j $THREADS >& abuild.log

#copy the reference workflow
cp -R ../orig/$WORKFLOW_* ./

#rerun only RECO part
cd $WORKFLOW
cmsRun step3_RAW2DIGI_L1Reco_RECO_RECOSIM_EI_PAT_VALIDATION_DQM.py > step4.log
cmsRun step4_HARVESTING.py >& step4.log
cd ../..
 
#run JR comparison
mkdir comparisonJR
cd comparisonJR
~/tools/validate ../new/$WORKFLOW_*/step3.root ../orig/$WORKFLOW_*/step3.root all

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
