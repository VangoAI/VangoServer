from flask import current_app, Blueprint, request
from app.utils import token_required
import json
import requests

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
def find_decimal(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, Decimal):
                print(f"Decimal found: Key = {k}, Value = {v}")
            else:
                find_decimal(v)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, Decimal):
                print(f"Decimal found: Index = {i}, Value = {v}")
            else:
                find_decimal(v)


@experiment.route('/<string:experiment_id>/run', methods=['POST'])
@token_required
def run(user_id, experiment_id):
    data_manager = current_app.data_manager

    experiment = data_manager.get_experiment(experiment_id)

    API_URL = 'https://server1.vango.ai'

    number = 0
    for k in range(len(experiment["experiment_parameters"][experiment["grid"]["z_axis"]])):
        for j in range(len(experiment["experiment_parameters"][experiment["grid"]["y_axis"]])):
            for i in range(len(experiment["experiment_parameters"][experiment["grid"]["x_axis"]])):
                experiment_workflow = json.loads(experiment_workflow_string)
                experiment_workflow["1"]["inputs"]["ckpt_name"] = experiment["experiment_parameters"]["models"][i if experiment["grid"]["x_axis"] == "models" else (j if experiment["grid"]["y_axis"] == "models" else (k if experiment["grid"]["z_axis"] == "models" else 0))]
                experiment_workflow["1"]["inputs"]["positive"] = experiment["experiment_parameters"]["prompts"][i if experiment["grid"]["x_axis"] == "prompts" else (j if experiment["grid"]["y_axis"] == "prompts" else (k if experiment["grid"]["z_axis"] == "prompts" else 0))]
                experiment_workflow["2"]["inputs"]["seed"] = int(experiment["experiment_parameters"]["seeds"][i if experiment["grid"]["x_axis"] == "seeds" else (j if experiment["grid"]["y_axis"] == "seeds" else (k if experiment["grid"]["z_axis"] == "seeds" else 0))])
                experiment_workflow["2"]["inputs"]["steps"] = int(experiment["experiment_parameters"]["steps"][i if experiment["grid"]["x_axis"] == "steps" else (j if experiment["grid"]["y_axis"] == "steps" else (k if experiment["grid"]["z_axis"] == "steps" else 0))])
                experiment_workflow["2"]["inputs"]["cfg"] = float(experiment["experiment_parameters"]["cfgs"][i if experiment["grid"]["x_axis"] == "cfgs" else (j if experiment["grid"]["y_axis"] == "cfgs" else (k if experiment["grid"]["z_axis"] == "cfgs" else 0))])
                experiment_workflow["1"]["inputs"]["empty_latent_width"] = int(experiment["experiment_parameters"]["widths"][i if experiment["grid"]["x_axis"] == "widths" else (j if experiment["grid"]["y_axis"] == "widths" else (k if experiment["grid"]["z_axis"] == "widths" else 0))])
                experiment_workflow["1"]["inputs"]["empty_latent_height"] = int(experiment["experiment_parameters"]["heights"][i if experiment["grid"]["x_axis"] == "heights" else (j if experiment["grid"]["y_axis"] == "heights" else (k if experiment["grid"]["z_axis"] == "heights" else 0))])
                experiment_workflow["2"]["inputs"]["sampler_name"] = experiment["experiment_parameters"]["samplers"][i if experiment["grid"]["x_axis"] == "samplers" else (j if experiment["grid"]["y_axis"] == "samplers" else (k if experiment["grid"]["z_axis"] == "samplers" else 0))]
                experiment_workflow["2"]["inputs"]["scheduler"] = experiment["experiment_parameters"]["schedulers"][i if experiment["grid"]["x_axis"] == "schedulers" else (j if experiment["grid"]["y_axis"] == "schedulers" else (k if experiment["grid"]["z_axis"] == "schedulers" else 0))]
                experiment_workflow["2"]["inputs"]["denoise"] = float(experiment["experiment_parameters"]["denoises"][i if experiment["grid"]["x_axis"] == "denoises" else (j if experiment["grid"]["y_axis"] == "denoises" else (k if experiment["grid"]["z_axis"] == "denoises" else 0))])
                experiment_workflow["9"]["inputs"]["filename_prefix"] = f"experiment/{experiment['experiment_id']}/{experiment['runs']}/{i}_{j}_{k}.png"

                response = requests.post(f'{API_URL}/prompt', json={"prompt": experiment_workflow, "number": number }, headers={"Content-Type": "application/json"})
                print(response.json())
                number += 1
    return "", 200


@experiment.route('/<string:experiment_id>/results', methods=['GET'])
@token_required
def get_results(user_id, experiment_id):
    data_manager = current_app.data_manager
    return data_manager.get_images(), 200

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
