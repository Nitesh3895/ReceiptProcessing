import os
import cv2
from ExtractWords import wordSegmentation, prepareImg, getBoundingbox
import pytesseract
from spellchecker import SpellChecker
import re
import pdb

spell = SpellChecker()
def main():
	"""reads images from data/ and outputs the word-segmentation to out/"""

	# read input images from 'in' directory
	imgFiles = os.listdir('../data/')
	main_list = []
	main_list_boxes = []

	for (i,f) in enumerate(imgFiles):
		print('Extracting words from sample %s'%f)
		raw_img = cv2.imread('../data/%s'%f)
		im_height, im_width, im_channels = raw_img.shape	
		
		# read image, prepare it by resizing it to fixed height and converting it to grayscale
		img = prepareImg(raw_img, 50)

		res = wordSegmentation(img, kernelSize=25, sigma=11, theta=7, minArea=100)
		BBOXES = getBoundingbox(res)
		# write output to 'out/inputFileName' directory
		# if not os.path.exists('../out/%s'%f):
		# 	os.mkdir('../out/%s'%f)
		
		extend_ratio_h = 0.1
		extend_ratio_w = 0.1
		# iterate over all segmented words
		invoice_flag = 0
		print('Extracted %d words'%len(res))
		lis0ftext = []
		lis0fbboxes = []
		for j, (x1, y1, x2, y2) in enumerate(BBOXES):
			
			(left, right, top, bottom) = (x1 , x2 , y1 , y2)
			new_top = top-((bottom-top)*extend_ratio_h)
			new_bottom = bottom+((bottom-top)*extend_ratio_h)
			new_left = left-((right-left)*extend_ratio_w)
			new_right = right+((right-left)*extend_ratio_w)

			if new_top < 0:
				new_top = 0
			if new_bottom > im_height:
				new_bottom = im_height
			if new_left < 0:
				new_left = 0
			if new_right > im_width:
				new_right = im_width
			x1, x2, y1, y2 = int(new_left), int(new_right), int(new_top), int(new_bottom)


			wordImg = raw_img[y1:y2, x1:x2]
			config = ("-l eng --oem 1 --psm 7")
			text = pytesseract.image_to_string(wordImg, config=config)
			# if text == "":
			# 	continue
			# lis0ftext.append((text, (x1, x2, y1, y2)))
			lis0ftext.append(text)
			lis0fbboxes.append((x1, x2, y1, y2))
			# print(text)

			


			# cv2.imwrite('../out/%s/%d.png'%(f, j), wordImg) # save word
			if text != "":
				cv2.rectangle(raw_img,(x1,y1),(x2,y2),(0,0,255),3) # draw bounding box in summary image
		main_list.append(lis0ftext)
		main_list_boxes.append(lis0fbboxes)
		


		# cv2.imwrite('../out/%s/summary.png'%f, img)
		cv2.imwrite('../out/summary%s'%f, raw_img)
	# main_list.append(lis0ftext)
	IC = ['invoice', 'INVOICE', 'Invoice', 'Invo', 'invo']
	main_temp = []
	main_temp_bboex = []
	for index_i, i in enumerate(main_list):
	#     print(i)
	    i_temp = []
	    i_temp_bboex = []
	    for index_j, j in enumerate(i):
	        if j != '':
	            i_temp.append(j)
	            i_temp_bboex.append(main_list_boxes[index_i][index_j])
	    main_temp.append(i_temp)
	    main_temp_bboex.append(i_temp_bboex)
	MAIN_TEXT = main_temp
	MANI_BBOXES = main_temp_bboex

	
	for i_ind, i in enumerate(MAIN_TEXT):
		# for j_ind, (j, bbox) in enumerate(i): 
		for j_ind, j in enumerate(i): 
			if (IC[0] in j or IC[1] in j or IC[2] in j or IC[3] in j or IC[4] in j) and len(list(j)) <=100:
				if len(re.findall('\d+.\d+|\.|\,|\-', j)) != 0 and len(re.findall('\$', j))==0:
					if '#' in j:
						j = j.replace(' ', '')
						invoice_no = j.split('#')[-1].split(' ')[0]
						invoice_no = re.findall('.+\d+', invoice_no)[0]
						# print('INVOICE NO',invoice_no, bbox)
						print('INVOICE NO',invoice_no, MANI_BBOXES[i_ind][j_ind])
						INVOICE_NO = invoice_no
						break
					temp = re.findall('\d+', j)
					if len(re.findall('\d+', j)) == 1:
						print('INVOICE NO',temp[0], MANI_BBOXES[i_ind][j_ind])
						# print('INVOICE NO',temp[0], bbox)
						INVOICE_NO = temp[0]
						break
				else:
					try:
						temp = re.findall('\d+' ,i[j_ind+1])
						if len(temp) == 1 and len(temp[0]) == len(i[j_ind+1]):
							print('INVOICE NO',i[j_ind+1], MANI_BBOXES[i_ind][j_ind])
							# print('INVOICE NO',i[j_ind+1], bbox)
							INVOICE_NO = i[j_ind+1]
							break
					except:
						pass


	for i_ind, i in enumerate(MAIN_TEXT):
		# for j_ind, (j, bbox) in enumerate(i):
		for j_ind, j in enumerate(i): 
			temp1 = re.findall('\d+/\d+.+/\d+', j)
			if len(temp1) != 0:
				# print('DATE1',temp1, bbox)
				print('DATE',temp1, MANI_BBOXES[i_ind][j_ind])
				DATE = temp1
				break
			temp1 = re.findall('\d{4}-\d{2}-\d{2}', j)
			if len(temp1) != 0:
				# print('DATE2',temp1, bbox)
				print('DATE',temp1, MANI_BBOXES[i_ind][j_ind])
				DATE = temp1
				break
			temp1 = re.findall('\d{2} \w+ \d{4}', j)
			if len(temp1) != 0:
				# print('DATE3',temp1, bbox)
				print('DATE',temp1, MANI_BBOXES[i_ind][j_ind])
				DATE = temp1
				break
			temp1 = re.findall('date', j, re.IGNORECASE)
			if len(temp1) != 0:
				try:
					temp1 = i[j_ind].replace(',','')
					temp2 = re.findall('\d+ \w+ \d{4}|\w+ \d+ \d{4}', temp1)
					
					
					if len(temp2) != 0:
						# print('DATE4',temp2, bbox)
						print('DATE',temp2, MANI_BBOXES[i_ind][j_ind])
						break
					temp1 = i[j_ind+1].replace(',','')
					temp2 = re.findall('\d+ \w+ \d{4}|\w+ \d+ \d{4}', temp1)
					if len(temp2) != 0:
						DATE = temp2
						# print('DATE5',temp2, bbox)
						print('DATE',temp2, MANI_BBOXES[i_ind][j_ind])
				except:
					pass
	# print(main_list)

if __name__ == '__main__':
	main()