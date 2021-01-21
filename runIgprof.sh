#!/bin/bash

pset=$1

igprof -pp -z -o ig.gz -t cmsRun cmsRun $pset 
igprof-analyse --sqlite -v --demangle --gdb ig*.gz > ig.txt
python ~/tools/fix-igprof-sql.py ig.txt > ig_fixed.txt
sqlite3 ig_cpu.sql3 < ig_fixed.txt

#add --customise Validation/Performance/IgProfInfo.customise
#igprof -mp -d -o ig.gz -t cmsRunGlibC cmsRunGlibC $pset 
#igprof-analyse --sqlite -v --demangle --gdb -r MEM_LIVE IgProf.49.gz > ig.txt
#python ~/tools/fix-igprof-sql.py ig.txt > ig_fixed.txt
#sqlite3 ig_mem.sql3 < ig_fixed.txt

