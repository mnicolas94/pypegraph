from inspect import signature, getsource
import ast


def number_callable_params(callable):
	"""
	Número de parámetros de una función o callable.
	:param callable: objeto que puede ser invocado
	:return:
	"""
	return len(signature(callable).parameters)


def function_has_return(callable):
	"""
	Devuelve True si la función tiene sentencia return, False en caso contrario.
	No funciona con funciones cuyo código no esté escrito en Python.
	:param callable:
	:return:
	"""

	return any(isinstance(node, ast.Return) for node in ast.walk(ast.parse(getsource(callable))))
