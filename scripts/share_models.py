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
model_shares_table = dynamodb.Table("ModelShares")

models = [
    { 'model_id': 'b6df4801-e932-4e28-b03a-fbb809637bd3', 'owner_id': '0dea49ef-abf9-4e73-8e2c-34fc529e2c9c' },
]

# get all the users from the users table
users = users_table.scan()['Items']

# for each user, add a model share for each model
for user in users:
    for model in models:
        model_id = model['model_id']
        owner_id = model['owner_id']
        user_id = user['user_id']
        model_share_id = str(uuid.uuid4())
        last_edited = datetime.now().isoformat() + "Z"

        model_shares_table.put_item(
            Item={
                'share_id': model_share_id,
                'model_id': model_id,
                'from_id': owner_id,
                'to_id': user_id,
                'last_edited': last_edited
            }
        )

print("Done")
