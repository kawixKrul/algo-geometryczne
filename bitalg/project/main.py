import copy
import random

from figures import Point, Node, TriangulatedPointSet


def preprocess(points: list[Point]) -> Node:
    # preprocess the list of points into a graph

    triangulated_point_set = TriangulatedPointSet(points)

    i = 0
    previous_nodes: list[Node] = []
    while len(triangulated_point_set.triangles) > 1 or i == 0:
        # if this is the first step - cover the point set in a triangle and triangulate
        # otherwise remove independent set of points and triangulate the holes
        if i != 0:
            triangulated_point_set.remove_points()
        else:
            triangulated_point_set.cover_with_triangle()
            triangulated_point_set.triangulate()
        triangulated_point_set.visualize("step" + str(i))

        current_nodes = []
        for triangle in triangulated_point_set.triangles:
            # each triangle from current triangulation is a node
            node = Node(triangle)
            current_nodes.append(node)

            # add node as child to one of the previous nodes the area of its triangle belonged to
            for previous_node in previous_nodes:
                if triangle.contains_point(previous_node.triangle.a) or triangle.contains_point(
                        previous_node.triangle.b) or triangle.contains_point(previous_node.triangle.c):
                    node.children.append(previous_node)

        previous_nodes = current_nodes
        i += 1

    root = previous_nodes[0]
    return root


def locate_point(points: list[Point], point: Point):
    root = preprocess(points)

    curr_node = root
    if not curr_node.triangle.contains_point(point):
        return None

    children: list[Node] = curr_node.children
    while children:
        for node in children:
            if node.triangle.contains_point(point):
                curr_node = node

                if not any(pnt in root.triangle.to_tuple() for pnt in node.triangle.to_tuple()):
                    break

        children = curr_node.children

    if any(pnt in root.triangle.to_tuple() for pnt in curr_node.triangle.to_tuple()):
        return None

    return curr_node.triangle


def test(seed=None, from_x=0, to_x=10, from_y=0, to_y=10, how_many=10, search_for=None):
    if seed is not None:
        random.seed(seed)
    if search_for is None:
        search_for = Point(random.uniform(from_x, to_x), random.uniform(from_y, to_y))
    test_points = [Point(random.uniform(from_x, to_x), random.uniform(from_y, to_y)) for _ in range(how_many)]

    print("Test points:\n", test_points)
    print("Trying to find: ", search_for)

    # deepcopy since I want to use them for something later
    result = locate_point(copy.deepcopy(test_points), search_for)
    print("Result: ", result)

    # visualise
    triangulated_point_set = TriangulatedPointSet(test_points)
    triangulated_point_set.cover_with_triangle()
    triangulated_point_set.triangulate()
    triangulated_point_set.visualize(name="result", point=search_for, result_triangle=result)


trivial_points = [
    Point(5, 1),
    Point(4, 2),
    Point(5, 4),
    Point(3, 5),
    Point(6, 6)
]

test(seed=69420, search_for=Point(6, 4))