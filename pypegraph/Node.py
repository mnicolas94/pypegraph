from pypegraph import utils
from pypegraph.Action import Action


class Node(object):
	"""
	TODO
	"""

	def __init__(self, action, sequential=True):
		self.inputs = {}
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
		self.eventNotify = Action()

	def connect(self, node, connection_name='', **configuration):
		"""
		TODO
		:param node:
		:param connection_name:
		:return:
		"""
		if isinstance(node, Node):
			self.eventNotify += node.receive_input
			configuration['connection_name'] = connection_name
			# put connection in the other node input connections
			node.input_connections.setdefault(self, []).append(configuration)
		else:
			self.eventNotify += node  # treat it like a callable

	def disconnect(self, node, connection_name=''):
		"""
		TODO
		:param node:
		:param connection_name:
		:return:
		"""
		if isinstance(node, Node):
			if self in node.input_connections:
				self.eventNotify -= node.receive_input
				configurations = node.input_connections[self]
				for configuration in configurations:
					conn_name = configuration['connection_name']
					if connection_name == conn_name:
						configurations.remove(configuration)
					if len(configurations) == 0:
						node.input_connections.pop(self)
		else:
			self.eventNotify -= node  # treat it like a callable

	def receive_input(self, node, node_output):
		self.inputs[node] = node_output
		self.eventReceivedInput.invoke(node, node_output)
		if self.all_inputs_received():
			self.eventAllInputsReceived.invoke(self)
			if self.sequential:
				self.execute_and_notify()  # TODO considerar poner esto como un observer del evento eventAllInputsReceived

	def all_inputs_received(self):
		"""
		Verificar si todas las entradas han sido recibidas.
		:return: True si se recibieron todas las entradas, False en caso contrario.
		"""
		if self.inputs.keys() != self.input_connections.keys():
			return False
		return True

	def get_input_args(self):
		args = []
		kwargs = {}
		for node, configurations in self.input_connections.items():
			input = self.inputs[node]
			for conf in configurations:
				if 'ignore_output' in conf and conf['ignore_output']:
					continue
				input_name = conf['connection_name']
				if input_name == '':
					args.append(input)
				else:
					kwargs[input_name] = input
		return args, kwargs

	def execute_action(self, args=None, kwargs=None):
		if self.__action_inputs > 0:
			if not args and not kwargs:
				args, kwargs = self.get_input_args()
			else:
				args = args if args else []
				kwargs = kwargs if kwargs else {}
			self.output = self.action(*args, **kwargs)
		else:
			self.output = self.action()
		self.eventActionExecuted.invoke(self.output)

	def notify(self):
		"""
		TODO
		:return:
		"""
		self.eventNotify.invoke(self, self.output)

	def clear_inputs(self):
		"""
		Limpiar el diccionario de las entradas recibidas.
		:return:
		"""
		self.inputs.clear()

	def execute_and_notify(self, args=None, kwargs=None):
		self.execute_action(args, kwargs)
		self.clear_inputs()
		self.notify()

	def __call__(self, *args, **kwargs):
		self.execute_and_notify(args, kwargs)
