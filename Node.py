import utils
from Action import Action
from Connection import Connection


class Node(object):
	"""
	TODO
	"""

	def __init__(self, action, sequential=True):
		self.inputs = {}
		self.input_notifications = 0  # esta es la cantidad de entradas recibidas de nodos que no brindan salida
		self.input_connections = {}

		self.output = None
		self.output_connections = []

		self.action = action
		self.__action_inputs = utils.number_callable_params(self.action)

		# wether to execute the node action on all inputs recieved
		self.sequential = sequential  # TODO considerar cambiar el nombre

		self.eventReceivedInput = Action()
		self.eventAllInputsReceived = Action()
		self.eventActionExecuted = Action()

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
			if connection_name == '':
				node.input_connections.setdefault(connection_name, []).append(connection)
			else:
				node.input_connections[connection_name] = connection

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
			if connection_name in node.input_connections:
				if connection_name == '':
					if connection in node.input_connections['']:
						node.input_connections[''].remove(connection)
				else:
					node.input_connections.pop(connection_name)

	def add_input(self, input, input_name=''):
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

	def receive_input(self, *args, **kwargs):
		"""
		Receives an input from an input connection.
		:param args:
		:param kwargs:
		:return:
		"""
		if len(args) > 0:
			self.add_input(*args)
		elif len(kwargs) > 0:
			key, arg = list(kwargs.items())[0]
			if key in self.input_connections:
				self.add_input(arg, key)  # TODO pasarle todos los parámetros del diccionario
			else:
				print('Warning: Trying to add input not registered as inpu connection:', key)
		elif len(self.input_connections) > 0:
			self.input_notifications += 1

		self.eventReceivedInput.invoke(*args, **kwargs)

	def all_inputs_received(self):
		"""
		Verificar si todas las entradas han sido recividas.
		:return: True si se recibieron todas las entradas, False en caso contrario.
		"""
		if self.inputs.keys() != self.input_connections.keys():
			return False
		if '' in self.inputs:
			if len(self.inputs['']) != len(self.input_connections['']) + self.input_notifications:
				return False
		return True

	def execute_action(self):
		if self.__action_inputs > 0:
			inputs = self.inputs.pop('') if '' in self.inputs else []
			named_inputs = self.inputs
			self.output = self.action(*inputs, **named_inputs)
		else:
			self.output = self.action()
		self.eventActionExecuted.invoke(self.output)

	def notify(self):
		"""
		TODO
		:return:
		"""
		for connection in self.output_connections:
			connection.send_output(self.output)

	def clear_inputs_output(self):
		"""
		Limpiar el diccionario de las entradas recibidas y la salida calculada.
		:return:
		"""
		self.inputs.clear()
		self.input_notifications = 0
		self.output = None

	def execute_and_notify(self):
		self.execute_action()
		self.notify()
		self.clear_inputs_output()

	def __call__(self, *args, **kwargs):
		self.receive_input(*args, **kwargs)
		if self.all_inputs_received():
			self.eventAllInputsReceived.invoke(self)
			if self.sequential:
				self.execute_and_notify()

