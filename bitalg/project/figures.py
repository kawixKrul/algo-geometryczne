from __future__ import annotations
from functools import reduce
from bitalg.visualizer.main import Visualizer
from collections import Counter

EPS = 1e-14


# math

def det3points(p1: Point, p2: Point, p3: Point):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y)


# data structures

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __gt__(self, other):
        if self.x != other.x:
            return self.x - other.x
        return self.y - other.y


class Triangle:
    def __init__(self, a: Point, b: Point, c: Point):
        if a > b:
            a, b = b, a
        if a > c:
            a, c = c, a
        if b > c:
            b, c = c, b

        self.a = a
        self.b = b
        self.c = c

    def __str__(self):
        return str(self.a) + ", " + str(self.b) + ", " + str(self.c)

    def contains_point(self, point: Point):
        det_ab = det3points(self.a, self.b, point)
        det_bc = det3points(self.b, self.c, point)
        det_ca = det3points(self.c, self.a, point)

        return (det_ab > -EPS and det_bc > -EPS and det_ca > -EPS) or (det_ab < EPS and det_bc < EPS and det_ca < EPS)

    def __eq__(self, other):
        return self.a == other.a or self.b == other.b or self.c == other.c

    def __hash__(self):
        return hash((self.a, self.b, self.c))


class Node:
    def __init__(self, triangle: Triangle, children: list[Node] = None):
        if children is None:
            children = []
        self.triangle = triangle
        self.children = children

    def __str__(self):
        return "Triangle: " + str(self.triangle) + "\n" + \
               "Children: " + str([str(node) for node in self.children])

    def __eq__(self, other: Node):
        return self.triangle == other.triangle and self.children == other.children

    def __hash__(self):
        return hash((self.triangle, self.children))


class Triangulation:
    def __init__(self, triangles: list[Triangle] = None):
        self.triangles = []


class Line:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end

    def __str__(self):
        return f'Line({self.start}, {self.end})'

    def __repr__(self):
        return f'Line({self.start}, {self.end})'

    def __contains__(self, item):
        return item == self.start or item == self.end

    def other(self, point: Point):
        if point == self.start:
            return self.end
        if point == self.end:
            return self.start
        return None

    def orientation(self, p):
        """
        Funkcja zwracająca orientację trójki punktów (self.start, self.end, p)
        -1: Przeciwnie do ruchu zegara
        0: Punkty są współliniowe
        1: Zgodnie z ruchem zegara
        """
        val = (self.end.y - self.start.y) * (p.x - self.end.x) - (self.end.x - self.start.x) * (p.y - self.end.y)
        if val == 0:
            return 0
        return 1 if val > 0 else -1

    def on_segment(self, p):
        """
        Funkcja sprawdzająca, czy punkt p leży na odcinku self
        """
        return (min(self.start.x, self.end.x) <= p.x <= max(self.start.x, self.end.x) and
                min(self.start.y, self.end.y) <= p.y <= max(self.start.y, self.end.y))

    def intersect(self, other):
        """
        Funkcja sprawdzająca, czy linie self i other się przecinają
        """
        if self.start == other.start or self.start == other.end or self.end == other.start or self.end == other.end:
            return False

        o1 = self.orientation(other.start)
        o2 = self.orientation(other.end)
        o3 = other.orientation(self.start)
        o4 = other.orientation(self.end)

        if o1 != o2 and o3 != o4:
            return True

        if o1 == 0 and self.on_segment(other.start):
            return True

        if o2 == 0 and self.on_segment(other.end):
            return True

        if o3 == 0 and other.on_segment(self.start):
            return True

        if o4 == 0 and other.on_segment(self.end):
            return True

        return False


