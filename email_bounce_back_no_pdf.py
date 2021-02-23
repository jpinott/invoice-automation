
import boto3
import json
from botocore.exceptions import ClientError


def lambda_handler(event, context):
	s3 = boto3.client('s3')
	b = ('cfaitinnovnp.autoinvoice.raw-email')
	emailName = event['Records'][0]['s3']['object']['key']
	resource = s3.get_object(Bucket=b, Key=emailName)
	text = (resource['Body'].read())
	##the above pulls the text body from an email trigger and puts it into var text
	return
	