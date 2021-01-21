import ROOT
import sys
import numpy as np
from DataFormats.FWLite import Events, Handle

filename = sys.argv[1]
events = Events(filename)

class Expression:
    def __init__(self, label, edmtype, eval_list):
        self.label = label
        self.edmtype = edmtype
        self.eval_list = eval_list

        self.handle = Handle(self.edmtype)

    def get(self, event):
        event.getByLabel(self.label, self.handle)
        obj = self.handle.product()
        for eval_name, eval_item in self.eval_list:
            ret = eval(eval_item)
            print("{}.{}={}".format(self.label, eval_name, ret))

expressions = []

#expressions.append(Expression(
#    "genMetTrue",
#    "vector<reco::GenMET>",
#    [("sumEt", "[o.sumEt() for o in obj]")]
#))
#
#expressions.append(Expression(
#    "pfMet",
#    "vector<reco::PFMET>",
#    [("sumEt", "[o.sumEt() for o in obj]")]
#))
#
#expressions.append(Expression(
#    "ak4TrackJets",
#    "vector<reco::TrackJet>",
#    [("pt", "[j.pt() for j in obj]")]
#))
#
#expressions.append(Expression(
#    "ak4GenJets",
#    "vector<reco::GenJet>",
#    [("pt", "[j.pt() for j in obj]"), ("eta", "[j.eta() for j in obj]"), ("phi", "[j.phi() for j in obj]")]
#))

#expressions.append(Expression(
#    "offlinePrimaryVertices",
#    "vector<reco::Vertex>",
#    [
#        ("size", "obj.size()"),
#    ]
#))
#
#expressions.append(Expression(
#    "particleFlowBlock",
#    "vector<reco::PFBlock>",
#    [
#        ("size", "sorted([o.elements().size() for o in obj])"),
#        ("elems", "sorted([[elem.type() for elem in o.elements()] for o in obj])"),
#    ]
#))

#expressions.append(Expression(
#    ("hbheprereco", ""),
#    "edm::SortedCollection<HBHERecHit,edm::StrictWeakOrdering<HBHERecHit> >",
#    [
#        ("size", "obj.size()"),
#        ("energy", "sorted([o.energy() for o in obj], reverse=True)"),
#    ]
#))

expressions.append(Expression(
    ("ecalMultiFitUncalibRecHit", "EcalUncalibRecHitsEB"),
    "edm::SortedCollection<EcalUncalibratedRecHit,edm::StrictWeakOrdering<EcalUncalibratedRecHit> >",
    [
        ("size", "obj.size()"),
        ("amplitude", "[o.amplitude() for o in obj]"),
        ("pedestal", "[o.pedestal() for o in obj]"),
        ("jitter", "[o.jitter() for o in obj]"),
        ("outOfTimeAmplitude", "[o.outOfTimeAmplitude() for o in obj]"),
        ("chi2", "[o.chi2() for o in obj]"),
    ]
))

if __name__ == "__main__":

    #get the order of event ID tuples in the file, so we can process all files
    #in the same order to account for multithreading
    evids = []
    for iev, event in enumerate(events):
        eid = event.object().id()
        eventId = (eid.run(), eid.luminosityBlock(), int(eid.event()))
        evids.append((eventId, iev))
    evids = sorted(evids, key=lambda x: x[0])

    #loop over events in a well-defined order
    for _, iev in evids:
        event.to(iev)

        eid = event.object().id()
        eventId = (eid.run(), eid.luminosityBlock(), int(eid.event()))
        print("event {}".format(eventId))

        for expr in expressions:
            expr.get(event)

