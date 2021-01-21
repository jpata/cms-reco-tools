import os, sys
import numpy as np

ret = {}
fi = open(sys.argv[1])
for line in fi.readlines():
    line = line.strip()
    if "TimeModule>" in line:
        spl = line.split()
        module = spl[-2]
        t = float(spl[-1])
        if not module in ret:
            ret[module] = []
        ret[module].append(t)
for k, vals in ret.items():
    print("{}, avg {:.1f} +- {:.1f} ms, {:.1f} ms total".format(k, 1000.0*np.mean(vals), 1000.0*np.std(vals), 1000.0*np.sum(vals)))
