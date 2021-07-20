from pypegraph.node import Node
from pypegraph import dag


def _do_nothing(*args, **kwargs):
    return args, kwargs


def get_empty_node():
    node = Node(action=_do_nothing)
    return node


def get_only_one_output(node: Node, *args, **kwargs):
    leafs = dag.leaf_nodes(node)
    leaf = leafs[0]
    outputs = node(*args, **kwargs)
    result = outputs[leaf]
    return result


def replace_node(node: Node, replacement: Node):
    input_connections = node.input_connections
    output_connections = node.output_connections

    for input_node, configurations in input_connections.items:
        for conf in configurations:
            connection_name = conf.pop('connection_name')
            input_node.connect(replacement, connection_name, **conf)

    for output_node, configuration in output_connections.items():
        connection_name = configuration.pop('connection_name')
        replacement.connect(output_node, connection_name, **configuration)

    node.disconnect_all_inputs()
    node.disconnect_all_outputs()

