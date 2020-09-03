#!/bin/bash
set -e

CMSSW=CMSSW_11_2_X_2020-08-03-2300
TAG=guitargeek:PFElecTkProducer_1
PR=30992

cd ~/work/reco
mkdir -p $PR
cd $PR

scram p -n orig CMSSW $CMSSW
scram p -n new CMSSW $CMSSW
cd new

eval `scramv1 runtime -sh`
git cms-merge-topic --unsafe $TAG
git cms-checkdeps -a >& dep.log 
scram b -j 8 >& abuild.log 
~/tools/buildQA.sh
