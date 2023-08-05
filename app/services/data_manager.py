import os
import datetime
import uuid
import boto3
from boto3.dynamodb.conditions import Key

class DataManager:
    def __init__(self):
        session = boto3.Session(aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), region_name="us-west-2")
        s3 = session.resource('s3')
        dynamodb = session.resource('dynamodb')

        self.files_bucket = s3.Bucket("vangoui-files")
        self.users_table = dynamodb.Table("Users")
        self.files_table = dynamodb.Table("Files")
    
    def create_user(self, google_id: str, email: str, name: str) -> dict:
        """
        Creates a new user in the users table with the given Google ID, email, and name.

        Args:
            google_id (str): The Google ID of the user.
            email (str): The email address of the user.
            name (str): The name of the user.
        Returns:
            dict: The user item from the users table.
        """
        user_id = str(uuid.uuid4())
        self.users_table.put_item(Item={
            "user_id": user_id,
            "google_id": google_id,
            "email": email,
            "username": name,
            "subscription_plan": "Free",
            "credits": 1,
        })
        return self.get_user_from_user_id(user_id)
    
    def user_id_exists(self, user_id: str) -> bool:
        """
        Check if a user with the given ID exists.

        Args:
            user_id (str): The ID of the user to check.
            
        Returns:
            bool: True if the user exists, False otherwise.
        """
        return self.get_user_from_user_id(user_id) is not None

    def google_id_exists(self, google_id: str) -> bool:
        """
        Check if a user with the given Google ID exists.

        Args:
            google_id (str): The Google ID of the user to check.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        return self.get_user_from_google_id(google_id) is not None

    def get_user_from_user_id(self, user_id: str) -> dict | None:
        """
        Retrieves a user from the users table based on the provided user ID.

        Args:
            user_id (str): The ID of the user to retrieve.

        Returns:
            dict | None: The user item from the users table, None if the user does not exist.
        """
        response = self.users_table.get_item(Key={"user_id": user_id})
        return response["Item"] if "Item" in response else None
    
    def get_user_from_google_id(self, google_id: str) -> dict | None:
        """
        Retrieves a user from the users table based on the provided Google ID.

        Args:
            google_id (str): The ID of the user to retrieve.

        Returns:
            dict | None: The user item from the users table, None if the user does not exist.
        """
        response = self.users_table.query(
            IndexName="google_id_index",
            KeyConditionExpression=Key('google_id').eq(google_id)
        )
        return response["Items"][0] if response["Items"] else None
    
    def create_file(self, user_id: str) -> dict:
        """
        Creates a new file in the files table with the given user ID.

        Args:
            user_id (str): The ID of the user to create the file for.
        Returns:
            dict: The file item from the files table.
        """
        file_id = str(uuid.uuid4())
        self.files_table.put_item(Item={
            "file_id": file_id,
            "owner_id": user_id,
            "file_name": "Untitled",
            "last_edited": datetime.datetime.now().isoformat(),
        })
        return self.get_file(file_id)
    
    def file_exists(self, file_id: str) -> bool:
        """
        Check if a file with the given ID exists.

        Args:
            file_id (str): The ID of the file to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        return self.get_file(file_id) is not None
    
    def get_file(self, file_id: str) -> dict:
        """
        Retrieves a file from the files table based on the provided file ID.

        Args:
            file_id (str): The ID of the file to retrieve.

        Returns:
            dict: The file item from the files table.
        """
        response = self.files_table.get_item(Key={"file_id": file_id})
        return response["Item"] if "Item" in response else None

    def get_files(self, user_id: str) -> list[dict]:
        """
        Retrieves all files from the files table for the given user ID.

        Args:
            user_id (str): The ID of the user to retrieve files for.

        Returns:
            list[dict]: A list of file items from the files table.
        """
        response = self.files_table.query(
            IndexName="owner_id_index",
            KeyConditionExpression=Key('owner_id').eq(user_id)
        )
        return response["Items"]
