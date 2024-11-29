from .base_agent import Agent
# from .doctor import (
#     Doctor, 
#     GPTDoctor, 
#     ChatGLMDoctor, 
#     MinimaxDoctor, 
#     WenXinDoctor, 
#     QwenDoctor, 
#     HuatuoGPTDoctor,
#     HFDoctor
# )
from .doctor_gary import Doctor
from .resident import Resident
from .patient import Patient
from .evaluator import Evaluator
from .reporter import Reporter, ReporterV2
from .host import Host


__all__ = [
    "Agent",
    "Doctor",
    # "GPTDoctor",
    # "HFDoctor",
    "Resident",
    "Evaluator",
    "Patient",
]   
