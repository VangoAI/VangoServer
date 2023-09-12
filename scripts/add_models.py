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
models_table = dynamodb.Table("Models")

models = [
    { 'name': 'Stable Diffusion XL v1.0', 's3_url': 'https://vango-models.s3.us-west-2.amazonaws.com/sd_xl_base_1.0.safetensors', 'owner_id': '0dea49ef-abf9-4e73-8e2c-34fc529e2c9c', 'type': 'Checkpoint' },
]

for model in models:
    model_id = str(uuid.uuid4())
    name = model['name']
    type = model['type']
    s3_url = model['s3_url']
    owner_id = model['owner_id']
    last_edited = datetime.now().isoformat() + "Z"

    models_table.put_item(
        Item={
            'model_id': model_id,
            'name': name,
            'type': type,
            'owner_id': owner_id,
            's3_url': s3_url,
            'last_edited': last_edited
        }
    )

print("Done")
