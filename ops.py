
from glob import glob 
import os
import tensorflow as tf
import numpy as np
import cv2 

#def class_activation_map(classmap, image):

def load_image(path, args):
	img = cv2.resize(cv2.imread(path), (args.input_width,args.input_height))
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	return img / 127.5 - 1

def load_tr_data(args):
	print "Preparing Training Data..."

	folders = os.path.join(args.data, "train")
	folders = glob(folders+"/*")
	
	images = []
	boxes = []
	labels = []
	labels_dict = {}
	for idx, folder in enumerate(folders):
		txt_path = os.path.join(folder,folder.split('/')[-1]+"_boxes.txt")
		fb = open(txt_path, "r")
		data = fb.read().split('\n')
		data = data[:len(data)-1]
		labels_dict[folder.split('/')[-1]] = idx
		
		for line in data:
			line = line.split('\t')
			name = line[0]
			box = line[1:]
			img_path = os.path.join(folder+"/images", name)
			# img = cv2.imread(img_path)
			images.append(img_path)
			boxes.append(box)
			labels.append(idx)

	return images, boxes, labels, labels_dict, len(labels)

def load_val_data(args, labels_dict):
	print("Preparing Validation Data...")

	path = os.path.join(args.data, "val")
	
	images = []
	boxes = []
	labels = []

	txt_path = os.path.join(path,"val_annotations.txt")
	fb = open(txt_path, "r")
	data = fb.read().split('\n')
	data = data[:len(data)-1]
	
	for line in data:
		line = line.split('\t')
		name = line[0]
		box = line[1:]
		img_path = os.path.join(path+"/images", name)

		# img = cv2.imread(img_path)
		images.append(img_path)
		boxes.append(box)
		labels.append(labels_dict[line[1]])


	return images, boxes, labels, len(labels)





