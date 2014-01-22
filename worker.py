import json
import time
import StringIO
from PIL import Image
from common import bucket, queue

# Create a thumbnail from an image.
# @param image: PIL image to resize.
# @param maxWidth: Maximum width of the thumbnail.
# @param maxHeight: Maximum height of the thumbnail.
def thumbnail(image, maxWidth, maxHeight):
	# Perform some sanity checks
	if not isinstance(maxWidth, int): raise Exception('Width must be an int')
	if not isinstance(maxHeight, int): raise Exception('Height must be an int')
	if maxWidth <= 0: raise Exception('Width must not be <= 0')
	if maxHeight <= 0: raise Exception('Height must not be <= 0');
	
	# Do some wizardry to maintain the aspect ratio of the image
	width, height = image.size
	targetWidth, targetHeight = width, height
	if targetWidth > maxWidth:
		targetWidth = maxWidth
		targetHeight = (targetWidth * height) / width
	if targetHeight > maxHeight:
		targetHeight = maxHeight
		targetWidth = (targetHeight * width) / height

	# Do the actual resizing operation using the best
	# quality resampler.
	return image.resize((targetWidth, targetHeight), resample=Image.ANTIALIAS)

# Read an image from S3.
# @param name: Name of the key that has the image.
def read(name):
	key = bucket.get_key(name)
	if not key: raise Exception('no such key '+name)
	return Image.open(StringIO.StringIO(key.get_contents_as_string()))

# Save an image to S3.
# @param name: Name of the key in the bucket to use.
# @param image: PIL image to save.
# @param format: Format to save the image as (JPEG/PNG/etc.)
def write(name, image, format):
	key = bucket.new_key(name)
	buf = StringIO.StringIO()
	image.save(buf, format=format, quality=8)
	key.set_metadata('Content-Type', 'image/'+format.lower())
	key.set_contents_from_string(buf.getvalue())
	buf.close()

try:
	
	# Loop forever.
	while 1:
		
		# Read a message from the queue containing the key of
		# the image to be resized, use read() to read the image.
		# For every size of image to generated, call thumbnail()
		# to generate the image and then write() to store the
		# generated thumbnail back into S3. Good luck, have fun.

# When someone tries to break the program just quit gracefully
# instead of raising some nasty exception.
except KeyboardInterrupt:
	pass