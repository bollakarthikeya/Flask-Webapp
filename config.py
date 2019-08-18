
import os

# dictionary to store configuration details
config = dict()

# S3 bucket name
config['BUCKET_NAME'] = 'YOUR BUCKET NAME'

# S3 bucket access id
config['ACCESS_ID'] = 'AWS ACCESS ID'

# S3 bucket secret key
config['SECRET_KEY'] = 'AWS SECRET KEY'

# secret key for the application
config['APP_SECRET_KEY'] = 'STRING OF YOUR CHOICE AS PASSSWORD'

# storage location for files created during compression in terms of absolute path
folderName = 'svd/files/'
folderPath = os.path.dirname(os.path.abspath(__name__))
config['FILE_LOCATION'] = folderPath + '/' + folderName
