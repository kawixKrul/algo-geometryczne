from __future__ import annotations

from math import sqrt
import numpy as np
from scipy.spatial import Delaunay

from bitalg.visualizer.main import Visualizer

EPS = 1e-14


# math

def det3points(p1: Point, p2: Point, p3: Point):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)


# data structures

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.neighbors = set()
        self.triangles = set()

    def to_tuple(self) -> (int, int):
        return self.x, self.y

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


class Triangle:
    def __init__(self, a: Point, b: Point, c: Point):
        self.a = a
        self.b = b
        self.c = c

    def to_tuple(self) -> (Point, Point, Point):
        return self.a, self.b, self.c

    def contains_point(self, point: Point) -> bool:
        # check if triangle contains point p

        det_ab = det3points(self.a, self.b, point)
        det_bc = det3points(self.b, self.c, point)
        det_ca = det3points(self.c, self.a, point)

        return (det_ab > -EPS and det_bc > -EPS and det_ca > -EPS) or (det_ab < EPS and det_bc < EPS and det_ca < EPS)

    def __str__(self):
        return str(self.a) + ", " + str(self.b) + ", " + str(self.c)

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b and self.c == other.c

    def __hash__(self):
        return hash((self.a, self.b, self.c))


class Node:
    def __init__(self, triangle: Triangle):
        self.triangle = triangle
        self.children = []

    def __str__(self):
        return "Triangle: " + str(self.triangle) + "\n" + \
               "Children: " + str([str(node) for node in self.children])

    def __eq__(self, other: Node):
        return self.triangle == other.triangle and self.children == other.children

    def __hash__(self):
        return hash((self.triangle, self.children))


class TriangulatedPointSet:
    def __init__(self, points: list[Point]):
        self.points = points
        self.triangles: set[Triangle] = set()
        self.triangle_left_point: Point = None
        self.triangle_right_point: Point = None
        self.triangle_top_point: Point = None

    def __str__(self):
        return str(self.points)

    def __eq__(self, other: TriangulatedPointSet):
        return self.points == other.points

    def __hash__(self):
        return hash(self.points)

    def triangulate(self):
        # Triangulate the point set. Resulting Triangles will be in self.triangles
        # complexity O(n log n)

        # use Delaunay triangulation and save result to self.triangles
        triangulation = Delaunay(np.array(list(map(lambda point: point.to_tuple(), self.points))))
        self.triangles.clear()
        for id0, id1, id2 in triangulation.simplices:
            self.triangles.add(Triangle(self.points[id0], self.points[id1], self.points[id2]))

        # update Point neighbours and triangles
        for triangle in self.triangles:
            triangle.a.neighbors.add(triangle.b)
            triangle.a.neighbors.add(triangle.c)
            triangle.a.triangles.add(triangle)

            triangle.b.neighbors.add(triangle.c)
            triangle.b.neighbors.add(triangle.a)
            triangle.b.triangles.add(triangle)

            triangle.c.neighbors.add(triangle.a)
            triangle.c.neighbors.add(triangle.b)
            triangle.c.triangles.add(triangle)

    def cover_with_triangle(self):
        # Cover the point set with a triangle

        lower_left = Point(min(self.points, key=lambda p: p.x).x, min(self.points, key=lambda p: p.y).y)
        upper_right = Point(max(self.points, key=lambda p: p.x).x, max(self.points, key=lambda p: p.y).y)
        self.triangle_left_point = Point(lower_left.x - (upper_right.y - lower_left.y) / sqrt(3) - EPS,
                                         lower_left.y - EPS)
        self.triangle_right_point = Point(upper_right.x + (upper_right.y - lower_left.y) / sqrt(3) + EPS,
                                          lower_left.y - EPS)
        self.triangle_top_point = Point(lower_left.x + (upper_right.x - lower_left.x) / 2,
                                        upper_right.y + (upper_right.x - lower_left.x) / 2 * sqrt(3) + EPS)
        self.points.extend([self.triangle_left_point, self.triangle_right_point, self.triangle_top_point])

    def remove_points(self):
        # delete a set of independent vertices with max degree of 8
        # complexity O(n)

        # get a set of independent vertices with max degree of 8
        # complexity O(n)
        points_to_delete = set()
        cant_delete = {self.triangle_left_point, self.triangle_right_point, self.triangle_right_point}
        for point in self.points:
            if point in cant_delete:
                continue

            if len(point.neighbors) <= 8:
                # choose vertex with degree <= 8 (at most 8 "neighbors")
                points_to_delete.add(point)

                # mark vertices connected to chosen vertex as unavailable (wouldn't be independent)
                # complexity O(1) since at most 8 neighbors
                cant_delete.update(locked_point for locked_point in point.neighbors)

        # delete points one by one
        # complexity O(n) (O(1) for each point to delete)
        for point_to_delete in points_to_delete:
            points_around: set[Point] = point_to_delete.neighbors
            triangles_to_remove: set[Triangle] = point_to_delete.triangles

            # make a hole
            self.triangles -= triangles_to_remove
            self.points.remove(point_to_delete)  # at most 8 triangles

            # update Points around the hole
            for point in points_around:  # at most 8 points around
                point.neighbors -= points_around
                point.neighbors.remove(point_to_delete)

                point.triangles -= point_to_delete.triangles

            # triangulate the hole
            # complexity O(n log n) but here n <= 8 so still O(1)
            hole = TriangulatedPointSet(list(points_around))
            hole.triangulate()
            self.triangles.update(hole.triangles)

    def visualize(self, name=None, point=None, result_triangle=None):
        vis = Visualizer()
        vis.add_point([(p.x, p.y) for p in self.points])
        for triangle in self.triangles:
            vis.add_line_segment((triangle.a.to_tuple(), triangle.b.to_tuple()))
            vis.add_line_segment((triangle.b.to_tuple(), triangle.c.to_tuple()))
            vis.add_line_segment((triangle.c.to_tuple(), triangle.a.to_tuple()))

        if point is not None:
            vis.add_point((point.x, point.y), color="red")
        if result_triangle is not None:
            vis.add_line_segment((result_triangle.a.to_tuple(), result_triangle.b.to_tuple()), color="green")
            vis.add_line_segment((result_triangle.b.to_tuple(), result_triangle.c.to_tuple()), color="green")
            vis.add_line_segment((result_triangle.c.to_tuple(), result_triangle.a.to_tuple()), color="green")

        vis.show()
        if name is not None:
            vis.save(name + ".png")

