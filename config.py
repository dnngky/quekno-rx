from qiskit.circuit.library import CXGate, HGate

ONE_QUBIT_GATE = HGate() # one-qubit gate type in generated circuit
TWO_QUBIT_GATE = CXGate() # two-qubit gate type in generated circuit

CONSEC_SWAPS_BIAS = .0 # likelihood of picking consecutive swaps for opt2 opt-type
SUBGRAPH_SIZE_STD = 10 # standard deviation of number of edges in random subgraphs
RAND_EDGES_VAR = .05 # variance of number of edges randomly sampled from subgraphs

GLINK_SEARCH_PATIENCE = 10 # number of attempts to find strong glink before regenerating subgraph
