import json
import re
import random

import boto.sqs
from boto.sqs.message import Message

class ImageSharerMessage(object):
    def __init__(self, j):
		self.__dict__ = json.loads(j)

keyre = re.compile('^AWSAccessKeyId=(.*)$')

def getKeys(file):
	with open(file,'r') as inf:
		hdr = inf.readline()
		
		# JSON format
		if hdr[0] == '{':
			inf.seek(0)
			return json.load(inf)
		
		# Root key format
		if keyre.match(hdr):
			out = dict()
			while hdr:
				parts = hdr.split('=')
				out[parts[0]] = parts[1].strip()
				hdr = inf.readline();
			return {
				'aws_access_key_id' : out['AWSAccessKeyId'], 
				'aws_secret_access_key' : out['AWSSecretKey']
			}
		# Colon format
		elif hdr[0] == '#':
			while hdr[0] == '#':
				hdr = inf.readline()
			out = dict()
			while hdr:
				parts = hdr.split(':')
				out[parts[0]] = parts[1].strip()
				hdr = inf.readline();
			return {
				'aws_access_key_id' : out['accessKeyId'], 
				'aws_secret_access_key' : out['secretKey']
			}
		
		# IAM format
		else:
			keys = inf.readline().split(',')
			return {
				'aws_access_key_id' : keys[1].strip(), 
				'aws_secret_access_key' : keys[2].strip()
			}


keys = getKeys('/home/ubuntu/credentials/amazon_dev-01_key.csv')
region = 'us-west-2'
queue_name = 'imagesharerresizequeue'
bucket_name = 'imagesharerresizebucket'

if not queue_name: raise Exception('You must set a queue name.')
if not bucket_name: raise Exception('You must set a bucket name.')

sqs = boto.sqs.connect_to_region(region, **keys)
s3 = boto.s3.connect_to_region(region, **keys)
queue = sqs.get_queue(queue_name) or sqs.create_queue(queue_name)
bucket = s3.lookup(bucket_name) or s3.create_bucket(bucket_name, location=region)
