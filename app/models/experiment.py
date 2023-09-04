import uuid
from datetime import datetime

class Experiment:
    def __init__(self, experiment_id: str, name: str, owner_id: str, cells: ['ExperimentCell'], run_ids: [str], last_edited: datetime):
        self.experiment_id = experiment_id
        self.name = name
        self.owner_id = owner_id
        self.cells = cells
        self.run_ids = run_ids
        self.last_edited = last_edited

    def default(owner_id: str) -> 'Experiment':
        return Experiment(
            experiment_id=str(uuid.uuid4()),
            name="Untitled Experiment",
            owner_id=owner_id,
            cells=[GridSliceCell.default()],
            run_ids=[],
            last_edited=datetime.now()
        )
    
    def to_dict(self):
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "owner_id": self.owner_id,
            "cells": [cell.to_dict() for cell in self.cells],
            "run_ids": self.run_ids,
            "last_edited": self.last_edited.isoformat() + "Z",
        }
    
class ExperimentRun:
    def __init__(self, run_id: str, name: str, parameters: 'ExperimentParameters', date: datetime):
        self.run_id = run_id
        self.name = name
        self.parameters = parameters
        self.date = date

    def default(name: str, parameters: 'ExperimentParameters') -> 'ExperimentRun':
        return ExperimentRun(
            run_id=str(uuid.uuid4()),
            name=name,
            parameters=parameters,
            date=datetime.now()
        )
    
    def to_dict(self):
        return {
            "run_id": self.run_id,
            "name": self.name,
            "parameters": self.parameters.to_dict(),
            "date": self.date.isoformat() + "Z",
        }

class ExperimentParameters:
    def __init__(self, models: [str], prompts: [str], seeds: [int], steps: [int], cfgs: [float], denoises: [float], widths: [int], heights: [int], samplers: [str], schedulers: [str]):
        self.models = models
        self.prompts = prompts
        self.seeds = seeds
        self.steps = steps
        self.cfgs = cfgs
        self.denoises = denoises
        self.widths = widths
        self.heights = heights
        self.samplers = samplers
        self.schedulers = schedulers

    def default() -> 'ExperimentParameters':
        return ExperimentParameters(
            models=["sd_xl_base_1.0.safetensors"],
            prompts=["A photo of a cat"],
            seeds=[1],
            steps=[30],
            cfgs=[8],
            denoises=[1],
            widths=[1024],
            heights=[1024],
            samplers=["euler"],
            schedulers=["normal"]
        )
    
    def to_dict(self):
        return self.__dict__
    
class ExperimentCell:
    pass
    
class GridSliceCell:
    type = "GridSlice"

    def __init__(self, fixed_parameters: 'ExperimentParametersFixed', x_axis: str, y_axis: str):
        self.fixed_parameters = fixed_parameters
        self.x_axis = x_axis
        self.y_axis = y_axis

    def default() -> 'GridSliceCell':
        return GridSliceCell(
            fixed_parameters=ExperimentParametersFixed.default(),
            x_axis="models",
            y_axis="prompts"
        )
    
    def to_dict(self):
        return {
            "type": self.type,
            "fixed_parameters": self.fixed_parameters.to_dict(),
            "x_axis": self.x_axis,
            "y_axis": self.y_axis
        }
    
class MarkdownCell:
    type = "Markdown"

    def __init__(self, content: str):
        self.content = content

    def default() -> 'MarkdownCell':
        return MarkdownCell(
            content="## Markdown"
        )
    
    def to_dict(self):
        return self.__dict__
    
class ExperimentParametersFixed:
    def __init__(self, models_index: int, prompts_index: int, seed_index: int, step_index: int, cfg_index: int, denoise_index: int, width_index: int, height_index: int, sampler_index: int, scheduler_index: int):
        self.models = models_index
        self.prompts = prompts_index
        self.seeds = seed_index
        self.steps = step_index
        self.cfgs = cfg_index
        self.denoises = denoise_index
        self.widths = width_index
        self.heights = height_index
        self.samplers = sampler_index
        self.schedulers = scheduler_index

    def default() -> 'ExperimentParametersFixed':
        return ExperimentParametersFixed(
            models_index=0,
            prompts_index=0,
            seed_index=0,
            step_index=0,
            cfg_index=0,
            denoise_index=0,
            width_index=0,
            height_index=0,
            sampler_index=0,
            scheduler_index=0
        )

    def to_dict(self):
        return self.__dict__
