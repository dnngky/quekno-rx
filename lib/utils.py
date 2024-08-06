from typing import Iterable, Optional

from .graph import Graph
from .graph_data import Edge


class singleton:
    """
    Singleton decorator (for Graph objects).
    """
    objs = {}

    def __init__(self, cls):
        self.cls = cls

    def __call__(self, *args) -> Graph:
        if self.cls not in singleton.objs:
            obj = object.__new__(self.cls)
            obj.__init__(*args)
            singleton.objs[self.cls] = obj
        return singleton.objs[self.cls]


def is_disjoint(edges: Iterable[Optional[Edge]]) -> bool:
    """
    Check whether the given collection of edges is disjoint.

    Params:
    - `edges`: an iterable collection of edges

    Returns:
    - True if `edges` is (pairwise) disjoint.
    """
    nodes = [node for edge in edges for node in edge if not edge.is_null]
    return len(nodes) == len(set(nodes)) # disjoint if no duplicates
