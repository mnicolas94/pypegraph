from pypegraph import utils


class Action:
	"""
	C#-like Action (see at https://docs.microsoft.com/en-us/dotnet/api/system.action?view=netframework-4.8).
	"""

	def __init__(self):
		self.callbacks = []

	def __iadd__(self, other):
		if callable(other):
			if other not in self.callbacks:
				self.callbacks.append(other)
		return self

	def __isub__(self, other):
		if callable(other):
			if other in self.callbacks:
				self.callbacks.remove(other)
		return self

	def invoke(self, *args, **kwargs):
		for callback in self.callbacks:
			num_parameters = utils.number_callable_params(callback)
			if num_parameters == 0:  # esto es solo para cuando el callback es una función lambda en vez de un nodo
				callback()
			else:
				callback(*args, **kwargs)


if __name__ == '__main__':
	print('Testing...')
	a = Action()
	def f(x): print('123')
	a += f
	a.invoke(2, 3)
	a -= f
	a.invoke()
	print('')
