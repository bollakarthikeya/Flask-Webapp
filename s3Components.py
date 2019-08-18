'''
@author: karthikeya
'''

import os
import io
import cv2
import boto3 
import zipfile
import numpy as np
from svd.config import config
from svd.compress import compressImage


# S3 initializations
s3 = boto3.resource('s3', aws_access_key_id = config['ACCESS_ID'], aws_secret_access_key = config['SECRET_KEY'])
s3Client = boto3.client('s3', aws_access_key_id = config['ACCESS_ID'], aws_secret_access_key = config['SECRET_KEY'])


# function to extract file name and file extension
def fileDetails(imgFile):
	fullFileName = imgFile.filename
	fileExtension = fullFileName.split('.')[-1]
	actualFileName = '.'.join(fullFileName.split('.')[:-1])
	return (fullFileName, actualFileName, fileExtension)


# zip all files in 'files' folder
def zipFiles(dirName, zipFileName):    
	# get all file paths
	filePaths = []    
	for root, _, files in os.walk(dirName):        
		for f in files:
			getFilePath = os.path.join(root, f)
			filePaths.append(getFilePath)  
	# add all files (using file paths) to a zip file
	myZipFile = zipfile.ZipFile(config['FILE_LOCATION'] + zipFileName, 'w')    
	with myZipFile:
		for f in filePaths:
			myZipFile.write(f)


# function to upload file to AWS S3
def fileUpload(imgFile):
	try:
		fullFileName, actualFileName, _ = fileDetails(imgFile)     
		# reconstruct the image from request's byte stream as follows 
		# https://gist.github.com/mjul/32d697b734e7e9171cdb
		imageByteArray = io.BytesIO()
		imgFile.save(imageByteArray)
		imageData = np.fromstring(imageByteArray.getvalue(), dtype=np.uint8)
		actualImage = cv2.imdecode(imageData, 1)  
		# pass the reconstructed original image for compression
		compressedImageMatrix, U, S, V = compressImage(actualImage)
		# delete any/all old files from 'files' folder before we start saving
		for f in os.listdir(config['FILE_LOCATION']):
			os.remove(os.path.join(config['FILE_LOCATION'], f))
		# store compressed image, matrices U, S, V so as to be uploaded to S3              
		np.save(config['FILE_LOCATION'] + 'U.npy', U)
		np.save(config['FILE_LOCATION'] + 'S.npy', S)
		np.save(config['FILE_LOCATION'] + 'V.npy', V)        
		cv2.imwrite(config['FILE_LOCATION'] + 'reconstructed_' + fullFileName, compressedImageMatrix)
		# zip all files in 'files' folder to download
		zipFileName = actualFileName + '.zip'
		zipFiles(config['FILE_LOCATION'], zipFileName)
		# upload files to S3
		s3.Object(config['BUCKET_NAME'], actualFileName + '/U.npy').upload_file(config['FILE_LOCATION'] + 'U.npy')    
		s3.Object(config['BUCKET_NAME'], actualFileName + '/S.npy').upload_file(config['FILE_LOCATION'] + 'S.npy')
		s3.Object(config['BUCKET_NAME'], actualFileName + '/V.npy').upload_file(config['FILE_LOCATION'] + 'V.npy')
		s3.Object(config['BUCKET_NAME'], actualFileName + '/reconstructed_' + fullFileName).upload_file(config['FILE_LOCATION'] + 'reconstructed_' + fullFileName)
		# delete files from 'files' folder once the upload is complete (with the exception of zip file as it needs to be downloaded)
		os.remove(config['FILE_LOCATION'] + 'U.npy')
		os.remove(config['FILE_LOCATION'] + 'V.npy')
		os.remove(config['FILE_LOCATION'] + 'S.npy')
		os.remove(config['FILE_LOCATION'] + 'reconstructed_' + fullFileName)
             
	except Exception:
		return False 
    
	return True

