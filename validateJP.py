import uproot
import sys
import ROOT

ROOT.gROOT.SetBatch(True)

import multiprocessing
from collections import OrderedDict

def check_histograms_equal(hist1, hist2):
    ret = True
    if hist1.__class__ != hist2.__class__:
        ret = False

    if hist1.GetNbinsX() != hist2.GetNbinsX():
        ret = False

    for ibin in range(0, hist1.GetNbinsX()+1):
        if hist1.GetBinContent(ibin) != hist2.GetBinContent(ibin):
            ret = False

    return ret

def get_histogram_bin_diff(hist1, hist2):
    bin_diff = 0.0
    for ibin in range(0, hist1.GetNbinsX()+1):
        bin_diff += abs(hist1.GetBinContent(ibin) - hist2.GetBinContent(ibin))
    return bin_diff

def get_file_histograms(fname):
    fi = uproot.open(fname)
    rfi = ROOT.TFile(fname)
    histogram_names = []
    for key in fi.iterkeys(recursive=True):
        obj = rfi.Get(key)
        if isinstance(obj, ROOT.TH1F) or isinstance(obj, ROOT.TH1D):
            histogram_names.append(key)

    return histogram_names

def sanitize_name(name):
    return name.replace(" ", "").replace("/", "__").replace(";1", "")

def plot_histograms(h1, h2, outfile_name, histname, ksProb, bDiff):

    cv = ROOT.TCanvas(histname, histname)

    cv.cd()
    pH = ROOT.TPad("head","head", 0, 0.93, 1, 1)
    pH.Draw()
    pH.cd()
    pt = ROOT.TPaveText(0,0,1,1)
    pt.SetFillColor(0)
    pt.AddText(histname)
    pt.Draw()

    cv.cd()
    pD = ROOT.TPad("dis","dis", 0, 0.0, 1, 0.93)
    pD.Draw()
    pD.cd()

    #black
    h2.SetLineWidth(2)
    h2.SetLineColor(1)
    h2.SetMarkerColor(1)

    #red
    h1.SetLineColor(2)
    h1.SetMarkerColor(2)

    h1.Draw()
    h2.Draw("SAMES")

    max1 = h1.GetMaximum()
    max2 = h2.GetMaximum()
    min1 = h1.GetMinimum()
    min2 = h2.GetMinimum()
    if (max2 > max1):
        h2.SetMaximum(max2+2*abs(max2))
    if (min2 < min1):
        h2.SetMinimum(min2-2*abs(min2))

    ksPt = ROOT.TPaveText(0,0, 0.35, 0.04, "NDC")
    ksPt.SetBorderSize(0)
    ksPt.SetFillColor(0)
    ksPt.AddText("1-P(KS)={:.2f}, diffBins={:.4f}, eblk {} ered {}".format(
        1-ksProb,
        bDiff,
        h1.GetEntries(),
        h2.GetEntries()))
    ksPt.Draw()

    legend = ROOT.TLegend(pD.GetUxmin(), pD.GetUymax()-0.1, pD.GetUxmin()+0.15, pD.GetUymax())
    legend.AddEntry(h1,"this PR","l")
    legend.AddEntry(h2,"ref","l")
    legend.Draw()

    cv.SaveAs(outfile_name)

    cv.Close()

def compare_histograms(fname1, fname2, histname):
    rfi1 = ROOT.TFile(fname1)
    rfi2 = ROOT.TFile(fname2)
    hist1 = rfi1.Get(histname)
    hist2 = rfi2.Get(histname)

    is_equal = check_histograms_equal(hist1, hist2)

    if is_equal:
        ret = (histname, {})
    else:
        m1 = hist1.GetMean()
        m2 = hist2.GetMean()
        ks = hist2.KolmogorovTest(hist1)
        plot_name = "{}.png".format(sanitize_name(histname))
        ret = (histname, {
            "name": histname,
            "equal": False,
            "mean1": m1,
            "mean2": m2,
            "bin_diff": get_histogram_bin_diff(hist1, hist2),
            "ks": ks,
            "plot_name": plot_name,
        })
        plot_histograms(hist1, hist2, "plots/" + plot_name, histname, ret[1]["ks"], ret[1]["bin_diff"])

    return ret

def filter_histograms_skip(histograms, skips):
    histograms_filtered = []
    for histogram in histograms:
        skipped = False
        for skip in skips:
            if skip in histogram:
                skipped = True
                break
        if not skipped:
            histograms_filtered.append(histogram)
    return histograms_filtered

def filter_histograms_require(histograms, requires):
    histograms_filtered = []
    for histogram in histograms:
        required = False
        for req in requires:
            if req in histogram:
                required = True
                break
        if required:
            histograms_filtered.append(histogram)
    return histograms_filtered

def compare_histograms_args(args):
    return compare_histograms(*args)

def parse_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", type=int, default=8, help="number of parallel processes to use")
    parser.add_argument("--skip", type=str, action="append", default=[])
    parser.add_argument("--require", type=str, action="append", default=[])
    parser.add_argument("--fn-ref", type=str, help="reference DQM file")
    parser.add_argument("--fn-new", type=str, help="new DQM file")
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()

    histograms = get_file_histograms(args.fn_ref)
    for hist in histograms:
        print(hist)
    histograms = filter_histograms_require(histograms, args.require)
    histograms = filter_histograms_skip(histograms, args.skip)

    pool = multiprocessing.Pool(args.j)
    results = OrderedDict(
        pool.map(compare_histograms_args, [(args.fn_new, args.fn_ref, histogram) for histogram in histograms]))
    pool.close()

    discrepant_results = [(key, res) for (key, res) in results.items() if len(res)>0]
    discrepant_results_sorted = sorted(discrepant_results, key=lambda kv: kv[1]["bin_diff"])
    for histname, res in discrepant_results_sorted:
        print("{histname} bin_diff={bin_diff}".format(
            histname=res["plot_name"],
            bin_diff=res["bin_diff"]
        ))
