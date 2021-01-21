import sys
import os
import yaml
from collections import OrderedDict

class MyDumper(yaml.SafeDumper):
    # HACK: insert blank lines between top-level objects
    # inspired by https://stackoverflow.com/a/44284819/3786245
    def write_line_break(self, data=None):
        super().write_line_break(data)

        if len(self.indents) == 1:
            super().write_line_break()

def get_modified_packages(pr_number):
    stream = os.popen('gh pr diff {} | egrep -o "a/(.*) "'.format(pr_number))
    output = stream.read()
    lines = output.split('\n')
    lines = [line.strip() for line in lines]
    packages = ["/".join(o[2:].split("/")[:2]) for o in lines if len(o)>0]
    return list(set(packages))

def parse_release(data):
    lines = data.split('\n')
    metadatas = []
    for line in lines:
        line = line.strip()
        if len(line) > 0:
            splt = line.split()
            pr_number = splt[1][1:]
            author = splt[3][:-1]
            title = line[line.index(":")+2:]
            metadata = {}
            metadata["number"] = pr_number
            metadata["author"] = author
            metadata["title"] = title
            metadata["reco_category"] = ""
            metadata["packages"] = get_modified_packages(pr_number)
            metadatas.append(metadata)
    return metadatas

def get_reco_category(metadata):
    return ""

def prepare_release_metadata(release="CMSSW_11_2_0_pre8"):
    stream = os.popen('gh release view {} | grep reconstruction'.format(release))
    output = stream.read()
    metadatas = parse_release(output)
    print(yaml.dump(metadatas))

def format_title(title):
    title = title.replace("\n", "")
    title = title.replace(":", ",")
    if "`" in title:
        idx_tag = title.index("`")
        title = title[:idx_tag].strip()
    if "]" in title:
        idx_tag = title.index("]")
        title = title[idx_tag+1:]
    title = title.strip()
    return title

def prepare_twiki(release_yaml):
    metadata = yaml.load(open(release_yaml))
    by_category = {}
    for md in metadata:
        rc = md["reco_category"]
        if rc == "":
            raise ValueError("reco_category for PR {} not set".format(md["number"]))

        if not rc in by_category:
            by_category[rc] = []
        by_category[rc].append(md)
    
    for cat in sorted(by_category.keys()):
        line = "   * *{}*: ".format(cat)
        for md in by_category[cat]:
            line += "{} ([[https://github.com/cms-sw/cmssw/pull/{}][#{}]]), ".format(format_title(md["title"]), md["number"], md["number"])
        print(line[:-2])

def get_pr_data(pr):
    stream = os.popen('gh pr view {}'.format(pr))
    lines = stream.read().split("\n")
    title = format_title(lines[0].strip()[7:])
    labels = []
    state = ""
    author = ""
    for line in lines:
        line = line.strip()
        if line.startswith("labels"):
            labels = line.split()[1:]
            labels = [l.replace(",", "") for l in labels]
        if line.startswith("state"):
            state = line[7:]
        if line.startswith("author"):
            author = line[8:]

    packages = get_modified_packages(pr)
    return {
        "author": author,
        "number": pr,
        "title": title,
        "labels": labels,
        "state": state,
        "packages": packages,
        "reco_category": ""
    }

def get_prs_merged_since_release(release="CMSSW_11_1_4", master="CMSSW_11_1_X"):
    os.popen("git checkout {}".format(release)).read() 
    os.popen("git checkout {}".format(master)).read() 
    stream = os.popen('git log {}..{} | grep "Merge pull request"'.format(release, master))
    new_prs = stream.read().split("\n")
    all_prs = [] 
    for line in new_prs:
        spl = line.split()
        if len(spl) == 6 and spl[0] == "Merge":
            pr = int(spl[3][1:])
            #data = get_pr_data(pr)
            all_prs.append(pr)
    return all_prs

def get_prs_open(master="CMSSW_11_1_X"):
    data = os.popen("gh pr list -B {}".format(master)).read()
    prs = []
    for line in data.split("\n"):
        if len(line)>0:
            spl = line.split()
            pr = int(spl[0])
            prs.append(pr)
    return prs

def format_pr_for_yaml(pr_data):
    ret = {k: pr_data[k] for k in ["title", "author", "number", "packages", "state", "reco_category"]}
    return ret

def prepare_upcoming_release_metadata(release="CMSSW_10_6_18", master="CMSSW_10_6_X"):
    prs_merged = get_prs_merged_since_release(release=release, master=master)
    prs_open = get_prs_open(master=master)
    prs = prs_merged + prs_open
    pr_data = [get_pr_data(pr) for pr in prs]
    reco_prs = [pr for pr in pr_data if "reconstruction-pending" in pr["labels"] or "reconstruction-approved" in pr["labels"]]
    formatted_pr_data = [format_pr_for_yaml(pr) for pr in pr_data]
    print(yaml.dump(formatted_pr_data, Dumper=MyDumper, sort_keys=False))

if __name__ == "__main__":

    #prepare_upcoming_release_metadata(sys.argv[1], sys.argv[2])
    #prepare_release_metadata(sys.argv[1])
    prepare_twiki(sys.argv[1])
