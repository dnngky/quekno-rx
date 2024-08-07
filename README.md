# QUEKNO: Quantum Circuits with Known Near-Optimal Cost

This repository provides the benchmark construction algorithm presented in *On constructing benchmark quantum circuits with near-optimal transformation cost* by Sanjiang Li, Xiangzhen Zhou, and Yuan Feng.

*Current quantum devices impose strict connectivity constraints on quantum circuits, making circuit transformation necessary before running logical circuits on real quantum devices. Many quantum circuit transformation (QCT) algorithms have been proposed in the past several years. This paper proposes a novel method for constructing benchmark circuits and uses these benchmark circuits to evaluate state-of-the-art QCT algorithms, including TKET from Cambridge Quantum Computing, Qiskit from IBM, and three academic algorithms SABRE, SAHS, and MCTS. These benchmarks have known near-optimal transformation costs and thus are called QUEKNO (for quantum examples with known near-optimality). Compared with QUEKO benchmarks designed by Tan and Cong (2021), which all have zero optimal transformation costs, QUEKNO benchmarks are more general and can provide a more faithful evaluation for QCT algorithms (like TKET) which use subgraph isomorphism to find the initial mapping. Our evaluation results show that SABRE can generate transformations with conspicuously low average costs on the 53-qubit IBM Q Rochester and Google's Sycamore in both gate size and depth objectives.*

## Installation

This project uses `python 3.12.4`, `qiskit 1.1.1`, and `rustworkx 0.15.1` (which comes with Qiskit). It is recommended that these packages are installed in an isolated virtual environment to avoid clashes (especially with `qiskit 1.1.1` which is not compatible with versions older than `qiskit 1.0`). If Anaconda is used, a virtual environment may be created by running the following:
```bash
$ conda create -n quekno
$ conda activate quekno
```
Then, navigate to the root directory of this repository and run:
```bash
$ sh install.sh
```
Alternatively, the user may choose to manually install the packages listed in `install.sh`.

## Benchmark construction

Benchmarks are categorised into the following packages, where `gate` and `depth` refer to gate size and depth optimisation objectives respectively:

- `20Q_gate_Tokyo`
- `20Q_depth_Tokyo`
- `53Q_gate_Rochester`
- `53Q_depth_Rochester`
- `53Q_gate_Sycamore`
- `53Q_depth_Sycamore`

Each package contains three sub-directories:

- `circuits`, which contains all constructed circuits in QASM format;
- `circuits_barriered`, which contains the same circuits but with a barrier added between every glink; and
- `results`, which contains the metadata of the circuits.

Each file in `results` comprises the following fields:

- `name`: name of the constructed circuit;
- `opt_type`: optimisation objective (`opt1`, `opt2`, or `depth`);
- `cost`: QUEKNO transformation cost (see original paper);
- `archgraph`: associated architecture graph;
- `subgraph_size`: average size (number of edges) of subgraphs across all glinks;
- `qbg_ratio`: ratio $M_1/M_2$, where $M_k$ denotes the number of $k$-qubit gates;
- `gate_size`: number of gates in the constructed circuit;
- `depth`: depth of the constructed circuit;
- `gate_cost`: incurred number of gates following routing (SWAP insertion) and decomposition (from SWAPs to CNOTs);
- `depth_cost`: incurred depth following routing and decomposition;
- `init_map`: initial permutation $\pi_1$, written in one-line notation (w.r.t. the natural ordering $0, 1, 2, \cdots, |\texttt{archgraph}| - 1$).
- `swaps`: a sequence of (edge-based) permutations $\pi_2, \cdots, \pi_{\ell + 1}$, with the $i$-th line specifying the swaps involved in the $(i + 1)$-th permutation.

To generate all benchmarks, simply run:
```bash
$ sh run.sh
```

If the user would like to generate each benchmark package individually, they may choose to run:
```bash
$ python main.py [objective] [archgraph]
```
Here, `objective = {gate, depth}` and `archgraph = {tokyo, rochester, sycamore}`.

Once generated, benchmarks may be found in `out`.

## Configurations

The file `config.py` defines a number of constants which affect the speed and output of the benchmark construction:

- `ONE_QUBIT_GATE` and `TWO_QUBIT_GATE` specify the type of gates used in the constructed circuits;
- `CONSEC_SWAP_BIAS` specifies the bias (if any) towards selecting consecutive swaps for `opt_type = OPT2`: a value $k$ indicates a $0.5 + k$ probability of selecting consecutive swaps;
- `SUBGRAPH_SIZE_STD` specifies the variance in the number of edges of randomly generated glink subgraphs: a value $\sigma$ indicates that $X \sim \mathcal N(\mu, \sigma^2)$ where $X$ is the number of edges and $\mu$ is `subgraph_size`;
- `RAND_EDGES_VAR` specifies the variance in the number of edges (2-qubit gates) randomly sampled from glink subgraphs during circuit construction: a value $k$ indicates that the number of edges sampled is $m(1 + kX)$ where $X \sim \mathcal U[1,4]$ and $m$ is the number edges in the subgraph;
- `GLINK_SEARCH_PATIENCE` specifies the number of attempts to find a strong glink-inducing permutation before moving on to another glink, i.e., generating another subgraph.
