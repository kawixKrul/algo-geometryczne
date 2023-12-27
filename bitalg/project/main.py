from figures import Point, Triangle, Node, Line, Polygon


def locate_point(points: list[Point], point: Point):
    # most of the actual algorithm is to build the data structure
    # for testing purposes, data structure is precomputed

    curr_node = root
    if not curr_node.triangle.contains_point(point):
        return None

    children: list[Node] = curr_node.children
    print(children)
    while children:
        for node in children:
            if node.triangle.contains_point(point):
                curr_node = node
                break

        children = curr_node.children

    return curr_node.triangle  # or something else idk


# test triangle from https://www.iue.tuwien.ac.at/phd/fasching/node82.html

"""points = [
    Point(0, 0),
    Point(5, 1),
    Point(10, 0),
    Point(4, 3),
    Point(5, 4),
    Point(3, 5),
    Point(6, 6),
    Point(5, 10)
]

triangles = [
    Triangle(points[1], points[2], points[4]),
    Triangle(points[2], points[4], points[6]),
    Triangle(points[2], points[6], points[7]),
    Triangle(points[5], points[6], points[7]),
    Triangle(points[4], points[5], points[6]),
    Triangle(points[3], points[4], points[5]),
    Triangle(points[0], points[3], points[5]),
    Triangle(points[0], points[1], points[3]),
    Triangle(points[1], points[3], points[4]),

    Triangle(points[2], points[4], points[7]),
    Triangle(points[4], points[5], points[7]),
    Triangle(points[1], points[4], points[5]),
    Triangle(points[0], points[1], points[4]),

    Triangle(points[0], points[4], points[7]),
    Triangle(points[0], points[2], points[4]),

    Triangle(points[0], points[2], points[7]),
]"""

"""nodes = [Node(triangles[i]) for i in range(9)]

# nodes[0].children.append(nodes[0])
nodes.append(Node(triangles[9], [nodes[1], nodes[2], nodes[3], nodes[4]]))
nodes.append(Node(triangles[10], [nodes[3], nodes[4]]))
nodes.append(Node(triangles[11], [nodes[5], nodes[6]]))
nodes.append(Node(triangles[12], [nodes[5], nodes[6], nodes[7], nodes[8]]))

# nodes[9].children.append(nodes[9])
nodes.append(Node(triangles[13], [nodes[10], nodes[11]]))
nodes.append(Node(triangles[14], [nodes[0], nodes[12]]))

nodes.append(Node(triangles[15], [nodes[9], nodes[13], nodes[14]]))

root = nodes[15]"""
root = Node(None, [])



#print(locate_point([], Point(4, 5)))


points = [
    #Point(0, 0),
    Point(5, 1),
    #Point(10, 0),
    Point(4, 2),
    Point(5, 4),
    Point(3, 5),
    Point(6, 6),
    #Point(5, 10)
]

lines = [
    Line(points[0], points[1]),
    Line(points[1], points[2]),
    Line(points[2], points[3]),
    Line(points[3], points[4]),
    Line(points[4], points[0]),
    Line(points[2], points[4]),
    Line(points[2], points[0])
]

test_poly = Polygon(points=points, lines=lines)
test_poly.visualize()

triangle = test_poly.cover_with_triangle()
triangle.visualize()

triangle = triangle.remove_point_with_highest_lines()
triangle.visualize()

triangle = triangle.remove_point_with_highest_lines()
triangle.visualize()

triangle = triangle.remove_point_with_highest_lines()
triangle.visualize()

triangle = triangle.remove_point_with_highest_lines()
triangle.visualize()

triangle = triangle.remove_point_with_highest_lines()
triangle.visualize()
