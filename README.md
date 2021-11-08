# pypegraph
Pypegraph is a python library to create directed acyclic graphs (DAG) that represent data processing pipelines. In a pypegraph graph, each node contains a function wich output is sendend to the connected nodes and are used as input of those nodes's functions.
# Installation
`pip install pypegraph`
# Common usage
```python
node1 = Node(lambda: print("Node1 is executing"), name="Node1")
node2 = Node(lambda: print("Node2 is executing"), name="Node2")

node1 |= node2  # connect both nodes node1 -> node2

outputs = node1()  # dictionary with each node outputs
node1_output = outputs[node1]  # None in this case because it does not return anything
node2_output = outputs[node2]  # None also
```
You can connect one node's output to a named parameter of another node's function input
```python
def foo(n):
  return n
def square(number):
  return number * number
node1 = Node(foo, name="Node1")
node2 = Node(square, name="Node2")

node1 |= (node2, "number")  # connect both nodes with a connection name
outputs = node1(2)
node2_output = outputs[node2]  # should be 4
```
# Connections
You can connect nodes in several ways
```python
node1 = Node(lambda: print("Node1 is executing"), name="Node1")
node2 = Node(lambda: print("Node2 is executing"), name="Node2")

# you can do
n1 = n1 | n2
# or
n1 |= n2
# or
n1.connect(n2)

# nodes can be disconnected with
n1.disconnect(n2)
```
