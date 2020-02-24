import utiles


class Action:
	"""
	TODO
	"""

	def __init__(self):
		self.callbacks = []

	def __add__(self, other):
		if callable(other):
			if other not in self.callbacks:
				self.callbacks.append(other)
		return self

	def __sub__(self, other):
		if callable(other):
			if other in self.callbacks:
				self.callbacks.remove(other)
		return self

	def invoke(self, *args, **kwargs):
		for callback in self.callbacks:
			num_parameters = utiles.number_callable_params(callback)
			if num_parameters == 0:  # esto es solo para cuando el callback es una función lambda en vez de un nodo
				callback()
			else:
				callback(*args, **kwargs)


if __name__ == '__main__':
	a = Action()
	a += lambda: print('123')
	a.invoke()
	print('')

