from bitalg.project.figures import Polygon
from networkx import DiGraph, Graph


def kirkaptrick(division: list[Polygon]):
    layer  = []
    digraph = DiGraph()

