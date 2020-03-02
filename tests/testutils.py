import random
from timeit import default_timer as timer
import cv2 as cv
import numpy as np
import os
from os import path
from datetime import datetime
import pandas as pd


def test_img():
	return cv.imread(os.path.dirname(__file__) + '/test_data/test.jpg')


def timeit(method):
	"""
	Decorador para medir el tiempo de ejecución de funciones
	:param method:
	:return:
	"""
	def timed(*args, **kw):
		ts = timer()
		result = method(*args, **kw)
		te = timer()
		print('Time for method \'{}\': {} ms'.format(method.__name__, te - ts))
		return result
	return timed


def warmup(method):
	"""
	Decorador para realizar fase de calentamiento antes de cualquier prueba de tiempo.
	:param method:
	:return:
	"""
	def warm(*args, **kw):
		print("warming...")
		for _ in range(10000):
			random.randint(0, 1000000)
		result = method(*args, **kw)
		return result
	return warm


def create_dir_of_file(file):
	"""
	Crea el directorio de un archivo, si este no existe.
	:param file: fichero.
	:return:
	"""
	directory, _ = path.split(file)
	if not path.exists(directory):
		os.makedirs(directory)


def date_string():
	"""
	Obtener string con la fecha actual en formato dia-mes-año_hora-minuto-segundo.
	:return: string con la fecha.
	"""
	return datetime.now().strftime("%y-%m-%d_%H-%M-%S")


def write_xlsx(datas, output_file):
	"""
	Escribir una tabla de datos en un archivo xlsx.
	:param datas: lista de tablas de datos con formato {columna: [valores], ...}.
	:param output_file: fichero de salida.
	:return:
	"""
	file_dir, _ = path.split(output_file)
	if file_dir != '' and not path.exists(file_dir):
		os.makedirs(file_dir)
	writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
	sheet_name = 'Sheet1'
	row = 0
	if isinstance(datas, list):
		for data in datas:
			df = pd.DataFrame(data)
			df.to_excel(writer, sheet_name=sheet_name, startrow=row, index=False)
			row += df.shape[0] + 2
	elif isinstance(datas, dict):
		for name, data in datas.items():
			df = pd.DataFrame(data)
			df.to_excel(writer, sheet_name=sheet_name, startrow=(row + 1), index=False)
			sheet = writer.sheets[sheet_name]
			sheet.write(row, 0, name)
			row += df.shape[0] + 3
	writer.save()


def sort_insert_binary(ordered_list, element, key=None, descending=False):
	length = len(ordered_list)
	if length == 0:
		ordered_list.append(element)
	else:
		insertado = False
		inf = 0
		sup = length - 1

		while not insertado and inf <= sup:
			med = (inf + sup) // 2
			m = ordered_list[med]
			cm = m if not key else key(m)
			ce = element if not key else key(element)

			if ce == cm:
				ordered_list.insert(med + 1, element)
				insertado = True
			elif cm > ce if descending else cm < ce:
				inf = med + 1
				if inf > sup:
					ordered_list.insert(inf, element)
			else:
				sup = med - 1
				if inf > sup:
					ordered_list.insert(med, element)


def search_binary(ordered_list, element, key=None, descending=False):
	length = len(ordered_list)
	if length == 0:
		return None
	else:
		inf = 0
		sup = length - 1

		while True:
			med = (inf + sup) // 2
			m = ordered_list[med]
			cm = m if not key else key(m)
			ce = element if not key else key(element)

			if ce == cm:
				return m
			elif cm > ce if descending else cm < ce:
				inf = med + 1
				if inf > sup:
					return None
			else:
				sup = med - 1
				if inf > sup:
					return None


def normalize_values(values, range_min=None, range_max=None, target_min=0, target_max=1):
	mn = min(values) if range_min is None else range_min
	mx = max(values) if range_max is None else range_max
	dif = mx - mn
	target_dif = target_max - target_min
	return [((x - mn) / dif) * target_dif + target_min for x in values]


