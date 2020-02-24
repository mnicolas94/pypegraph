from pypegraph.Node import Node
import utiles


class Connection(object):
	"""
	TODO
	"""

	def __init__(self, input_node, output_node, input_name='', output_name='', **configuration):
		self.input_node = input_node
		self.input_name = input_name
		self.output_node = output_node
		self.output_name = output_name
		self.__output_inputs = utiles.number_callable_params(output_node)  # number input paramaters of output_node
		self.setup_configuration(**configuration)

	def setup_configuration(self, **configuration):
		conf = configuration.copy()
		self.outputless = conf.pop('outputless', False)  # ignore input_node's output and just notify end of execution
		self.parallel = conf.pop('parallel', False)  # execution of output node will be done in another thread (or process)

	def send_output(self, output):
		if self.ouputless or self.__output_inputs == 0:
			self.output_node()
		elif self.output_name == '':
			self.output_node(*[output])
		else:
			self.output_node(**{self.output_name: output})
		# TODO multiple outputs

