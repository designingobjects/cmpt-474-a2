import boto.ec2
import boto.sqs
import boto.s3
import json

def getKeys(file):
	with open(file,'r') as inf:
		hdr = inf.readline()
		keys = inf.readline().split(',')
	return {
		'aws_access_key' : keys[1], 
		'aws_secret_access_key' : keys[2]
	}


keys = getKeys('credentials.csv')
region = 'us-west-2'
queue_name = None
bucket_name = None

if not queue_name: raise Exception('You must set a queue name.')
if not bucket_name: raise Exception('You must set a bucket name.')

sqs = boto.sqs.connect_to_region(region, **keys)
s3 = boto.s3.connect_to_region(region, **keys)
queue = sqs.get_queue(queue_name) or sqs.create_queue(queue_name)
bucket = s3.lookup(bucket_name) or s3.create_bucket(bucket_name, location=region)
