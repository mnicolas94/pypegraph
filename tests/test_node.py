from pypegraph.Node import Node
import unittest
from tests import testutils


class TestNode(unittest.TestCase):

    def setUp(self):
        super().setUp()

    def test_whenConnects_connectionSucceeded(self):
        # arrange
        n1 = Node(lambda: print("node 1"))
        n2 = Node(lambda: print("node 2"))

        # false positive assertion
        self.assertEqual(n1.output_connections_count, 0)
        self.assertEqual(n2.input_connections_count, 0)

        # action
        n1.connect(n2)

        # assert
        self.assertEqual(n1.output_connections_count, 1)
        self.assertEqual(n2.input_connections_count, 1)

    def test_whenConnectsWithOperator_connectionSucceeded(self):
        # arrange
        n1 = Node(lambda: print("node 1"))
        n2 = Node(lambda: print("node 2"))

        # false positive assertion
        self.assertEqual(n1.output_connections_count, 0)
        self.assertEqual(n2.input_connections_count, 0)

        # action
        n1 = n1 | n2

        # assert
        self.assertEqual(n1.output_connections_count, 1)
        self.assertEqual(n2.input_connections_count, 1)

    def test_whenConnectsWithOperatorInPlace_connectionSucceeded(self):
        # arrange
        n1 = Node(lambda: print("node 1"))
        n2 = Node(lambda: print("node 2"))

        # false positive assertion
        self.assertEqual(n1.output_connections_count, 0)
        self.assertEqual(n2.input_connections_count, 0)

        # action
        n1 |= n2

        # assert
        self.assertEqual(n1.output_connections_count, 1)
        self.assertEqual(n2.input_connections_count, 1)

    def test_whenConnectsWithOperatorAndName_connectionSucceeded(self):
        # arrange
        n1 = Node(lambda: 1)
        n2 = Node(lambda x: x + x)

        # false positive assertion
        self.assertEqual(n1.output_connections_count, 0)
        self.assertEqual(n2.input_connections_count, 0)

        # action
        n1 = n1 | (n2, "x")

        # assert
        self.assertEqual(n1.output_connections_count, 1)
        self.assertEqual(n2.input_connections_count, 1)
        outputs = n1()
        n2_output = outputs[n2]
        self.assertEqual(n2_output, 2)

    def test_whenDisconnectNode_resultsAreConsistent(self):
        n1 = Node(action=lambda: 1)
        n2 = Node(action=lambda x: 2 + x)

        def f3(*xs): return sum(xs)

        n3 = Node(action=f3)

        n1 = n1 | n2 | n3
        n2 |= n3

        outputs = n1()
        self.assertEqual(outputs[n3], 4)

        n1.disconnect(n3)

        outputs = n1()
        self.assertEqual(outputs[n3], 3)

    def test_whenCallSingleNodeGraph_getOutput(self):
        # arrange
        n1 = Node(lambda: 42)

        # act
        outputs = n1()

        # assert
        self.assertEqual(outputs[n1], 42)

    def test_whenCallGraph_getOutputs(self):
        # arrange
        n1 = Node(lambda: 42)
        n2 = Node(lambda x: x + 8)
        n3 = Node(lambda x, y: x + y)

        n1.connect(n2)
        n1.connect(n3, "x")
        n2.connect(n3, "y")

        # act
        outputs = n1()

        # assert
        expected = {
            n1: 42,
            n2: 50,
            n3: 92
        }
        self.assertEqual(outputs, expected)

    def test_whenGetLastNodes_nodesAreCorrect(self):
        # arrange
        n1 = Node(lambda: print('node 1'))
        n2 = Node(lambda: print('node 2'))
        n3 = Node(lambda: print('node 3'))
        n4 = Node(lambda: print('node 4'))

        n1 |= n2 | n3
        n1 |= n3
        n2 |= n4

        # act
        last_nodes = n1.output_nodes

        # assert
        expected = [n3, n4]
        self.assertEqual(last_nodes, expected)


if __name__ == '__main__':
    unittest.main()
