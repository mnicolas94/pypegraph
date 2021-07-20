import copy
from typing import Tuple, Dict, List

from pypegraph import utils
from pypegraph.action import Action


class Node(object):
    """
    TODO
    """

    def __init__(self, action, name='-', sequential=True):
        self._name = name
        self._inputs_received = {}
        self._input_connections: Dict[Node, List[Dict]] = {}

        self._output = None
        self._output_connections: Dict[Node, dict] = {}

        self._action = action
        self.__action_inputs = utils.number_callable_params(self._action)

        # wether to execute the node action on all inputs recieved
        self._sequential = sequential  # TODO considerar cambiar el nombre

        self.eventReceivedInput = Action()
        self.eventAllInputsReceived = Action()
        self.eventActionExecuted = Action()

    @property
    def name(self):
        return self._name

    @property
    def name_verbose(self):
        input_count = self.input_connections_count
        output_count = self.output_connections_count
        verbose_name = f'{self.name} {input_count} -> {output_count}'
        return verbose_name

    def __str__(self):
        return self.name

    @property
    def input_connections_count(self):
        return len(self._input_connections)

    @property
    def output_connections_count(self):
        return len(self._output_connections)

    @property
    def input_connections(self):
        return copy.copy(self._input_connections)

    @property
    def output_connections(self):
        return copy.copy(self._output_connections)

    def connect(self, node, connection_name='', **configuration):
        """
        TODO
        :param node:
        :param connection_name:
        :return:
        """
        configuration['connection_name'] = connection_name
        if isinstance(node, Node):
            # put connection in the other node input connections
            node._input_connections.setdefault(self, []).append(configuration)
        self._output_connections[node] = configuration

    def __or__(self, other):
        node = other
        connection_name = ""
        configuration = {}
        if isinstance(other, Tuple):
            if len(other) == 2:
                node, connection_name = other
                configuration = {}
            elif len(other) == 3:
                node, connection_name = other
                configuration = {}
        self.connect(node, connection_name, **configuration)
        return self

    def disconnect(self, node: "Node"):
        if node in self._output_connections:
            self._output_connections.pop(node)
        if isinstance(node, Node):
            if self in node._input_connections:
                node._input_connections.pop(self)

    def disconnect_named_connection(self, node: "Node", connection_name=''):
        """
        TODO
        :param node:
        :param connection_name:
        :return:
        """
        if isinstance(node, Node):
            if self in node._input_connections:
                configurations = node._input_connections[self]
                for configuration in configurations:
                    conn_name = configuration['connection_name']
                    if connection_name == conn_name:
                        configurations.remove(configuration)
                    if len(configurations) == 0:
                        node._input_connections.pop(self)
                        if node in self._output_connections:
                            self._output_connections.pop(node)

    def disconnect_all_inputs(self):
        input_nodes = [node for node, _ in self._input_connections.items()]
        for node in input_nodes:
            node.disconnect(self)

    def disconnect_all_outputs(self):
        output_nodes = [node for node, _ in self._output_connections.items()]
        for node in output_nodes:
            self.disconnect(node)

    def _push_input_from_node(self, node, node_output):
        self._inputs_received[node] = node_output
        self.eventReceivedInput.invoke(node, node_output)
        if self._all_inputs_received():
            self.eventAllInputsReceived.invoke(self)
            if self._sequential:
                outputs = self._execute_and_notify()
                return outputs
        return {}

    def _all_inputs_received(self):
        """
        Verificar si todas las entradas han sido recibidas.
        :return: True si se recibieron todas las entradas, False en caso contrario.
        """
        if self._inputs_received.keys() != self._input_connections.keys():
            return False
        return True

    def _clear_inputs_received(self):
        """
        Limpiar el diccionario de las entradas recibidas.
        :return:
        """
        self._inputs_received.clear()

    def _get_input_args(self):
        args = []
        kwargs = {}
        for node, configurations in self._input_connections.items():
            input = self._inputs_received[node]
            for conf in configurations:
                if 'ignore_output' in conf and conf['ignore_output']:
                    continue
                input_name = conf['connection_name']
                if input_name == '':
                    args.append(input)
                else:
                    kwargs[input_name] = input
        return args, kwargs

    def _execute_action(self, args=None, kwargs=None):
        if self.__action_inputs > 0:
            if args is None and kwargs is None:
                args, kwargs = self._get_input_args()
            else:
                args = args if args is not None else []
                kwargs = kwargs if kwargs is not None else {}
            self._output = self._action(*args, **kwargs)
        else:
            self._output = self._action()
        self.eventActionExecuted.invoke(self._output)

    def _notify(self) -> dict:
        """
        TODO
        :return:
        """
        backpropagated_outputs = {}
        for node, config in self._output_connections.items():
            if isinstance(node, Node):
                outputs = node._push_input_from_node(self, self._output)
            else:
                outputs = node(self._output) or {}  # TODO add callable to graph outputs dir

            for key in outputs.keys():
                backpropagated_outputs[key] = outputs[key]

        return backpropagated_outputs

    def _execute_and_notify(self, args=None, kwargs=None) -> dict:
        self._execute_action(args, kwargs)
        self._clear_inputs_received()
        backpropagated_outputs = self._notify()
        backpropagated_outputs[self] = self._output
        return backpropagated_outputs

    def __call__(self, *args, **kwargs) -> dict:
        graph_outputs = self._execute_and_notify(args, kwargs)
        return graph_outputs

    def __copy__(self):
        self_copy = type(self)(action=self._action, name=self._name, sequential=self._sequential)
        for node, conf in self._output_connections.items():
            conf_copy = copy.copy(conf)
            connection_name = conf_copy.pop('connection_name')
            self_copy.connect(node, connection_name, **conf_copy)
        return self_copy

    def __deepcopy__(self, memodict={}):
        self_copy = type(self)(action=self._action, name=self._name, sequential=self._sequential)

        copies_dict = {self: self_copy}
        traversal_queue = [self]
        visited = []

        while len(traversal_queue) > 0:
            node = traversal_queue[0]
            traversal_queue.remove(node)
            node_copy = copies_dict[node]
            visited.append(node)

            for connected_node, conf in node._output_connections.items():
                if connected_node in copies_dict:
                    connected_node_copy = copies_dict[connected_node]
                else:
                    connected_node_copy = Node(
                        action=connected_node._action,
                        name=connected_node._name,
                        sequential=connected_node._sequential)
                    copies_dict[connected_node] = connected_node_copy
                conf_copy = copy.copy(conf)
                connection_name = conf_copy.pop('connection_name')
                node_copy.connect(connected_node_copy, connection_name, **conf_copy)
                if connected_node not in visited:
                    traversal_queue.append(connected_node)
        return self_copy
