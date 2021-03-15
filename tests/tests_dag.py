from pypegraph import dag
from pypegraph.node import Node
import unittest
from tests import testutils


class TestDag(unittest.TestCase):

    def setUp(self):
        super().setUp()

    def test_whenTraverseDepth_nodesOrderIsCorrect(self):
        # arrange
        graph, (n1, n2, n3, n4, n5, n6, n7) = testutils.get_graph()

        # act
        nodes = dag.traverse_depth_first(graph)
        nodes = list(nodes)

        # assert
        expected = [n1, n2, n5, n6, n7, n3, n4]
        self.assertEqual(expected, nodes)

    def test_whenTraverseBreadth_nodesOrderIsCorrect(self):
        # arrange
        graph, (n1, n2, n3, n4, n5, n6, n7) = testutils.get_graph()

        # act
        nodes = dag.traverse_breadth_first(graph)
        nodes = list(nodes)

        # assert
        expected = [n1, n2, n3, n4, n5, n6, n7]
        self.assertEqual(expected, nodes)

    def test_whenTraverseConnectionsDepth_nodesOrderIsCorrect(self):
        # arrange
        graph, (n1, n2, n3, n4, n5, n6, n7) = testutils.get_graph()

        # act
        connections = dag.traverse_connections_depth_first(graph)
        connections = list(connections)

        # assert
        expected = [
            (n1, n2),
            (n2, n5),
            (n5, n6),
            (n6, n7),
            (n5, n7),
            (n1, n3),
            (n3, n5),
            (n1, n4),
            (n4, n6)
        ]
        self.assertEqual(expected, connections)

    def test_whenTraverseConnectionsBreadth_nodesOrderIsCorrect(self):
        # arrange
        graph, (n1, n2, n3, n4, n5, n6, n7) = testutils.get_graph()

        # act
        connections = dag.traverse_connections_depth_first(graph)
        connections = list(connections)

        # assert
        expected = [
            (n1, n2),
            (n1, n3),
            (n1, n4),
            (n2, n5),
            (n3, n5),
            (n4, n6),
            (n5, n6),
            (n5, n7),
            (n6, n7),
        ]
        self.assertEqual(expected, connections)

    def test_whenGetLeafNodes_nodesAreCorrect(self):
        # arrange
        graph, (n1, n2, n3, n4, n5, n6, n7) = testutils.get_graph()

        # act
        nodes = dag.leaf_nodes(graph)

        # assert
        expected = [n7]
        self.assertEqual(expected, nodes)


if __name__ == '__main__':
    unittest.main()
