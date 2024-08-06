import itertools as it
import os
import sys
import time
import warnings

from qiskit import QuantumCircuit, qasm2
from qiskit.transpiler.passes import RemoveBarriers
from tqdm import tqdm

from lib.graph import Graph
from lib.graph_utils import Tokyo, graph_from_name
from config import *
from quekno import QUEKNO

CIRCUITS_ROOT = lambda benchmark: f"out/{benchmark}/circuits"
CIRCUITS_BARRIERED_ROOT = lambda benchmark: f"out/{benchmark}/circuits_barriered"
RESULTS_ROOT = lambda benchmark: f"out/{benchmark}/results"


def benchmark_name(opt: str, archgraph: Graph):
    num_qubits = 20 if archgraph.name == "tokyo" else 53
    return f"{num_qubits}Q_{opt}_{archgraph.name.capitalize()}"

def export_circuits(
    root: str,
    barriered_root: str,
    name: str,
    circuit: QuantumCircuit,
    is_barriered: bool = True
):
    if is_barriered:
        qasm2.dump(circuit, os.path.join(barriered_root, name + ".qasm"))
        qasm2.dump(RemoveBarriers()(circuit), os.path.join(root, name + ".qasm"))
    else:
        qasm2.dump(circuit, os.path.join(CIRCUITS_ROOT, name + ".qasm"))

def export_results(
    root: str,
    name: str,
    results: dict
):
    with open(os.path.join(root, name + ".txt"), "w") as f:
        f.write(f"name: {name}\n")
        for key, val in results.items():
            if isinstance(val, float):
                val = f"{val:.3f}" # round to 3 sf
            f.write(f"{key}: {val}\n")

def main(opt: str, archgraph: Graph) -> int:

    subgraph_sizes = (SubgraphSize.TOKYO,) if archgraph.name == "tokyo" else (SubgraphSize.SMALL, SubgraphSize.LARGE)
    opt_types = (OptType.OPT1, OptType.OPT2) if opt == "gate" else (OptType.DEPTH,)
    target_costs = (0, 1, 2, 3, 4, 5, 10, 15, 20, 25) if opt == "gate" else (1, 2, 3, 4, 5, 10)
    qbg_ratios = (QBGRatio.TFL,) if opt == "gate" else (QBGRatio.TFL, QBGRatio.QSE)

    benchmark = benchmark_name(opt, archgraph)
    num_circuits = len(subgraph_sizes) * len(opt_types) * len(target_costs) * len(qbg_ratios) * 10
    prog_bar = tqdm(total = num_circuits, leave = False)

    params = it.product(subgraph_sizes, opt_types, target_costs, qbg_ratios, range(10))
    for subgraph_size, opt_type, target_cost, qbg_ratio, i in params:
        
        num_qubits = 20 if archgraph.name == "tokyo" else 53
        size = "small" if subgraph_size == SubgraphSize.SMALL else "large"
        name = f"{num_qubits}QBT_{opt}_{archgraph.name.capitalize()}_{size}_{opt_type.value}_{target_cost}_{qbg_ratio.value}_no.{i}"
        builder = QUEKNO(
            opt_type = opt_type,
            target_cost = target_cost,
            archgraph = Tokyo(),
            subgraph_size = SubgraphSize.TOKYO,
            qbg_ratio = QBGRatio.TFL
        )
        circuit, _, results = builder.run(add_barriers = True, verbose = False)

        export_circuits(
            CIRCUITS_ROOT(benchmark),
            CIRCUITS_BARRIERED_ROOT(benchmark),
            name,
            circuit,
            is_barriered = True
        )
        export_results(
            RESULTS_ROOT(benchmark),
            name,
            results
        )
        prog_bar.set_description(name, refresh = False)
        displayed = prog_bar.update()
        if not displayed:
            prog_bar.refresh()
    
    prog_bar.close()

    return num_circuits


if __name__ == "__main__":

    warnings.filterwarnings("ignore")

    if len(sys.argv) != 3:
        raise ValueError("requires opt and name")
    if (opt := sys.argv[1].lower()) not in ("gate", "depth"):
        raise ValueError("opt needs to be either 'gate' or 'depth'")
    if (name := sys.argv[2].lower()) not in ("tokyo", "rochester", "sycamore"):
        raise ValueError("name needs to be either 'tokyo', 'rochester', or 'sycamore'")
    
    t0 = time.time()
    num_circuits = main(opt, graph_from_name(name))
    t1 = time.time()

    print(f"Generated {num_circuits} circuits in {(t1 - t0):.3f} s.")
