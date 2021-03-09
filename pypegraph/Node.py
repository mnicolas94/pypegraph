from typing import Tuple

from pypegraph import utils
from pypegraph.Action import Action
from pypegraph.Connection import Connection


class Node(object):
	"""
	TODO
	"""

	def __init__(self, action, sequential=True):
		self.inputs = {}
		self.input_notifications = 0  # esta es la cantidad de entradas recibidas de nodos que no brindan salida
		self.input_connections = []

		self._output = None
		self.output_connections = []

		self.action = action
		self.__action_inputs = utils.number_callable_params(self.action)

		# wether to execute the node action on all inputs recieved
		self.sequential = sequential  # TODO considerar cambiar el nombre

		self.eventReceivedInput = Action()
		self.eventAllInputsReceived = Action()
		self.eventActionExecuted = Action()

	@property
	def input_connections_count(self):
		return len(self.input_connections)

	@property
	def output_connections_count(self):
		return len(self.output_connections)

	def connect(self, node, connection_name='', **configuration):
		"""
		TODO
		:param node:
		:param connection_name:
		:return:
		"""
		connection = Connection(self, node, connection_name, **configuration)
		self.output_connections.append(connection)
		# put connection in the other node input connections
		if isinstance(node, Node):
			node.input_connections.append(connection)

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

	def disconnect(self, node, connection_name=''):
		"""
		TODO
		:param node:
		:param connection_name:
		:return:
		"""
		connection = Connection(self, node, connection_name)  # TODO considerar hacerlo de otra manera, esto puede ser costoso por gusto
		if connection in self.output_connections:
			self.output_connections.remove(connection)

		if isinstance(node, Node):
			if connection in node.input_connections:
				node.input_connections.remove(connection)

	def _add_input(self, input, input_name=''):
		"""
		Adds a received input to the list of received inputs.
		:param input:
		:param input_name:
		:return:
		"""
		if input_name == '':
			self.inputs.setdefault(input_name, []).append(input)
		else:
			self.inputs[input_name] = input

	def _receive_input(self, *args, **kwargs):
		"""
		Receives an input from an input connection.
		:param args:
		:param kwargs:
		:return:
		"""
		if len(args) > 0:
			self._add_input(*args)
		elif len(kwargs) > 0:
			key, arg = list(kwargs.items())[0]  # TODO pasarle todos los parámetros del diccionario
			exists_input_connection = any(key == connection.output_name for connection in self.input_connections)
			if exists_input_connection:
				self._add_input(arg, key)
			else:
				print('Warning: Trying to add input not registered as input connection:', key)
		elif len(self.input_connections) > 0:
			self.input_notifications += 1

		self.eventReceivedInput.invoke(*args, **kwargs)

	def _all_inputs_received(self):
		"""
		Verificar si todas las entradas han sido recibidas.
		:return: True si se recibieron todas las entradas, False en caso contrario.
		"""
		unnamed_inputs = len(self.inputs['']) if '' in self.inputs else 0
		named_inputs = (len(self.inputs) - 1) if '' in self.inputs else len(self.inputs)
		total_inputs = unnamed_inputs + named_inputs
		if len(self.input_connections) != total_inputs:
			return False
		return True

	def _get_inputs(self):
		inputs = self.inputs.pop('') if '' in self.inputs else []
		named_inputs = self.inputs
		return inputs, named_inputs

	def _clear_inputs(self):
		"""
		Limpiar el diccionario de las entradas recibidas.
		:return:
		"""
		self.inputs.clear()
		self.input_notifications = 0

	def _execute_action(self):
		if self.__action_inputs > 0:
			inputs, named_inputs = self._get_inputs()
			self._output = self.action(*inputs, **named_inputs)
		else:
			self._output = self.action()
		self.eventActionExecuted.invoke(self._output)

	def _notify(self) -> dict:
		"""
		TODO
		:return:
		"""
		backpropagated_outputs = {}
		for connection in self.output_connections:
			outputs = connection.send_output(self._output) or {}
			for key in outputs.keys():
				backpropagated_outputs[key] = outputs[key]

		return backpropagated_outputs

	def _execute_and_notify(self) -> dict:
		self._execute_action()
		self._clear_inputs()

		backpropagated_outputs = self._notify()
		backpropagated_outputs[self] = self._output

		return backpropagated_outputs

	def __call__(self, *args, **kwargs) -> dict:
		self._receive_input(*args, **kwargs)
		if self._all_inputs_received():
			self.eventAllInputsReceived.invoke(self)
			if self.sequential:
				graph_outputs = self._execute_and_notify()  # TODO considerar poner esto como un observer del evento eventAllInputsReceived
				return graph_outputs

		return {}

