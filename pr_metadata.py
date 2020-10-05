import sys
import os
import yaml
from collections import OrderedDict

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

def prepare_metadata(release):
    stream = os.popen('gh release view {} | grep reco'.format(release))
    output = stream.read()
    metadatas = parse_release(output)
    print(yaml.dump(metadatas))

def format_title(title):
    idx_tag = title.index("`")
    title = title[:idx_tag].strip()
    idx_tag = title.index("]")
    title = title[idx_tag+1:]
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

if __name__ == "__main__":
    
    #prepare_metadata(sys.argv[1])
    prepare_twiki(sys.argv[1])
