from pypegraph.node import Node


def subscriptable_filter_node(key):
	node = Node(action=lambda subscriptable: subscriptable[key])
	return node
