from flask import current_app, Blueprint, request
from app.utils import token_required
import json
import requests
import itertools
import time

from ..utils import floats_to_decimals

experiment = Blueprint('experiment', __name__)

experiment_workflow_string = """
{
  "1": {
    "inputs": {
      "ckpt_name": "realistic_vision_5.0.safetensors",
      "vae_name": "Baked VAE",
      "clip_skip": -1,
      "lora_name": "None",
      "lora_model_strength": 1,
      "lora_clip_strength": 1,
      "positive": "photograph of beautiful interior design living room, orange theme",
      "negative": "ugly, disfigured",
      "empty_latent_width": 512,
      "empty_latent_height": 512,
      "batch_size": 1
    },
    "class_type": "Efficient Loader"
  },
  "2": {
    "inputs": {
      "sampler_state": "Sample",
      "seed": 185001115171524,
      "steps": 20,
      "cfg": 7,
      "sampler_name": "euler",
      "scheduler": "normal",
      "denoise": 1,
      "preview_method": "auto",
      "vae_decode": "true",
      "model": [
        "1",
        0
      ],
      "positive": [
        "1",
        1
      ],
      "negative": [
        "1",
        2
      ],
      "latent_image": [
        "1",
        3
      ],
      "optional_vae": [
        "1",
        4
      ]
    },
    "class_type": "KSampler (Efficient)"
  },
  "9": {
    "inputs": {
      "filename_prefix": "ComfyUI",
      "images": [
        "2",
        5
      ]
    },
    "class_type": "SaveImage"
  }
}
"""

'''
type ExperimentObj = {
    experiment_id: string;
    name: string;
    experiment_parameters: ExperimentParametersObj;
    grid: GridObj;
    runs: number;
    owner_id: string;
    last_edited: string;
}

type ExperimentParametersObj = {
    models: string[];
    prompts: string[];
    seeds: number[];
    steps: number[];
    cfgs: number[];
    denoises: number[];
    widths: number[];
    heights: number[];
    samplers: string[];
    schedulers: string[];
}

type GridObj = {
    x_axis: string;
    y_axis: string;
    z_axis: string;
}
'''

from decimal import Decimal

mapping = {
    'models': ("1", "inputs", "ckpt_name"),
    'prompts': ("1", "inputs", "positive"),
    'seeds': ("2", "inputs", "seed"),
    'steps': ("2", "inputs", "steps"),
    'cfgs': ("2", "inputs", "cfg"),
    'widths': ("1", "inputs", "empty_latent_width"),
    'heights': ("1", "inputs", "empty_latent_height"),
    'samplers': ("2", "inputs", "sampler_name"),
    'schedulers': ("2", "inputs", "scheduler"),
    'denoises': ("2", "inputs", "denoise")
}


@experiment.route('/run/<string:run_id>/start', methods=['POST'])
@token_required
def run(user_id, run_id):
    API_URL = 'https://server1.vango.ai'
    data_manager = current_app.data_manager

    run = data_manager.get_run(run_id)
    models = data_manager.get_models(run["parameters"]["models"])
    models_downloading = []
    for model in models:
        response = requests.post(f'{API_URL}/download/checkpoint', json={"model_id": model["model_id"], "s3_url": model["s3_url"]}, headers={"Content-Type": "application/json"})
        print("status", response.status_code)
        if response.status_code == 202:
            models_downloading.append(model)

    while models_downloading:
        i = 0
        while i < len(models_downloading):
            response = requests.get(f'{API_URL}/download/checkpoint/status/{models_downloading[i]["model_id"]}')
            print(response.status_code, response.json(), response.json()["status"])
            if response.json()["status"] == True:
                models_downloading.pop(i)
            else:
                i += 1
        time.sleep(10)

    sorted_keys = sorted(run["parameters"].keys())
    params_indices = [range(len(run["parameters"][key])) for key in sorted_keys]
    index_combinations = list(itertools.product(*params_indices))
    combinations = [dict(zip(sorted_keys, combination)) for combination in index_combinations]

    for combination in combinations:
        experiment_workflow = json.loads(experiment_workflow_string)
        for key, value in combination.items():
            val = run["parameters"][key][value]
            if isinstance(val, Decimal):
                val = float(val)
            experiment_workflow[mapping[key][0]][mapping[key][1]][mapping[key][2]] = val
        experiment_workflow["9"]["inputs"]["filename_prefix"] = f"run/{run_id}/" + "_".join([str(combination[key]) for key in sorted(combination.keys())]) + ".png"
        experiment_workflow["1"]["inputs"]["ckpt_name"] += ".safetensors"
        response = requests.post(f'{API_URL}/prompt', json={"prompt": experiment_workflow}, headers={"Content-Type": "application/json"})
        print(response.json())

    return "", 200

@experiment.route('/<string:experiment_id>')
@token_required
def get_experiment(user_id, experiment_id):
    data_manager = current_app.data_manager
    try:
        experiment = data_manager.get_experiment(experiment_id)
    except Exception as e:
        return {"error getting experiment": str(e)}, 500

    if not experiment:
        return '', 404
    return experiment, 200

@experiment.route('/list')
@token_required
def list_experiments(user_id):
    data_manager = current_app.data_manager
    try:
        experiments = data_manager.get_experiments(user_id)
    except Exception as e:
        return {"error listing experiments": str(e)}, 500
    return experiments, 200

@experiment.route('/create', methods=['POST'])
@token_required
def create_experiment(user_id):
    data_manager = current_app.data_manager
    try:
        experiment = data_manager.create_experiment(user_id)
    except Exception as e:
        return {"error creating experiment": str(e)}, 500
    return experiment, 200

@experiment.route('/<string:experiment_id>/save', methods=['POST'])
@token_required
def save_experiment(user_id, experiment_id):
    data_manager = current_app.data_manager
    try:
        data_manager.save_experiment(experiment_id, request.json['experiment'])
    except Exception as e:
        return {"error saving experiment": str(e)}, 500
    return '', 204

@experiment.route('/<string:experiment_id>/rename', methods=['POST'])
@token_required
def rename_experiment(user_id, experiment_id):
    data_manager = current_app.data_manager
    try:
        experiment = data_manager.rename_experiment(experiment_id, request.json['name'])
    except Exception as e:
        return {"error renaming experiment": str(e)}, 500
    return experiment, 200

@experiment.route('/<string:experiment_id>/run/create', methods=['POST'])
@token_required
def create_run(user_id, experiment_id):
    data_manager = current_app.data_manager
    try:
        run = data_manager.create_run(experiment_id, request.json['name'], floats_to_decimals(request.json['experiment_parameters']))
    except Exception as e:
        return {"error creating run": str(e)}, 500
    return run, 200

@experiment.route('/run/<string:run_id>')
@token_required
def get_run(user_id, run_id):
    data_manager = current_app.data_manager
    try:
        run = data_manager.get_run(run_id)
    except Exception as e:
        return {"error getting run": str(e)}, 500

    if not run:
        return '', 404
    return run, 200
