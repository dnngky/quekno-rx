from enum import Enum

from qiskit.circuit.library import CXGate, HGate

# for generation of circuits
ONE_QUBIT_GATE = HGate()
TWO_QUBIT_GATE = CXGate()

CONSEC_SWAPS_BIAS = .0 # likelihood of picking consecutive swaps for opt2 opt-type
SUBGRAPH_SIZE_STD = 10 # standard deviation of number of edges in random subgraphs
RAND_EDGES_VAR = .05 # variance of number of edges randomly sampled from subgraphs

# values of each OptType correspond to permitted target costs
class OptType(Enum):
    OPT1 = "opt1"
    OPT2 = "opt2"
    DEPTH = "depth"

class SubgraphSize(Enum):
    TOKYO = 5
    SMALL = 8
    LARGE = 16

class QBGRatio(Enum):
    TFL = 1.5
    QSE = 2.55
