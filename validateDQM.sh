#!/bin/bash


baseA=$1
baseB=$2
diffN=$3
inList=$4
lMod=$5
dMod=$6

patt=$7
pattE=$8

if [ "x${dMod}" == "x" ]; then
    echo 6 parameters are expected on input
    exit 17
fi

fLock=lastlistDQM_${diffN}.txt
if [ -f "${fLock}" ]; then 
    echo "${fLock} exists: can't run two comparisons of the same ${diffN}"
    exit 17
fi

cWD=`pwd`
export pidList=""
echo Start processing at `date`
grep root ${inList} | grep -v "#" | while read -r dsN fNP procN procR comm; do 
    fN=`echo ${baseA}/${fNP} | cut -d" " -f1 | sed -e "s?^${baseA}/??g"`
    wfDirA=`echo ${baseA}/${fN} | sed -e 's?/[^/]*root??g'`
    dqmA=`find -L ${wfDirA} -maxdepth 1 -name DQM_V\*.root | tail -1 `
    [ "x${dqmA}" == "x" ] && echo "Missing DQM file in ${wfDirA}" && continue
    wfDirB=`echo ${baseB}/${fN} | sed -e 's?/[^/]*root??g'`
    dqmB=`find -L ${wfDirB} -maxdepth 1 -name DQM_V\*.root | tail -1 `
    [ "x${dqmB}" == "x" ] && echo "Missing DQM file in ${wfDirB}" && continue
    [ "x${procN}" == "xNANO" ] && echo "Skip map entry with .root process NANO; NOT SUPPORTED YET" && continue

    extN=dqm_${diffN}_${dsN}
    mkdir -p ${extN}
    cd ${cWD}/${extN}
    
    echo "Will compare ${dqmA} (red) to ${dqmB} (black) in ${cWD}/${extN} with lMod ${lMod} dmod ${dMod} patt ${patt} pattE ${pattE}"
    echo "Now in `pwd`"

    fO=${extN}_${lMod}_${dMod}.ps

    ~/tools/makeDiff.sh ${dqmB} ${dqmA} ${fO} ${lMod} ${dMod} "${patt}" "${pattE}" >& ${fO}.log &

    pidList=${pidList}" "${!}
    export pidList
    echo $pidList
    nRunning=`ps -p $pidList | grep -c "^[ ]*[1-9]"`
    while ((nRunning > 10 )); do  
	nRunning=`ps -p $pidList | grep -c "^[ ]*[1-9]"`
#	echo $nRunning "still above 5 -> sleep 10 "
	sleep 10
    done
    cd ${cWD}
    echo $pidList > ${fLock}
done
allPids=`cat ${fLock}`
nRunning=1
while (( nRunning > 0 )); do
    nRunning=`ps -p $allPids | grep -c "^[ ]*[1-9]"`
#    echo $nRunning
    sleep 10
done

rm ${fLock}
echo done at `date`
