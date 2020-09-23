#include "TString.h"
#include <iostream>

void validate(TString step, TString file, TString refFile, TString r="RECO", bool SHOW=false, TString sr="");

int main(int argc, const char** argv) {
  if (argc != 4) {
    std::cerr << "./validate new.root old.root {all|jets|pf}" << std::endl;
  } else {
    validate(argv[3], argv[1], argv[2]);
  }
}
