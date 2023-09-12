import os
import datetime
import uuid
import boto3
from boto3.dynamodb.conditions import Key
import json
from ..models.experiment import Experiment
from werkzeug.datastructures import FileStorage

class DataManager:
    def __init__(self):
        session = boto3.Session(aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), region_name="us-west-2")
        s3 = session.resource('s3')
        self.s3_client = session.client('s3')
        dynamodb = session.resource('dynamodb')

        self.files_bucket = s3.Bucket("vangoui-files")
        self.images_bucket = s3.Bucket("vango-logos")
        self.models_bucket = s3.Bucket("vango-models")
        self.users_table = dynamodb.Table("Users")
        self.files_table = dynamodb.Table("Files")
        self.experiments_table = dynamodb.Table("Experiments")
        self.experiment_runs_table = dynamodb.Table("ExperimentRuns")
        self.models_table = dynamodb.Table("Models")
        self.model_shares_table = dynamodb.Table("ModelShares")
    
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
        self.share_model("b6df4801-e932-4e28-b03a-fbb809637bd3", "0dea49ef-abf9-4e73-8e2c-34fc529e2c9c", user_id) # share sdxl
        return self.get_user(user_id)
    
    def user_id_exists(self, user_id: str) -> bool:
        """
        Check if a user with the given ID exists.

        Args:
            user_id (str): The ID of the user to check.
            
        Returns:
            bool: True if the user exists, False otherwise.
        """
        return self.get_user(user_id) is not None

    def google_id_exists(self, google_id: str) -> bool:
        """
        Check if a user with the given Google ID exists.

        Args:
            google_id (str): The Google ID of the user to check.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        return self.get_user_from_google_id(google_id) is not None

    def get_user(self, user_id: str) -> dict | None:
        """
        Retrieves a user from the users table based on the provided user ID.

        Args:
            user_id (str): The ID of the user to retrieve.

        Returns:
            dict | None: The user item from the users table, None if the user does not exist.
        """
        response = self.users_table.get_item(Key={"user_id": user_id})
        return response["Item"] if "Item" in response else None
    
    def get_users(self, user_ids: list[str]) -> list[dict]:
        """
        Retrieves multiple users from the users table based on the provided user IDs.

        Args:
            user_ids (list[str]): The IDs of the users to retrieve.

        Returns:
            list[dict]: List of user items from the users table.
        """
        unique_user_ids = list(set(user_ids))
        keys = [{"user_id": user_id} for user_id in unique_user_ids]
        response = self.users_table.meta.client.batch_get_item(
            RequestItems={
                'Users': {
                    'Keys': keys
                }
            }
        )
        
        retrieved_users = response['Responses']['Users']
        retrieved_users_dict = {user['user_id']: user for user in retrieved_users}
        final_result = [retrieved_users_dict.get(user_id, "") for user_id in user_ids]
        return final_result
    
    def get_usernames(self, user_ids: list[str]) -> list[str]:
        """
        Retrieves the usernames of the users with the given user IDs.

        Args:
            user_ids (list[str]): The IDs of the users to retrieve usernames for.

        Returns:
            list[str]: A list of usernames.
        """
        users = self.get_users(user_ids)
        return [user["username"] for user in users]
    
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

        empty_workflow = {
            "last_node_id": 0,
            "last_link_id": 0,
            "nodes": [],
            "links": [],
            "groups": [],
            "config": {},
            "extra": {},
            "version": 0.4
        }
        
        self.files_bucket.put_object(Key=file_id, Body=json.dumps(empty_workflow, indent=4))
        self.files_table.put_item(Item={
            "file_id": file_id,
            "owner_id": user_id,
            "file_name": "Untitled",
            "last_edited": datetime.datetime.utcnow().isoformat() + "Z",
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

    def get_file_content(self, file_id: str) -> str:
        """
        Retrieves the contents of a file from the files bucket based on the provided file ID.

        Args:
            file_id (str): The ID of the file to retrieve.

        Returns:
            str: The contents of the file.
        """
        file_object = self.files_bucket.Object(file_id)
        return file_object.get()["Body"].read().decode("utf-8")

    def rename_file(self, file_id: str, file_name: str) -> dict:
        """
        Renames a file in the files table based on the provided file ID.

        Args:
            file_id (str): The ID of the file to rename.

        Returns:
            dict: The file item from the files table.
        """
        self.files_table.update_item(
            Key={"file_id": file_id},
            UpdateExpression="SET file_name = :file_name",
            ExpressionAttributeValues={":file_name": file_name}
        )
        return self.get_file(file_id)
    
    def save_file(self, file_id: str, content: str) -> None:
        """
        Saves the contents of a file to the files bucket based on the provided file ID.

        Args:
            file_id (str): The ID of the file to save.
            content (str): The contents of the file.
        """
        file_object = self.files_bucket.Object(file_id)
        file_object.put(Body=content)
        self.files_table.update_item(
            Key={"file_id": file_id},
            UpdateExpression="SET last_edited = :last_edited",
            ExpressionAttributeValues={":last_edited": datetime.datetime.now().isoformat()}
        )

    def copy_file(self, user_id: str, file_id: str) -> dict:
        """
        Copies a file in the files table based on the provided file ID.

        Args:
            file_id (str): The ID of the file to copy.
            user_id (str): The ID of the user to copy the file for.

        Returns:
            dict: The file item from the files table.
        """
        file = self.get_file(file_id)
        file_content = self.get_file_content(file_id)
        
        new_file = self.create_file(user_id)
        self.save_file(new_file["file_id"], file_content)
        self.rename_file(new_file["file_id"], file["file_name"] + " (Copy)")
        return new_file
    
    def get_experiment(self, experiment_id: str) -> dict:
        """
        Retrieves an experiment from the experiments table based on the provided experiment ID.

        Args:
            experiment_id (str): The ID of the experiment to retrieve.

        Returns:
            dict: The experiment item from the experiments table.
        """
        response = self.experiments_table.get_item(Key={"experiment_id": experiment_id})
        return response["Item"] if "Item" in response else None
    
    def get_experiments(self, user_id: str) -> list[dict]:
        """
        Retrieves all experiments from the experiments table for the given user ID.

        Args:
            user_id (str): The ID of the user to retrieve experiments for.

        Returns:
            list[dict]: A list of experiment items from the experiments table.
        """
        response = self.experiments_table.query(
            IndexName="owner_id_index",
            KeyConditionExpression=Key('owner_id').eq(user_id)
        )
        return response["Items"]
    
    def create_experiment(self, user_id: str) -> dict:
        """
        Creates a new experiment in the experiments table with the given user ID.

        Args:
            user_id (str): The ID of the user to create the experiment for.
        Returns:
            dict: The experiment item from the experiments table.
        """
        experiment = Experiment.default(user_id)
        experiment_dict = experiment.to_dict()
        self.experiments_table.put_item(Item=experiment_dict)
        return experiment_dict
    
    def save_experiment(self, experiment_id: str, experiment: dict) -> None:
        """
        Saves the experiment to the experiments table based on the provided experiment ID.

        Args:
            experiment_id (str): The ID of the experiment to save.
            experiment (dict): The experiment.
        """
        self.experiments_table.update_item(
            Key={"experiment_id": experiment_id},
            UpdateExpression="SET cells = :cells, run_ids = :run_ids, last_edited = :last_edited",
            ExpressionAttributeValues={":cells": experiment["cells"], ":run_ids": experiment["run_ids"], ":last_edited": datetime.datetime.utcnow().isoformat() + "Z"}
        )

    def rename_experiment(self, experiment_id: str, name: str) -> dict:
        """
        Renames an experiment in the experiments table based on the provided experiment ID.

        Args:
            experiment_id (str): The ID of the experiment to rename.

        Returns:
            dict: The experiment item from the experiments table.
        """
        self.experiments_table.update_item(
            Key={"experiment_id": experiment_id},
            UpdateExpression="SET #n = :name, last_edited = :last_edited",
            ExpressionAttributeNames={"#n": "name"},
            ExpressionAttributeValues={":name": name, ":last_edited": datetime.datetime.utcnow().isoformat() + "Z"}
        )
        return self.get_experiment(experiment_id)
    
    def create_run(self, experiment_id: str, name: str, experiment_parameters: dict) -> dict:
        """
        Creates a new run in the experiment runs table with the given experiment ID, name, and parameters.

        Args:
            experiment_id (str): The ID of the experiment to create the run for.
            name (str): The name of the run.
            experiment_parameters (dict): The parameters of the run.
        Returns:
            dict: The run item from the experiment runs table.
        """
        run_id = str(uuid.uuid4())
        self.experiment_runs_table.put_item(Item={
            "run_id": run_id,
            "experiment_id": experiment_id,
            "name": name,
            "parameters": experiment_parameters,
            "date": datetime.datetime.utcnow().isoformat() + "Z",
        })
        experiment = self.get_experiment(experiment_id)
        experiment["run_ids"].append(run_id)
        self.save_experiment(experiment_id, experiment)
        return self.get_run(run_id)
    
    def get_run(self, run_id: str) -> dict:
        """
        Retrieves a run from the experiment runs table based on the provided run ID.

        Args:
            run_id (str): The ID of the run to retrieve.

        Returns:
            dict: The run item from the experiment runs table.
        """
        response = self.experiment_runs_table.get_item(Key={"run_id": run_id})
        return response["Item"] if "Item" in response else None
    
    def create_model(self, user_id: str, name: str, type: str, s3_url: str, model_id: str = None) -> dict:
        """
        Creates a new model in the models table with the given user ID, name, type, and S3 URL.

        Args:
            user_id (str): The ID of the user to create the model for.
            name (str): The name of the model.
            type (str): The type of the model.
            s3_url (str): The S3 URL of the model.
            model_id (str): The ID of the model, if None a new ID will be generated.

        Returns:
            dict: The model item from the models table.
        """
        if model_id is None:
            model_id = str(uuid.uuid4())

        self.models_table.put_item(Item={
            "model_id": model_id,
            "name": name,
            "type": type,
            "owner_id": user_id,
            "s3_url": s3_url,
            "last_edited": datetime.datetime.utcnow().isoformat() + "Z",
        })
        return self.get_model(model_id)
    
    def get_model(self, model_id: str) -> dict:
        """
        Retrieves a model from the models table based on the provided model ID.

        Args:
            model_id (str): The ID of the model to retrieve.

        Returns:
            dict: The model item from the models table.
        """
        response = self.models_table.get_item(Key={"model_id": model_id})
        return response["Item"] if "Item" in response else None
    
    def get_models(self, model_ids: [str]) -> list[dict]:
        """
        Retrieves multiple models from the models table based on the provided model IDs.

        Args:
            model_ids (list[str]): The IDs of the models to retrieve.

        Returns:
            list[dict]: List of model items from the models table.
        """
        keys = [{"model_id": model_id} for model_id in model_ids]
        response = self.models_table.meta.client.batch_get_item(
            RequestItems={
                'Models': {
                    'Keys': keys
                }
            }
        )
        return response['Responses']['Models']

    def list_models(self, user_id: str) -> dict:
        """
        Retrieves all models for the given user ID.

        Args:
            user_id (str): The ID of the user to retrieve models for.

        Returns:
            dict: A dictionary of model items from the models table.
        """
        # get all models owned by the user and all models shared with the user
        owned_models = self.models_table.query(
            IndexName="owner_id_index",
            KeyConditionExpression=Key('owner_id').eq(user_id)
        )["Items"]

        shares = self.model_shares_table.query(
            IndexName="to_id_index",
            KeyConditionExpression=Key('to_id').eq(user_id)
        )["Items"]
        shared_models = self.get_models([share["model_id"] for share in shares]) if shares else []

        return owned_models + shared_models
    
    def share_model(self, model_id: str, from_id: str, to_id: str) -> None:
        """
        Shares a model with another user.

        Args:
            model_id (str): The ID of the model to share.
            from_id (str): The ID of the user sharing the model.
            to_id (str): The ID of the user to share the model with.
        """
        self.model_shares_table.put_item(Item={
            "share_id": str(uuid.uuid4()),
            "model_id": model_id,
            "from_id": from_id,
            "to_id": to_id,
            "last_edited": datetime.datetime.utcnow().isoformat() + "Z",
        })
    
    def start_upload(self, num_parts: int) -> dict:
        """
        Starts an upload to the models bucket with the given number of parts.

        Args:
            num_parts (int): The number of parts to upload.

        Returns:
            tuple: The model ID, upload ID, and presigned URLs.
        """
        model_id = str(uuid.uuid4())
        upload_id = self.s3_client.create_multipart_upload(Bucket='vango-models', Key=model_id)["UploadId"]

        presigned_urls = []
        for i in range(num_parts):
            presigned_url = self.models_bucket.meta.client.generate_presigned_url(
                ClientMethod='upload_part',
                Params={
                    'Bucket': 'vango-models',
                    'Key': model_id,
                    'UploadId': upload_id,
                    'PartNumber': i + 1
                }
            )
            presigned_urls.append(presigned_url)
        
        return model_id, upload_id, presigned_urls
    
    def complete_upload(self, user_id: str, model_id: str, name: str, type: str, upload_id: str, parts: list[dict]) -> None:
        """
        Completes an upload to the models bucket with the given model ID, upload ID, and parts.

        Args:
            model_id (str): The ID of the model to complete the upload for.
            upload_id (str): The ID of the upload to complete.
            parts (list[dict]): The parts of the upload.
        """
        self.models_bucket.meta.client.complete_multipart_upload(
            Bucket="vango-models",
            Key=model_id,
            UploadId=upload_id,
            MultipartUpload={"Parts": parts}
        )
        return self.create_model(user_id, name, type, f"https://vango-models.s3-us-west-2.amazonaws.com/{model_id}", model_id)

    def get_images(self):
        objects = self.images_bucket.objects.filter(Prefix="images/sdxl_eval_1/")
        object_keys = [obj.key for obj in objects]
        object_keys.sort(key=lambda key: (int(key.split('_')[3]), int(key.split('_')[4])))

        s3_base_url = "https://{}.s3.us-west-2.amazonaws.com/".format(self.images_bucket.name)
        s3_urls = []
        for object_key in object_keys:
            s3_url = s3_base_url + object_key
            s3_urls.append(s3_url)
        return s3_urls
    