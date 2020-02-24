from pypegraph.Node import Node
from pipeline_graph_tests.Detectors import FaceDetectorFaceRetail
import unittest
import utiles
import cv2 as cv


class TestPypegraphUseCases(unittest.TestCase):

	def setUp(self):
		super().setUp()

	def test_simple_pipeline(self):
		detector = FaceDetectorFaceRetail()

		# crear nodos
		input_node = Node(action=lambda: utiles.test_img())
		detector_node = Node(action=detector.detect)
		filter_det_node = Node(action=lambda detections: [max(detections, key=lambda x: x[1])])
		draw_best_node = Node(action=utiles.draw_detections)
		output_node1 = Node(action=lambda image: cv.imshow('Detection', image))

		global num_outputs
		num_outputs = 0
		def on_output():
			global num_outputs
			num_outputs += 1
		validator_node = Node(action=on_output)

		# conexiones
		input_node.connect(detector_node)
		input_node.connect(draw_best_node, 'image')
		detector_node.connect(filter_det_node)
		filter_det_node.connect(draw_best_node, 'detections')
		draw_best_node.connect(output_node1)
		output_node1.connect(validator_node)

		input_node()
		self.assertEqual(num_outputs, 1)

	def test_semicomplex_pipeline(self):
		detector = FaceDetectorFaceRetail()

		# crear nodos
		input_node = Node(action=lambda: utiles.test_img())

		detector_node = Node(action=detector.detect)
		filter_det_node = Node(action=lambda detections: [max(detections, key=lambda x: x[1])])
		det2box_node = Node(action=lambda det: det[0][0])

		drawer_node = Node(action=utiles.draw_detections)
		draw_best_node = Node(action=utiles.draw_detections)
		cropper_node = Node(action=lambda image, box: image[box[1]:box[3], box[0]:box[2]])

		output_node1 = Node(action=lambda image: cv.imshow('original', image))
		output_node2 = Node(action=lambda image: cv.imshow('all_detections', image))
		output_node3 = Node(action=lambda image: cv.imshow('detection', image))
		output_node4 = Node(action=lambda image: cv.imshow('cropped', image))

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

		input_node()
		self.assertEqual(end_reached, 1)


if __name__ == '__main__':
	unittest.main()
