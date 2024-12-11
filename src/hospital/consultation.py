import argparse
import os
import json
from typing import List
import jsonlines
from tqdm import tqdm
import time
import concurrent
import random
from utils.register import register_class, registry


@register_class(alias="Scenario.Consultation")
class Consultation:
    @staticmethod
    def add_parser_args(parser: argparse.ArgumentParser):
        parser.add_argument("--resident_obesity_goal", default="Maintain", help="resident Obesity Goal")
        parser.add_argument("--resident_profile_path", default="obesity.json", type=str)
        parser.add_argument("--patient_database", default="patients.json", type=str)
        parser.add_argument("--patient", default="Agent.Patient.GPT", help="registry name of patient agent")
        parser.add_argument("--doctor", default="Agent.Doctor.GPT", help="registry name of doctor agent")
        parser.add_argument("--reporter", default="Agent.Reporter.GPT", help="registry name of reporter agent")
        parser.add_argument("--resident", default="Agent.Resident.GPT", help="registry name of resident agent")
        parser.add_argument("--evaluator", default="Agent.Evaluator.GPT", help="registry name of evaluator agent")
        parser.add_argument("--max_conversation_turn", default=10, type=int, help="max conversation turn between doctor and patient")
        parser.add_argument("--max_workers", default=4, type=int, help="max workers for parallel diagnosis")
        parser.add_argument("--delay_between_tasks", default=10, type=int, help="delay between tasks")
        parser.add_argument("--save_path", default="dialog_history.jsonl", help="save path for dialog history")
        parser.add_argument("--ff_print", default=False, action="store_true", help="print dialog history")
        parser.add_argument("--parallel", default=False, action="store_true", help="parallel diagnosis")

