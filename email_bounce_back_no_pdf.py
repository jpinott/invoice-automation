import boto3
import os
import json
from botocore.exceptions import ClientError
import re
import base64
from base64 import b64decode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def lambda_handler(event, context):
	s3 = boto3.client('s3')
	b = ('cfaitinnovnp.autoinvoice.raw-email')
	emailName = event['Records'][0]['s3']['object']['key']
	resource = s3.get_object(Bucket=b, Key=emailName)
	text = (resource['Body'].read().decode("utf-8"))
	s3.delete_object(Bucket=b, Key=emailName)
	##the above pulls the text body from an email trigger and puts it into var text
	regex = r"(?s)(Content-Transfer-Encoding: base64)([^-]*)"
	client = boto3.client('ses',region_name='us-east-1')
	emailTo = (re.search(r"Return-Path: <(.*)>", text).group(1))
	emailFrom = 'invoice@rev.cfadevelop.com'
	region = 'us-east-1'
	try:
		result = re.search(regex, text)
		pdfBlock = (result.group(2))
		bytes = b64decode(pdfBlock)
		if bytes[0:4] != b'%PDF':
		  raise ValueError('Missing the PDF file signature')
		
		# Write the PDF contents to a local file
		pdfName = re.search(r"Content-Type: application/pdf; name=(.*)", text).group(1)
		pdfName = pdfName[1:(len(pdfName)-1)]
		f = open('/tmp/'+pdfName, 'wb')
		f.write(bytes)
		f.close()
		msg = MIMEMultipart('mixed')
		# Add subject, from and to lines.
		msg['Subject'] = "PDF Test Back" 
		msg['From'] = emailFrom 
		msg['To'] = emailTo
		BODY_TEXT = "Hello,\r\nPlease see the attached file for the soon-to-be routed PDF."
		# The HTML body of the email.
		BODY_HTML = """\
		<html>
		<head></head>
		<body>
		<h1>Hello!</h1>
		<p>Please see the attached file for a list of customers to contact.</p>
		</body>
		</html>
		"""
		CHARSET = "UTF-8"
		msg_body = MIMEMultipart('alternative')
		ATTACHMENT = '/tmp/' + pdfName
		
		# Encode the text and HTML content and set the character encoding. This step is
		# necessary if you're sending a message with characters outside the ASCII range.
		textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
		htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
		
		# Add the text and HTML parts to the child container.
		msg_body.attach(textpart)
		msg_body.attach(htmlpart)
		
		# Define the attachment part and encode it using MIMEApplication.
		att = MIMEApplication(open(ATTACHMENT, 'rb').read())
		att.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT))
		
		# Attach the multipart/alternative child container to the multipart/mixed
		# parent container.
		msg.attach(msg_body)
		
		# Add the attachment to the parent container.
		msg.attach(att)
		try:
		    #Provide the contents of the email.
		    response = client.send_raw_email(
		        Source=emailFrom,
		        Destinations=[
		            emailTo
		        ],
		        RawMessage={
		            'Data':msg.as_string(),
		        }
		    )
		# Display an error if something goes wrong.	
		except ClientError as e:
		    print(e.response['Error']['Message'])
	except:
		##sends the bounce back no pdf email
		subject = "[Invoice Automation] No Invoice Attached"
		body_text = ("Hello,\n There was no invoice attached to the last email "
		"sent to invoice@rev.cfadevelop.com. Please resend with a PDF attachment.")
		html_text = """<html>
		<head></head>
		<body>
		  <h1>Hello,</h1>
		  <p>There was no invoice attached to the last email
		sent to invoice@rev.cfadevelop.com. Please resend with a PDF attachment.</p>
		</body>
		</html>"""
		charset = "UTF-8"
		try:
			    response = client.send_email(
		        Destination={
		            'ToAddresses': [
		                emailTo,
		            ],
		        },
		        Message={
		            'Body': {
		                'Html': {
		                    'Charset': charset,
		                    'Data': html_text,
		                },
		                'Text': {
		                    'Charset': charset,
		                    'Data': body_text,
		                },
		            },
		            'Subject': {
		                'Charset': charset,
		                'Data': subject,
		            },
		        },
		        Source=emailFrom
		    )
		# Display an error if something goes wrong.	
		except ClientError as e:
		    print(e.response['Error']['Message'])
	return