class Polygon:
    def __init__(self, points: list[Point], triangulation: Triangulation = None, lines: list[Line] = None, llp: Point = None, lrp: Point = None, tlp: Point = None):
        self.points = points
        self.triangulation = triangulation
        self.lines = lines
        self.llp = llp
        self.lrp = lrp
        self.tlp = tlp

    def __str__(self):
        return str(self.points)

    def __eq__(self, other: Polygon):
        return self.points == other.points

    def __hash__(self):
        return hash(self.points)

    def convex_hull(self) -> list[Point]:
        """
        Return the convex hull of the given points.
        """
        L, R, S = -1, 1, 0

        def cmp(a, b) -> int:
            return (a > b) - (a < b)

        def turn(p: Point, q: Point, r: Point) -> int:
            return cmp((q.x - p.x) * (r.y - p.y) - (r.x - p.x) * (q.y - p.y), 0)

        def left_turn(hull: list[Point], r: Point) -> list[Point]:
            while len(hull) > 1 and turn(hull[-2], hull[-1], r) != L:
                hull.pop()
            if not hull or hull[-1] != r:
                hull.append(r)
            return hull

        points = self.points.copy()
        points = sorted(points, key=lambda p: (p.x, p.y))
        lower = reduce(left_turn, points, [])
        upper = reduce(left_turn, reversed(points), [])
        return lower.extend(upper[i] for i in range(1, len(upper) - 1)) or lower

    def cover_with_triangle(self) -> Polygon:
        hull = self.convex_hull()
        lower_left = Point(min(self.points, key=lambda p: p.x).x, min(self.points, key=lambda p: p.y).y)
        upper_right = Point(max(self.points, key=lambda p: p.x).x, max(self.points, key=lambda p: p.y).y)
        triangle_left_point = Point((lower_left.x - 1)*-2, (lower_left.y - 1)*2)
        triangle_right_point = Point((upper_right.x + 1)*2, (lower_left.y - 1)*2)
        triangle_top_point = Point((lower_left.x + upper_right.x) / 2, (upper_right.y + 1)*2)
        new_points = [triangle_left_point, triangle_right_point, triangle_top_point] + self.points.copy()
        new_lines = [Line(triangle_left_point, triangle_right_point), Line(triangle_left_point, triangle_top_point),
                     Line(triangle_right_point, triangle_top_point)] + self.lines.copy()
        # link convex hull points with outer triangle points
        for p in hull:
            llp = Line(triangle_left_point, p)
            flag = True
            for l in self.lines+new_lines:
                if llp.intersect(l):
                    flag = False
            if flag:
                new_lines.append(llp)
            rlp = Line(triangle_right_point, p)
            flag = True
            for l in self.lines+new_lines:
                if rlp.intersect(l):
                    flag = False
            if flag:
                new_lines.append(rlp)
            tlp = Line(triangle_top_point, p)
            flag = True
            for l in self.lines+new_lines:
                if tlp.intersect(l):
                    flag = False
            if flag:
                new_lines.append(tlp)

        # link convex hull points with each other to eliminate holes
        for i in range(len(hull)):
            new_lines.append(Line(hull[i], hull[(i+1) % len(hull)]))

        return Polygon(points=new_points, triangulation=self.triangulation, lines=self.lines.copy()+new_lines, llp=triangle_left_point, lrp=triangle_right_point, tlp=triangle_top_point)

    def remove_point_with_highest_lines(self) -> Polygon:
        """
        Funkcja usuwająca punkt o największej liczbie linii
        """
        lines = [l for l in self.lines if self.lrp not in l and self.llp not in l and self.tlp not in l]
        max_lines = Counter(l.start for l in lines)+Counter(l.end for l in self.lines)
        max_point = max_lines.most_common(1)[0][0]
        uncovered_lines = [l for l in self.lines if max_point in l]
        uncovered_points = set([l.other(max_point) for l in uncovered_lines]) - {self.lrp, self.llp, self.tlp}
        new_lines = [l for l in self.lines if max_point not in l]
        for p in uncovered_points:
            llp = Line(self.llp, p)
            flag = True
            for l in new_lines:
                if llp.intersect(l):
                    flag = False
            if flag:
                new_lines.append(llp)
            rlp = Line(self.lrp, p)
            flag = True
            for l in new_lines:
                if rlp.intersect(l):
                    flag = False
            if flag:
                new_lines.append(rlp)
            tlp = Line(self.tlp, p)
            flag = True
            for l in new_lines:
                if tlp.intersect(l):
                    flag = False
            if flag:
                new_lines.append(tlp)
        new_points = [p for p in self.points if p != max_point]
        return Polygon(points=new_points, triangulation=self.triangulation, lines=new_lines, llp=self.llp, lrp=self.lrp, tlp=self.tlp)

    def retriangulate(self, points: list[Point]) -> list[Line]:
        new_lines = []
        for p in points:
            llp = Line(self.llp, p)
            flag = True
            for l in self.lines+new_lines:
                if llp.intersect(l):
                    flag = False
            if flag:
                new_lines.append(llp)
            rlp = Line(self.lrp, p)
            flag = True
            for l in self.lines+new_lines:
                if rlp.intersect(l):
                    flag = False
            if flag:
                new_lines.append(rlp)
            tlp = Line(self.tlp, p)
            flag = True
            for l in self.lines+new_lines:
                if tlp.intersect(l):
                    flag = False
            if flag:
                new_lines.append(tlp)
        return new_lines

    def visualize(self):
        vis = Visualizer()
        vis.add_point([(p.x, p.y) for p in self.points])
        vis.add_line_segment([((l.start.x, l.start.y), (l.end.x, l.end.y)) for l in self.lines])
        vis.show()