def validate_box(box, img_width, img_height):
	"""
	Validar que las dimensiones de un rectángulo no estén fuera de las dimensiones de una imagen.
	:param x1: límite izquierdo del rectángulo.
	:param y1: límite superior del rectángulo.
	:param x2: límite derecho del rectángulo.
	:param y2: límite inferior del rectángulo.
	:param img_width: ancho de la imagen.
	:param img_height: alto de la imagen.
	:return: True si el rectángulo es válido, False en caso contrario.
	"""
	x1, y1, x2, y2 = box
	if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0:
		return False
	if x1 > img_width or y1 > img_height or x2 > img_width or y2 > img_height:
		return False
	return True


def validate_boxes(boxes, img_width, img_height):
	"""
	De una lista de rectángulos, filtra los que son válidos, es decir, los que sus dimensiones no se salen de las dimensiones
	de la imagen.
	:param boxes: lista de rectángulos.
	:param img_width: ancho de la imagen.
	:param img_height: alto de la imagen.
	:return: lista filtrada.
	"""
	return [box for box in boxes if validate_box(box, img_width, img_height)]


def get_boxes(detections):
	return [box for box, _ in detections]


def get_confidences(detections):
	return [confidence for _, confidence in detections]


def filter_confidence(detections, threshold):
	return [(box, confidence) for box, confidence in detections if confidence >= threshold]


def filter_valid_dets(detections, img_width, img_height):
	return [(box, confidence) for box, confidence in detections if validate_box(box, img_width, img_height)]


def draw_detections(image, detections):
	draw = image.copy()
	for det in detections:
		box, _ = det
		cv.rectangle(draw, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2, 4)
	return draw


def filter_valid_boxes(boxes, img_width, img_height):
	"""
	De una lista de rectángulos, filtra los que son válidos, es decir, los que sus dimensiones no se salen de las dimensiones
	de la imagen.
	:param boxes: lista de rectángulos.
	:param img_width: ancho de la imagen.
	:param img_height: alto de la imagen.
	:return: lista filtrada.
	"""
	return [box for box in boxes if validate_box(box, img_width, img_height)]


def intersection_over_union(A, B):
	(x1a, y1a, x2a, y2a) = A
	(x1b, y1b, x2b, y2b) = B
	# determine the (x, y)-coordinates of the intersection rectangle
	xA = max(x1a, x1b)
	yA = max(y1a, y1b)
	xB = min(x2a, x2b)
	yB = min(y2a, y2b)

	# compute the area of intersection rectangle
	interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

	# compute the area of both the prediction and ground-truth rectangles
	boxAArea = (x2a - x1a + 1) * (y2a - y1a + 1)
	boxBArea = (x2b - x1b + 1) * (y2b - y1b + 1)

	iou = interArea / float(boxAArea + boxBArea - interArea)
	return iou


def non_max_suppression(boxes, overlap_thresh=0.3, iou_thresh=0.65):
	if len(boxes) == 0:
		return []
	if boxes.dtype.kind == "i":
		boxes = boxes.astype("float")
	pick = []
	x1 = boxes[:, 0]
	y1 = boxes[:, 1]
	x2 = boxes[:, 2]
	y2 = boxes[:, 3]
	area = (x2 - x1 + 1) * (y2 - y1 + 1)
	idxs = np.argsort(y2)
	while len(idxs) > 0:
		last = len(idxs) - 1
		i = idxs[last]
		pick.append(i)

		# dimensiones de las intersecciones
		xx1 = np.maximum(x1[i], x1[idxs[:last]])
		yy1 = np.maximum(y1[i], y1[idxs[:last]])
		xx2 = np.minimum(x2[i], x2[idxs[:last]])
		yy2 = np.minimum(y2[i], y2[idxs[:last]])

		w = np.maximum(0, xx2 - xx1 + 1)  # ancho de las intersecciones
		h = np.maximum(0, yy2 - yy1 + 1)  # alto de las intersecciones

		overlap = (w * h) / area[idxs[:last]]
		iou_overlap = np.array([intersection_over_union(boxes[i], b) for b in boxes[idxs[:last]]])

		# idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlap_thresh)[0])))
		idxs = np.delete(idxs, np.concatenate(([last], np.where(iou_overlap > iou_thresh)[0])))
	return pick


