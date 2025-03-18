import boto3
import uuid
import urllib
import os

s3_bucket = os.getenv('S3_BUCKET')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

def upload(image_data, file_extension):
  s3_client = boto3.resource(
      's3',
      endpoint_url='https://storage.yandexcloud.net',
      aws_access_key_id=aws_access_key_id,
      aws_secret_access_key=aws_secret_access_key
  )
  
  key = f'users/{str(uuid.uuid4())}{file_extension}'
  s3_client.Object(s3_bucket, key).put(Body=image_data)
  url = f'https://{s3_bucket}.s3.amazonaws.com/{urllib.parse.quote(key)}'

  return url
