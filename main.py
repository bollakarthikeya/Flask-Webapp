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
import svd.s3Components

# OTHER IMPORTS
import os
import zipfile
import svd.config
from flask.helpers import send_from_directory


# THE APP
app = Flask(__name__)
app.secret_key = svd.config.config['APP_SECRET_KEY']


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


# zip all files in 'files' folder
def zipFiles(dirName, zipFileName):    
    # get all file paths
    filePaths = []    
    for root, _, files in os.walk(dirName):        
        for file in files:
            getFilePath = os.path.join(root, file)
            filePaths.append(getFilePath)    
    # add all files (using file paths) to a zip file
    myZipFile = zipfile.ZipFile(svd.config.config['FILE_LOCATION'] + zipFileName, 'w')    
    with myZipFile:
        for file in filePaths:
            myZipFile.write(file)


# download zip file
@app.route('/download/<filename>', methods = ['GET'])
def downloadFiles(filename):
    return send_from_directory(svd.config.config['FILE_LOCATION'], filename, as_attachment = True)            


# FILE UPLOAD LOGIC - We will include 'POST' method only as we are uploading image as part of homepage
@app.route('/', methods = ['POST']) 
def uploadImage():    
    # get the file from form with input-type 'file' from 'upload_image.html'
    file = request.files["actual_image_location_in_html_page"]   
    fullFileName, actualFileName, _ = svd.s3Components.fileDetails(file)
    # if invalid file format
    if not isValidFileExtension(file.filename):
        flash('File format for ' + fullFileName + ' is invalid') 
        return redirect(url_for('fileFormatError'))        
    # if there's a valid file submission, store <original, compressed> files in S3
    if file and isValidFileExtension(fullFileName):
        fileUploadComplete = svd.s3Components.fileUpload(file)
        zipFileName = actualFileName + '.zip'
        return redirect(url_for('downloadFiles', filename = zipFileName)) if fileUploadComplete else redirect(url_for('compressionFailError'))











