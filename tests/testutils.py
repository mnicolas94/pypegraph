from pypegraph.node import Node


def get_simple_graph():
	n1 = Node(lambda: print('node 1'), name='n1')
	n2 = Node(lambda: print('node 2'), name='n2')
	n3 = Node(lambda: print('node 3'), name='n3')
	n4 = Node(lambda: print('node 4'), name='n4')
	n5 = Node(lambda: print('node 5'), name='n5')
	n6 = Node(lambda: print('node 6'), name='n6')
	n7 = Node(lambda: print('node 7'), name='n7')

	n1 = n1 | n2 | n3 | n4
	n2 |= n5
	n3 |= n5
	n4 |= n6
	n5 |= n6 | n7
	n5 |= n7

	return n1, [n1, n2, n3, n4, n5, n6, n7]


def get_graph():
	n1 = Node(lambda: print('node 1'), name='n1')
	n2 = Node(lambda: print('node 2'), name='n2')
	n3 = Node(lambda: print('node 3'), name='n3')
	n4 = Node(lambda: print('node 4'), name='n4')
	n5 = Node(lambda: print('node 5'), name='n5')
	n6 = Node(lambda: print('node 6'), name='n6')
	n7 = Node(lambda: print('node 7'), name='n7')

	n1 = n1 | n2 | n3 | n4
	n2 |= n5
	n3 |= n5
	n4 |= n6
	n5 |= n6 | n7
	n5 |= n7

	return n1, [n1, n2, n3, n4, n5, n6, n7]
