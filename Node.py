import utiles
from pypegraph.Action import Action


class Node(object):
	"""
	TODO
	"""

	def __init__(self, action, sequential=True):
		self.inputs = {}
		self.input_notifications = 0  # esta es la cantidad de entradas recibidas de nodos que no brindan salida
		self.input_connections = {}

		self.output = None
		self.output_connections = {}

		self.action = action
		self.__action_inputs = utiles.number_callable_params(self.action)

		# wether to execute the node action on all inputs recieved
		self.sequential = sequential  # TODO considerar cambiar el nombre

		self.eventReceivedInput = Action()
		self.eventAllInputsReceived = Action()
		self.eventActionExecuted = Action()

	def connect(self, node, node_name=''):
		"""
		TODO
		:param node:
		:param node_name:
		:return:
		"""
		self.output_connections.setdefault(node_name, []).append(node)
		# connect self as the other node input
		if isinstance(node, Node):
			if node_name == '':
				node.input_connections.setdefault(node_name, []).append(self)
			else:
				node.input_connections[node_name] = self

	def disconnect(self, node, node_name=''):
		"""
		TODO
		:param node:
		:param node_name:
		:return:
		"""
		if node_name in self.output_connections:
			self.output_connections[node_name].remove(node)
		if isinstance(node, Node):
			if node_name in node.input_connections:
				if node_name == '':
					node.input_connections[node_name].remove(self)
				else:
					node.input_connections.pop(node_name)

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
			karg, arg = list(kwargs.items())[0]
			self.add_input(arg, karg)  # TODO pasarle todos los parámetros del diccionario
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
		for name, callables in self.output_connections.items():
			for callback in callables:
				num_parameters = utiles.number_callable_params(callback)
				if num_parameters == 0:  # esto es solo para cuando el callback es una función lambda en vez de un nodo
					callback()
				elif name == '':
					callback(*[self.output])
				else:
					callback(**{name: self.output})

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

