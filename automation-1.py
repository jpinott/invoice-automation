import base64
import tika
import re
from base64 import b64decode
from tika import parser

# this function will convert base64 text into a pdf and save it on your computer
def b64_topdf(b64text):
    bytes = b64decode(b64text, validate = True)
    if bytes[0:4] != b'%PDF':
        raise ValueError('Missing the PDF file signature')
    f = open('file.pdf', 'wb')
    f.write(bytes)
    f.close()


# getting text file with email contents, extracting only base64 text & calling conversion function
with open('/Users/julianny.pinottvel/Downloads/pdf2base64', 'r') as file:
    data = file.read().replace('\n', '')

regex = r"(?s)(Content-Transfer-Encoding: base64)([^-]*)"
result = re.search(regex, data)
convertible = result.group(2)
b64_topdf(convertible)