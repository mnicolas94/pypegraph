from pypegraph import dag
from pypegraph.node import Node
import unittest
from tests import testutils


class TestDag(unittest.TestCase):

    def setUp(self):
        super().setUp()

    def test_whenTraverseDepth_nodesOrderIsCorrect(self):
        # arrange
        graph, (n1, n2, n3, n4, n5, n6, n7) = self.get_graph()

        # act
        nodes = dag.traverse_depth_first(graph)
        nodes = list(nodes)

        # assert
        expected = [n1, n2, n5, n6, n7, n3, n4]
        self.assertEqual(expected, nodes)

    def test_whenTraverseBreadth_nodesOrderIsCorrect(self):
        # arrange
        graph, (n1, n2, n3, n4, n5, n6, n7) = self.get_graph()

        # act
        nodes = dag.traverse_breadth_first(graph)
        nodes = list(nodes)

        # assert
        expected = [n1, n2, n3, n4, n5, n6, n7]
        self.assertEqual(expected, nodes)

    def test_whenGetLeafNodes_nodesAreCorrect(self):
        # arrange
        graph, (n1, n2, n3, n4, n5, n6, n7) = self.get_graph()

        # act
        nodes = dag.leaf_nodes(graph)

        # assert
        expected = [n7]
        self.assertEqual(expected, nodes)

    @staticmethod
    def get_graph():
        n1 = Node(lambda: print('node 1'))
        n2 = Node(lambda: print('node 2'))
        n3 = Node(lambda: print('node 3'))
        n4 = Node(lambda: print('node 4'))
        n5 = Node(lambda: print('node 5'))
        n6 = Node(lambda: print('node 6'))
        n7 = Node(lambda: print('node 7'))

        n1 = n1 | n2 | n3 | n4
        n2 |= n5
        n3 |= n5
        n4 |= n6
        n5 |= n6 | n7
        n5 |= n7

        return n1, [n1, n2, n3, n4, n5, n6, n7]


if __name__ == '__main__':
    unittest.main()
