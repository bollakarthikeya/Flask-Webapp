'''
@author: karthikeya
'''
# FLASK IMPORTS
from flask import Flask
from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for

# S3 IMPORTS
from svd.s3Components import fileDetails
from svd.s3Components import fileUpload


# OTHER IMPORTS
import os
import zipfile
from svd.config import config
from flask.helpers import send_from_directory


# THE APP
application = Flask(__name__)
app = application
app.secret_key = config['APP_SECRET_KEY']


# this is the default homepage
@app.route('/') 
def homepage():    
	return render_template('upload_image.html')


# error page when file format is invalid
@app.route('/fileFormatError')
def fileFormatError():
	errorMessage = 'invalid file format!'
	return render_template('fileFormatError.html', message = errorMessage)
    

# error page when compression fails
@app.route('/compressionFailError')
def compressionFailError():
    errorMessage = 'compression failed!'
    return render_template('compressionFailError.html', message = errorMessage)

        
# Logic to check if file extension is valid
def isValidFileExtension(filename):
	VALID_FILE_EXTENSIONS = {'jpeg', 'jpg', 'png', 'gif'}    
	entries = filename.split('.')
	isValid = entries[-1].lower() in VALID_FILE_EXTENSIONS
	return isValid


# download zip file
@app.route('/download/<path:filename>', methods = ['GET'])
def downloadFiles(filename):
	return send_from_directory(config['FILE_LOCATION'], filename, as_attachment = True)            


# FILE UPLOAD LOGIC - We will include 'POST' method only as we are uploading image as part of homepage
@app.route('/', methods = ['POST']) 
def uploadImage():    
	# get the file from form with input-type 'file' from 'upload_image.html'
	imgFile = request.files['actual_image_location_in_html_page']   
	fullFileName, actualFileName, _ = fileDetails(imgFile)
	# if invalid file format
	if not isValidFileExtension(imgFile.filename):
		flash('File format for ' + fullFileName + ' is invalid') 
		return redirect(url_for('fileFormatError'))        
	# if there's a valid file submission, store <original, compressed> files in S3
	if imgFile and isValidFileExtension(fullFileName):
		fileUploadComplete = fileUpload(imgFile)
		zipFileName = actualFileName + '.zip'
		return redirect(url_for('downloadFiles', filename = zipFileName)) if fileUploadComplete else redirect(url_for('compressionFailError'))











