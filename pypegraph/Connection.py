from pypegraph import utils


class Connection(object):
	"""
	TODO
	"""

	def __init__(self, input_node, output_node, output_name='', **configuration):
		self.input_node = input_node
		self.output_node = output_node
		self.output_name = output_name
		self.__output_inputs = utils.number_callable_params(output_node)  # number input paramaters of output_node
		self.setup_configuration(**configuration)

	def setup_configuration(self, **configuration):
		conf = configuration.copy()
		self.outputless = conf.pop('outputless', False)  # ignore input_node's output and just notify end of execution
		self.parallel = conf.pop('parallel', False)  # execution of output node will be done in another thread (or process)

	def send_output(self, output) -> dict:
		if self.output_name == '':
			outputs = self.output_node(*[output])
		else:
			outputs = self.output_node(**{self.output_name: output})
		return outputs
		# TODO multiple outputs

	def __eq__(self, other):
		if not isinstance(other, Connection):
			return False
		if other.input_node != self.input_node:
			return False
		if other.output_node != self.output_node:
			return False
		if other.output_name != self.output_name:
			return False
		return True
