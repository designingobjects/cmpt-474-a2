import string
from PIL import Image
from bottle import route, request, run
from boto.s3.key import Key
from common import bucket, queue

# All the sizes our app supports
sizes = { 
	'small': { 'width': 100, 'height': 100 },
	'medium': { 'width': 300, 'height': 300 },
	'large': { 'width': 600, 'height': 600 }
}

# Generate a unique id to be used in an S3 bucket.
def generate_id():
	raise Exception('Implement me!')


# Write a message to SQS containing enough information to 
# create all the necessary thumbnails from a worker.
def notify_worker(id, sizes):
	raise Exception('Implement me!')	


# Generate a URL for a resource in an S3 bucket
def url(name):
	return Key(bucket, name).generate_url(expires_in=-1,query_auth=False)


# Executed when you curl -XPOST http://your-instance.com/
@route('/', method='POST')
def upload():
	
	# Get the uploaded image from the user
	upload = request.files.get('image')

	# If the user didn't actually send anything then error
	if not upload: return 'no image'

	# Set some variables for convenience; upload.file is a
	# file-descriptor like object representing the data the
	# user has uploaded.
	file = upload.file
	image = None

	# Attempt to open the file the user uploaded as an image
	# and if it fails then tell the user they've uploaded an
	# invalid image.
	try:
		image = Image.open(file)
	except:
		return 'invalid image'

	# Since Image.open moves the file pointer as it checks the
	# validity of the image, we need to rewind it for when we
	# place all the data into the bucket.
	file.seek(0)

	# Generate a new id and key to place the image into.
	id = generate_id()
	
	# Store the original image into the bucket.
	key = bucket.new_key(id+'-original')

	# Set the Content-Type metadata to the appropriate mime-type so
	# that when your data is served over S3 the browser can display
	# the image properly (the default is application/octet-stream).
	key.set_metadata('Content-Type', 'image/'+image.format.lower())

	# Finally load the image data into S3.
	key.set_contents_from_file(file)

	# Send a message to a worker to begin processing the resizing
	# of the freshly minted image.
	notify_worker(id, sizes)

	# Return the URLs to the images.
	return  { key: url(id+'-'+key) for key in ['original'] + sizes.keys() }



# Listen on all interfaces on port 80; note that on Linux port 80
# falls into the list of privileged ports and thus you must either
# run your script as root or setup some system whereby the script
# is allocated the port and then drops its privileges.
run(host='0.0.0.0', port=80)
