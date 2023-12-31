from bitalg.project.figures import TriangulatedPointSet
from networkx import DiGraph, Graph


def kirkaptrick(division: list[TriangulatedPointSet]):
    layer  = []
    digraph = DiGraph()

