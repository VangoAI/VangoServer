import os
import boto3
import uuid
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

session = boto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="us-west-2"
)

dynamodb = session.resource('dynamodb')
users_table = dynamodb.Table("Users")
models_table = dynamodb.Table("Models")

models = [
    { 'name': 'Stable Diffusion XL v1.0', 's3_url': 'https://vango-models.s3.us-west-2.amazonaws.com/sd_xl_base_1.0.safetensors' },
]

response = users_table.scan()
users = response['Items']

for user in users:
    owner_id = user['user_id']

    for model in models:
        model_id = str(uuid.uuid4())
        name = model['name']
        s3_url = model['s3_url']
        last_edited = datetime.now().isoformat() + "Z"

        models_table.put_item(
            Item={
                'model_id': model_id,
                'name': name,
                'owner_id': owner_id,
                's3_url': s3_url,
                'last_edited': last_edited
            }
        )

print("Done")
