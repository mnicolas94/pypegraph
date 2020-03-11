from pypegraph.Node import Node
import unittest
from tests import testutils
import cv2 as cv


class TestPypegraphUseCases(unittest.TestCase):

	def setUp(self):
		super().setUp()

	def test_node_disconnection(self):
		n1 = Node(action=lambda: 1)
		n2 = Node(action=lambda x: 2 + x)

		def f3(*xs): return sum(xs)
		n3 = Node(action=f3)

		def f4(x):
			global result
			result = x**2
		n4 = Node(action=lambda x: f4(x))

		n1.connect(n2)
		n1.connect(n3)
		n2.connect(n3)
		n3.connect(n4)

		n1()
		self.assertEqual(16, result)
		n1.disconnect(n3)
		n1()
		self.assertEqual(9, result)

	def test_ignore_output(self):
		n1 = Node(action=lambda: 1)
		n2 = Node(action=lambda x: 2 + x)

		def executed_first(first):
			global ef
			ef = first

		def f3(*xs):
			executed_first(False)
			return sum(xs)

		n3 = Node(action=f3)
		n3.eventReceivedInput += lambda*_: executed_first(True)

		def f4(x):
			global result
			result = x ** 2

		n4 = Node(action=lambda x: f4(x))

		n1.connect(n2)
		n1.connect(n3, ignore_output=True)
		n2.connect(n3)
		n3.connect(n4)

		n1()
		self.assertEqual(9, result)
		self.assertFalse(ef)  # verificar que el nodo 3 se ejecutó después de haber recibido ambas entradas (n1 y n2)

	def test_parallel_notification(self):
		# TODO
		pass

	def test_execute_midle_graph(self):
		"""
		Test a graph execution begining from an intermediate node instead from the first one.
		It is required to pass that intermediate node's arguments.
		:return:
		"""
		n1 = Node(action=lambda: 1)
		n2 = Node(action=lambda x: 2 + x)

		def f3(*xs): return sum(xs)

		n3 = Node(action=f3)

		def f4(x):
			global result
			result = x ** 2

		n4 = Node(action=lambda x: f4(x))

		n1.connect(n2)
		n1.connect(n3)
		n2.connect(n3)
		n3.connect(n4)

		n3(*[1, 2, 3, 4])
		self.assertEqual(100, result)

	def test_simple_pipeline(self):
		def detection(img):
			return [((1, 1, 40, 40), 0.5), ((40, 50, 140, 150), 0.9)]

		# crear nodos
		input_node = Node(action=lambda: testutils.test_img())
		detector_node = Node(action=detection)
		filter_det_node = Node(action=lambda detections: [max(detections, key=lambda x: x[1])])
		draw_best_node = Node(action=testutils.draw_detections)
		output_node1 = Node(action=lambda image: cv.imshow('Detection', image))

		# this node is for validation only
		global num_outputs
		num_outputs = 0
		def on_output():
			global num_outputs
			num_outputs += 1

		# conexiones
		input_node.connect(detector_node)
		input_node.connect(draw_best_node, 'image')
		detector_node.connect(filter_det_node)
		filter_det_node.connect(draw_best_node, 'detections')
		draw_best_node.connect(output_node1)
		output_node1.connect(on_output)

		# run pipeline
		input_node()
		self.assertEqual(1, num_outputs)

	def test_semicomplex_pipeline(self):
		def detection(img):
			return [((1, 1, 40, 40), 0.5), ((40, 50, 140, 150), 0.9)]

		# crear nodos
		input_node = Node(action=lambda: testutils.test_img())

		detector_node = Node(action=detection)
		filter_det_node = Node(action=lambda detections: [max(detections, key=lambda x: x[1])])
		det2box_node = Node(action=lambda det: det[0][0])

		drawer_node = Node(action=testutils.draw_detections)
		draw_best_node = Node(action=testutils.draw_detections)
		cropper_node = Node(action=lambda image, box: image[box[1]:box[3], box[0]:box[2]])

		output_node1 = Node(action=lambda image: cv.imshow('original', image))
		output_node2 = Node(action=lambda image: cv.imshow('all_detections', image))
		output_node3 = Node(action=lambda image: cv.imshow('detection', image))
		output_node4 = Node(action=lambda image: cv.imshow('cropped', image))

		# this node is for validation only
		global end_reached
		end_reached = False
		def on_output():
			global end_reached
			end_reached = True
		validator_node = Node(action=on_output)

		# conexiones
		input_node.connect(detector_node)
		input_node.connect(drawer_node, 'image')
		input_node.connect(draw_best_node, 'image')
		input_node.connect(cropper_node, 'image')
		input_node.connect(output_node1)

		detector_node.connect(drawer_node, 'detections')
		detector_node.connect(filter_det_node)

		filter_det_node.connect(det2box_node)
		filter_det_node.connect(draw_best_node, 'detections')

		det2box_node.connect(cropper_node, 'box')

		drawer_node.connect(output_node2)
		draw_best_node.connect(output_node3)
		cropper_node.connect(output_node4)

		output_node1.connect(validator_node)
		output_node2.connect(validator_node)
		output_node3.connect(validator_node)
		output_node4.connect(validator_node)

		# run pipeline
		input_node()
		self.assertEqual(1, end_reached)


if __name__ == '__main__':
	unittest.main()
