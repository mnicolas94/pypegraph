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
			node.input_connections.append(connection)

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
			key, arg = list(kwargs.items())[0]  # TODO pasarle todos los parámetros del diccionario
			exists_input_connection = any(key == connection.output_name for connection in self.input_connections)
			if exists_input_connection:
				self.add_input(arg, key)
			else:
				print('Warning: Trying to add input not registered as input connection:', key)
		elif len(self.input_connections) > 0:
			self.input_notifications += 1

		self.eventReceivedInput.invoke(*args, **kwargs)

	def all_inputs_received(self):
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

	def clear_inputs(self):
		"""
		Limpiar el diccionario de las entradas recibidas.
		:return:
		"""
		self.inputs.clear()
		self.input_notifications = 0

	def execute_and_notify(self):
		self.execute_action()
		self.clear_inputs()
		self.notify()

	def __call__(self, *args, **kwargs):
		self.receive_input(*args, **kwargs)
		if self.all_inputs_received():
			self.eventAllInputsReceived.invoke(self)
			if self.sequential:
				self.execute_and_notify()  # TODO considerar poner esto como un observer del evento eventAllInputsReceived

