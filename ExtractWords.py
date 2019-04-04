import math
import cv2
import operator
import numpy as np
from create__kernel import createKernel



def prepareImg(img, height):
    """convert given image to grayscale image (if needed) and resize to desired height"""
    assert img.ndim in (2, 3)
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img
    # h = img.shape[0]
    # factor = height / h
    # return cv2.resize(img, dsize=None, fx=factor, fy=factor)

def append_dict(group, index, group_dict,bbox):
	    if int(group) in group_dict.keys():
	        # print('in keys')
	        group_dict[group].append(bbox[index])
	    else:
	        # print('creating key')
	        group_dict[group] = []
	        group_dict[group].append(bbox[index])

def wordSegmentation(img, kernelSize=25, sigma=11, theta=7, minArea=0):

    # apply filter kernel
    kernel = createKernel(kernelSize, sigma, theta)
    imgFiltered = cv2.filter2D(img, -1, kernel, borderType=cv2.BORDER_REPLICATE).astype(np.uint8)
    (_, imgThres) = cv2.threshold(imgFiltered, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    imgThres = 255 - imgThres

    # find connected components. OpenCV: return type differs between OpenCV2 and 3
    if cv2.__version__.startswith('3.'):
        (_, components, _) = cv2.findContours(imgThres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)	
    else:
        (components, _) = cv2.findContours(imgThres, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # append components to result
    res = []
    for c in components:
        # skip small word candidates
        if cv2.contourArea(c) < minArea:
            continue
        # append bounding box and image of word to result list
        currBox = cv2.boundingRect(c) # returns (x, y, w, h)
        (x, y, w, h) = currBox
        currImg = img[y:y+h, x:x+w]
        res.append((currBox, currImg))

    # return list of words, sorted by x-coordinate
    return sorted(res, key=lambda entry:entry[0][1])

def create_groups(bbox):
    group = 0
    group_list = []
    group_dict = {}
    i = 0
    flag = 'unchanged'
    test = bbox[0][0] + bbox[0][2]
#     print(test)

    for index, box in enumerate(bbox):
        if index + 1 == len(bbox):
            break
        x, y, w, h = box
        # print(bbox[index][0] + bbox[index][2], bbox[index+1][0])
        if abs(bbox[index][0] + bbox[index][2] - bbox[index+1][0]) <= 25:
            # print(abs(bbox[index][0] + bbox[index][2] - bbox[index+1][0]))
            append_dict(group, index, group_dict, bbox)
            group_list.append(group)
            # print('if')
        else:
            # print('else')
            group_list.append(group)
            append_dict(group, index, group_dict,bbox)
            group = group + 1
    append_dict(group, index, group_dict,bbox)
    group_list.append(group)
    # print([group_list], len(group_list))
#     print(group_dict)
    return group_dict


def getBoundingbox(result):
	bbox = list(zip(*result))[0]
	group = 0
	group_list = []
	group_dict = {}
	i = 0
	flag = 'unchanged'
	test = bbox[0][1]

	BBOX = bbox
	for index, box in enumerate(bbox):
	    if index + 1 == len(bbox):
	        break
	    x, y, w, h = box
	    if abs(test - bbox[index+1][1]) <= 15:
	        # print(abs(test - bbox[index+1][1]))
	        append_dict(group, index, group_dict,bbox)
	        group_list.append(group)
	    else:
	        flag = 'changed'
	        group = group + 1
	        test = bbox[index+1][1]
	#         append_dict(group, index, group_dict)
	    if flag == 'changed':
	        group_list.append(group - 1)
	        flag = 'unchanged'
	        append_dict(group-1, index, group_dict,bbox)
	group_list.append(group)
	# print([group_list], len(group_list))
	# print(group_dict)

	group_dict = {}
	for index, groupId in enumerate(group_list):
	    # print(group_dict.keys())
	    if int(groupId) in group_dict.keys():
	        # print('in keys')
	        group_dict[groupId].append(bbox[index])
	    else:
	        # print('creating key')
	        group_dict[groupId] = []
	        group_dict[groupId].append(bbox[index])
	    # print(group_dict)
	# 

	GROUP_DICT = group_dict
	SUB_GROUPS = []
	for i in GROUP_DICT:
	#     print(i, GROUP_DICT[i])
	    bbox = sorted(GROUP_DICT[i], key=lambda entry:entry[0])
	    # print(bbox)
	    sub_group_dict = create_groups(bbox)
	    SUB_GROUPS.append(sub_group_dict)
	#     print("GROUP_DICT: ", GROUP_DICT[i])
	#     print("SUB_GROUPS ", SUB_GROUPS)
	#     print('\n')

	# print('SUB_GROUPS', SUB_GROUPS, len(SUB_GROUPS))
	# print('\n \n \n')

	FINAL_BBOXES = []
	for t in SUB_GROUPS:
	    for i in t:
	#         print(t[i])
	        X1 = min(list(zip(*t[i]))[0])
	        Y1 = min(list(zip(*t[i]))[1])
	        X2 = max(tuple(map(operator.add,list(zip(*t[i]))[0], list(zip(*t[i]))[2])))
	        Y2 = max(tuple(map(operator.add,list(zip(*t[i]))[1], list(zip(*t[i]))[3])))
	        FINAL_BBOXES.append((X1, Y1, X2, Y2))
	#     print("\n")
	#     print(i)
	return FINAL_BBOXES




