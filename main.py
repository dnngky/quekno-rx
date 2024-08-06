import itertools as it
import os
import sys
import time
import warnings

from qiskit import QuantumCircuit, qasm2
from qiskit.transpiler.passes import RemoveBarriers
from tqdm import tqdm

from lib.graph_utils import Tokyo, graph_from_name
from lib.utils import *
from config import *
from quekno import QUEKNO

CIRCUITS_ROOT = lambda benchmark: f"out/{benchmark}/circuits"
CIRCUITS_BARRIERED_ROOT = lambda benchmark: f"out/{benchmark}/circuits_barriered"
RESULTS_ROOT = lambda benchmark: f"out/{benchmark}/results"


def benchmark_name(opt: str, archgraph: Graph):
    return f"{archgraph.num_nodes}Q_{opt}_{archgraph.name.capitalize()}"

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
        qasm2.dump(circuit, os.path.join(root, name + ".qasm"))

def export_results(
    root: str,
    name: str,
    results: dict
):
    with open(os.path.join(root, name + ".txt"), "w") as f:
        f.write(f"name: {name}\n")
        for key, val in results.items():
            if key == "build_time":
                pass
            elif key == "swaps":
                f.write(f"{key}:\n")
                for swap_seq in val:
                    f.write(", ".join(map(str, swap_seq)) + '\n')
            else:
                val = f"{val:.3f}" if isinstance(val, float) else val # round to 3 sf
                f.write(f"{key}: {val}\n")

def main(objective: str, archgraph: Graph) -> int:

    subgraph_sizes = (SubgraphSize.TOKYO,) if isinstance(archgraph, Tokyo) else (SubgraphSize.SMALL, SubgraphSize.LARGE)
    opt_types = (OptType.OPT1, OptType.OPT2) if objective == "gate" else (OptType.DEPTH,)
    target_costs = (0, 1, 2, 3, 4, 5, 10, 15, 20, 25) if objective == "gate" else (1, 2, 3, 4, 5, 10)
    qbg_ratios = (QBGRatio.TFL,) if objective == "gate" else (QBGRatio.TFL, QBGRatio.QSE)

    benchmark = benchmark_name(objective, archgraph)
    num_circuits = len(subgraph_sizes) * len(opt_types) * len(target_costs) * len(qbg_ratios) * 10
    prog_bar = tqdm(total = num_circuits, leave = False)

    params = it.product(subgraph_sizes, opt_types, target_costs, qbg_ratios, range(10))
    for subgraph_size, opt_type, target_cost, qbg_ratio, i in params:
        
        size = "small" if subgraph_size == SubgraphSize.SMALL else "large"
        opt = "opt" if opt_type.value == OptType.DEPTH else opt_type.value
        name = f"{benchmark}_{size}_{opt}_{target_cost}_{qbg_ratio.value}_no.{i}"
        builder = QUEKNO(
            opt_type = opt_type,
            target_cost = target_cost,
            archgraph = archgraph,
            subgraph_size = subgraph_size,
            qbg_ratio = qbg_ratio
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
    if (objective := sys.argv[1].lower()) not in ("gate", "depth"):
        raise ValueError("obj needs to be either 'gate' or 'depth'")
    if (archgraph := sys.argv[2].lower()) not in ("tokyo", "rochester", "sycamore"):
        raise ValueError("archgraph needs to be either 'tokyo', 'rochester', or 'sycamore'")
    
    t0 = time.time()
    num_circuits = main(objective, graph_from_name(archgraph))
    t1 = time.time()

    print(f"[{objective}_{archgraph}] Generated {num_circuits} circuits in {(t1 - t0):.3f} s.")
