import copy

from pypegraph.node import Node
from pypegraph import dag
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

    def test_whenConnectSameNodeWithDifferentConnectionName_inputsAndOutputsCountsAreCorrect(self):
        # arrange
        n1 = Node(lambda: print("node 1"))
        n2 = Node(lambda x, y: print(f"node 2: {x + y}"))

        # action
        n1.connect(n2, 'x')
        n1.connect(n2, 'y')

        # assert
        self.assertEqual(n1.output_connections_count, 1)
        self.assertEqual(n2.input_connections_count, 1)
        self.assertEqual(len(n2.input_connections[n1]), 2)

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

    def test_whenDisconnectNamedConfiguration_remainingConfigurationsAreCorrect(self):
        # arrange
        n1 = Node(lambda: print("node 1"))
        n2 = Node(lambda x, y: print(f"node 2: {x + y}"))
        n1.connect(n2, 'x')
        n1.connect(n2, 'y')

        # false positive assertion
        self.assertEqual(n1.output_connections_count, 1)
        self.assertEqual(n2.input_connections_count, 1)
        self.assertEqual(len(n2.input_connections[n1]), 2)

        # action
        n1.disconnect_named_connection(n2, 'x')

        # assert
        self.assertEqual(n1.output_connections_count, 1)
        self.assertEqual(n2.input_connections_count, 1)
        self.assertEqual(len(n2.input_connections[n1]), 1)
        self.assertEqual(n2.input_connections[n1][0]['connection_name'], 'y')

    def test_whenDisconnectAllInputs_nodeInputsEqualsZero(self):
        # arrange
        n1 = Node(lambda: print("node 1"))
        n2 = Node(lambda: print("node 2"))
        n3 = Node(lambda: print("node 3"))
        n4 = Node(lambda: print("node 4"))

        n1 |= n4
        n2 |= n4
        n3 |= n4

        # false positive assertion
        self.assertEqual(n4.input_connections_count, 3)

        # action
        n4.disconnect_all_inputs()

        # assert
        self.assertEqual(n4.input_connections_count, 0)

    def test_whenDisconnectAllOutputs_nodeOutputsEqualsZero(self):
        # arrange
        n1 = Node(lambda: print("node 1"))
        n2 = Node(lambda: print("node 2"))
        n3 = Node(lambda: print("node 3"))
        n4 = Node(lambda: print("node 4"))

        n1 |= n2
        n1 |= n3
        n1 |= n4

        # false positive assertion
        self.assertEqual(n1.output_connections_count, 3)

        # action
        n1.disconnect_all_outputs()

        # assert
        self.assertEqual(n1.output_connections_count, 0)

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

    def test_whenExecuteIntermediateNode_getExpectedOutputs(self):
        n1 = Node(action=lambda: 1)
        n2 = Node(action=lambda x: 2 + x)
        n3 = Node(action=lambda *xs: sum(xs))
        n4 = Node(action=lambda x: x ** 2)

        n1.connect(n2)
        n1.connect(n3)
        n2.connect(n3)
        n3.connect(n4)

        outputs = n3(*[1, 2, 3, 4])
        expected = {
            n3: 10,
            n4: 100
        }
        self.assertEqual(outputs, expected)

    def test_whenConnectionIsIgnoreOutput_resultsAreConsistentWithThatOutputIgnored(self):
        n1 = Node(action=lambda: 1)
        n2 = Node(action=lambda x: 2 + x)
        n3 = Node(action=lambda *xs: sum(xs))
        n4 = Node(action=lambda x: x**2)

        n1.connect(n2)
        n1.connect(n3, ignore_output=True)
        n2.connect(n3)
        n3.connect(n4)

        outputs = n1()
        result = outputs[n4]
        expected = 9
        self.assertEqual(result, expected)

    def test_whenGetName_nameIsCorrect(self):
        # arrange
        n1, _ = testutils.get_graph()

        # act
        name = n1.name

        # assert
        expected = 'n1'
        self.assertEqual(expected, name)

    def test_whenGetNameVerbose_nameIsCorrect(self):
        # arrange
        n1, _ = testutils.get_graph()

        # act
        name = n1.name_verbose

        # assert
        expected = 'n1 0 -> 3'
        self.assertEqual(expected, name)

    def test_whenCopy_resultIsCorrect(self):
        # arrange
        n1 = Node(action=lambda: print('node 1'), name='node 1')
        n2 = Node(action=lambda: print('node 2'), name='node 2')
        n3 = Node(action=lambda: print('node 3'), name='node 3')

        n1.connect(n2, 'n2')
        n1.connect(n3, 'n3')

        # act
        n1copy = copy.copy(n1)

        # assert
        self.assertEqual(n1.name, n1copy.name)
        for connection, connection_copy in zip(n1.output_connections.items(), n1copy.output_connections.items()):
            node, conf = connection
            node_copy, conf_copy = connection_copy
            self.assertEqual(node, node_copy)
            self.assertEqual(conf, conf_copy)

    def test_whenDeepCopy_resultIsCorrect(self):
        # arrange
        n1, _ = testutils.get_graph()

        # act
        n1copy = copy.deepcopy(n1)

        # assert
        bfs = dag.traverse_breadth_first(n1)
        bfscopy = dag.traverse_breadth_first(n1copy)
        for node, nodecopy in zip(bfs, bfscopy):
            self.assertEqual(node.name, nodecopy.name)
            for connection, connection_copy in zip(node.output_connections.items(), nodecopy.output_connections.items()):
                child, conf = connection
                child_copy, conf_copy = connection_copy
                self.assertNotEqual(child, child_copy)
                self.assertEqual(conf, conf_copy)


if __name__ == '__main__':
    unittest.main()
