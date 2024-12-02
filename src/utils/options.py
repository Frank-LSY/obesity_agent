# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import argparse
from pathlib import Path
from utils.register import registry
from typing import Callable, List, Optional, Union
import json
import copy


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scenario", default="Scenario.Consultation", 
        choices=["Scenario.Consultation", "Scenario.CollaborativeConsultation"], 
        type=str
    )
    args, _ = parser.parse_known_args()
    
    scenario_group = parser.add_argument_group(
            title="Scenario",
            description="scenario configuration",
        )
    registry.get_class(args.scenario).add_parser_args(scenario_group)
    args, _ = parser.parse_known_args()
    # print(args)
    # Add args of resident to parser.
    if hasattr(args, "resident"):
        resident_group = parser.add_argument_group(
            title="Resident",
            description="Resident configuration",
        )
        if registry.get_class(args.resident) is not None:
            registry.get_class(args.resident).add_parser_args(resident_group)
        else:
            raise RuntimeError()
    
    # Add args of evaluator to parser.
    if hasattr(args, "evaluator"):
        evaluator_group = parser.add_argument_group(
            title="Evaluator",
            description="Evaluator configuration",
        )
        if registry.get_class(args.evaluator) is not None:
            registry.get_class(args.evaluator).add_parser_args(evaluator_group)
        else:
            raise RuntimeError()
        
    # Add args of doctor to parser.
    if hasattr(args, "doctor"):
        doctor_group = parser.add_argument_group(
            title="Doctor",
            description="Doctor configuration",
        )
        if registry.get_class(args.doctor) is not None:
            registry.get_class(args.doctor).add_parser_args(doctor_group)
        else:
            raise RuntimeError()

    args, _ = parser.parse_known_args()

    return args
                