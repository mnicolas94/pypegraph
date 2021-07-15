from pypegraph.node import Node


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

