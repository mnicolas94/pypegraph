from typing import Generator

from pypegraph.node import Node


def traverse_depth_first(node: Node) -> Generator:
    """
    Traverse a directed acyclic graph using depth-first search.
    :param node: first node of the graph
    :return: a list with the nodes in depth-first order.
    """
    visited = [node]
    yield node

    childs = node.output_connections
    check_list = list(childs.keys())

    while len(check_list) > 0:
        next_node = check_list.pop(0)
        if next_node not in visited:
            visited.append(next_node)
            yield next_node
            childs = next_node.output_connections
            childs_nodes = list(childs.keys())
            for i, child_node in enumerate(childs_nodes):
                check_list.insert(i, child_node)


def traverse_breadth_first(node: Node) -> Generator:
    """
    Traverse a directed acyclic graph using breadth-first search.
    :param node: first node of the graph
    :return: a list with the nodes in breadth-first order.
    """
    visited = [node]
    yield node

    childs = node.output_connections
    check_queue = list(childs.keys())

    while len(check_queue) > 0:
        next_node = check_queue.pop(0)
        if next_node not in visited:
            visited.append(next_node)
            yield next_node
            childs = next_node.output_connections
            childs_nodes = list(childs.keys())
            for child_node in childs_nodes:
                check_queue.append(child_node)


def traverse_connections_depth_first(node: Node) -> Generator:
    visited = []

    check_list = []
    childs = list(node.output_connections.keys())
    for child in childs:
        check_list.append((node, child))

    while len(check_list) > 0:
        next_connection = check_list.pop(0)
        if next_connection not in visited:
            visited.append(next_connection)
            yield next_connection
            n1, n2 = next_connection
            childs = n2.output_connections
            childs_nodes = list(childs.keys())
            for i, child_node in enumerate(childs_nodes):
                check_list.insert(i, (n2, child_node))


def traverse_connections_breadth_first(node: Node) -> Generator:
    visited = []

    check_list = []
    childs = list(node.output_connections.keys())
    for child in childs:
        check_list.append((node, child))

    while len(check_list) > 0:
        next_connection = check_list.pop(0)
        if next_connection not in visited:
            visited.append(next_connection)
            yield next_connection
            n1, n2 = next_connection
            childs = n2.output_connections
            childs_nodes = list(childs.keys())
            for i, child_node in enumerate(childs_nodes):
                check_list.append((n2, child_node))


def leaf_nodes(node: Node):
    nodes = traverse_depth_first(node)

    leafs = []
    for n in nodes:
        outputs_count = n.output_connections_count
        if outputs_count == 0:
            leafs.append(n)
    return leafs


def print_pipeline_depth_first(node: Node) -> str:
    connections = traverse_connections_depth_first(node)
    string = ''
    for connection in connections:
        n1, n2 = connection
        s = f"{n1} -> {n2}"
        string += f'{s}\n'
        print(s)
    return string


def print_pipeline_breadth_first(node: Node) -> str:
    connections = traverse_connections_breadth_first(node)
    string = ''
    for connection in connections:
        n1, n2 = connection
        s = f"{n1} -> {n2}"
        string += f'{s}\n'
        print(s)
    return string