def box_area(box):
	x1, y1, x2, y2 = box
	return (x2 - x1) * (y2 - y1)


def box_center(box):
	x1, y1, x2, y2 = box
	return (x2 - x1) // 2, (y2 - y1) // 2


def screen_resolution():
	import tkinter
	root = tkinter.Tk()
	width = root.winfo_screenwidth()
	height = root.winfo_screenheight()
	return width, height


def stack_images(images, cols=3, resize=True):
	import math
	sw, sh = screen_resolution()  # resolución de la pantalla
	n = len(images)  # cantidad de imágenes
	cols = min(n, cols)  # limitar el número de columnas en caso de que sean menos imágenes
	rows = math.ceil(n / cols)  # cantidad de filas
	if resize:
		nsize = (int((sw - 50) / cols), int((sh - 80) / rows))  # nuevo tamaño de cada imagen para que quepan en pantalla
		images = [cv.resize(img, nsize) for img in images]  # cambiar el tamaño de todas las imágenes

	# rellenar con imágenes en negro
	total_imgs = cols * rows
	count_fill = total_imgs - n  # cantidad a rellenar
	if count_fill > 0:
		shape = images[0].shape
		dtype = images[0].dtype
		black_img = np.zeros(shape, dtype)
		for _ in range(count_fill):
			images.append(black_img)

	new_shape = np.concatenate(((rows, cols), images[0].shape))
	images = np.array(images)
	reshaped = images.reshape(new_shape)

	vstacks = []
	for row_imgs in reshaped:
		row_stack = np.hstack(row_imgs)
		vstacks.append(row_stack)

	stack = np.vstack(vstacks)
	return stack


def stack_and_write(imgs_path, out):
	images = [cv.imread(img) for img in imgs_path]

	stack = stack_images(images)
	cv.imwrite(out, stack)


def take_skip(iterable, take, skip):
	"""
	Método para modificar la manera de iterar sobre una estructura de datos iterable, de manera que se tomen 'take' elementos
	y se ignoren 'skip' elementos de manera sucesiva. Ejemplo: si se tiene la lista l=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10] y se
	invoca take_skip(l, 3, 4), la salida sería un generador que devuelve los elementos [1, 2, 3, 8, 9, 10]
	:param self:
	:param iterable:
	:param take:
	:param skip:
	:return:
	"""
	assert take > 0, 'El parámetro take tiene que ser mayor que 0.'
	temp_take = take
	temp_skip = skip
	for x in iterable:
		if temp_take > 0 or skip == 0:
			yield x
			temp_take -= 1
		else:
			if temp_skip > 1:
				temp_skip -= 1
			else:
				temp_take = take
				temp_skip = skip


def mk_string(collection, sep=', ', start='', end=''):
	ret = start
	for item in collection:
		ret = ret + str(item) + sep
	# Removing the last inserted separator.
	ret = ret[:len(ret) - len(sep)]
	return ret + end


def shutdown():
	os.system('shutdown /p /f')


def download_file(url, output):
	import requests
	r = requests.get(url)
	with open(output, 'wb') as f:
		f.write(r.content)


def download_files(dict_url_output):
	import requests
	with requests.Session() as s:
		i = 0
		for url, output in dict_url_output.items():
			r = s.get(url)
			with open(output, 'wb') as f:
				f.write(r.content)
			i += 1
			if i % 250 == 0: print('downloaded {} images'.format(i))
