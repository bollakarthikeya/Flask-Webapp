'''
@author: karthikeya
'''

import os
import io
import cv2
import boto3 
import svd.main
import svd.config
import svd.compress
import numpy as np


# S3 initializations
s3 = boto3.resource('s3',
                    aws_access_key_id = svd.config.config['ACCESS_ID'],
                    aws_secret_access_key = svd.config.config['SECRET_KEY'])

s3Client = boto3.client('s3',
                        aws_access_key_id = svd.config.config['ACCESS_ID'],
                        aws_secret_access_key = svd.config.config['SECRET_KEY'])


# function to extract file name and file extension
def fileDetails(file):
    fullFileName = file.filename
    fileExtension = fullFileName.split('.')[-1]
    actualFileName = '.'.join(fullFileName.split('.')[:-1])
    return (fullFileName, actualFileName, fileExtension)


# function to upload file to AWS S3
def fileUpload(file):
    try:
        fullFileName, actualFileName, _ = fileDetails(file)     
        # reconstruct the image from request's byte stream as follows 
        # https://gist.github.com/mjul/32d697b734e7e9171cdb
        imageByteArray = io.BytesIO()
        file.save(imageByteArray)
        imageData = np.fromstring(imageByteArray.getvalue(), dtype=np.uint8)
        actualImage = cv2.imdecode(imageData, 1)    
        # pass the reconstructed original image for compression
        _, matrices = svd.compress.compressImage(actualImage)
        compressedImageMatrix, U, S, V = matrices
        # delete any/all old files from 'files' folder before we start saving
        for f in os.listdir(svd.config.config['FILE_LOCATION']):
            os.remove(os.path.join(svd.config.config['FILE_LOCATION'], f))
        # store compressed image, matrices U, S, V so as to be uploaded to S3              
        np.save(svd.config.config['FILE_LOCATION'] + 'U.npy', U)
        np.save(svd.config.config['FILE_LOCATION'] + 'S.npy', S)
        np.save(svd.config.config['FILE_LOCATION'] + 'V.npy', V)        
        cv2.imwrite('./files/reconstructed_' + fullFileName, compressedImageMatrix)
        # zip all files in 'files' folder to download
        zipFileName = actualFileName + '.zip'
        svd.main.zipFiles('files', zipFileName)           
        # upload files to S3
        s3.Object(svd.config.config['BUCKET_NAME'], actualFileName + '/U.npy').upload_file(svd.config.config['FILE_LOCATION'] + 'U.npy')    
        s3.Object(svd.config.config['BUCKET_NAME'], actualFileName + '/S.npy').upload_file(svd.config.config['FILE_LOCATION'] + 'S.npy')
        s3.Object(svd.config.config['BUCKET_NAME'], actualFileName + '/V.npy').upload_file(svd.config.config['FILE_LOCATION'] + 'V.npy')
        s3.Object(svd.config.config['BUCKET_NAME'], actualFileName + '/reconstructed_' + fullFileName).upload_file(svd.config.config['FILE_LOCATION'] + 'reconstructed_' + fullFileName)
        # delete files from 'files' folder once the upload is complete (with the exception of zip file as it needs to be downloaded)
        os.remove(svd.config.config['FILE_LOCATION'] + 'U.npy')
        os.remove(svd.config.config['FILE_LOCATION'] + 'V.npy')
        os.remove(svd.config.config['FILE_LOCATION'] + 'S.npy')
        os.remove(svd.config.config['FILE_LOCATION'] + 'reconstructed_' + fullFileName)
             
    except Exception:
        return False 
    
    return True
