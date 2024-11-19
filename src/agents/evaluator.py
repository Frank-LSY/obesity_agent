# health evaluator of the system
from .base_agent import Agent
from utils.register import register_class, registry
@register_class(alias="Agent.Evaluator.GPT")
class Evaluator(Agent):
    def __init__(self, args, evaluator_info=None):
        engine = registry.get_class("Engine.GPT")(
            openai_api_key=args.patient_openai_api_key, 
            openai_api_base=args.patient_openai_api_base,
            openai_model_name=args.patient_openai_model_name, 
            temperature=args.patient_temperature, 
            max_tokens=args.patient_max_tokens,
            top_p=args.patient_top_p,
            frequency_penalty=args.patient_frequency_penalty,
            presence_penalty=args.patient_presence_penalty
        )
        if evaluator_info is None:
            self.system_message = \
                "You are an evaluator. You are responsible for evaluate health conditions of any residents.\n"
        else: self.system_message = evaluator_info

        super(Evaluator, self).__init__(engine)

    @staticmethod
    def add_parser_args(parser):
        parser.add_argument('--evaluator_openai_api_key', type=str, help='API key for OpenAI')
        parser.add_argument('--evaluator_openai_api_base', type=str, help='API base for OpenAI')
        parser.add_argument('--evaluator_openai_model_name', type=str, help='API model name for OpenAI')
        parser.add_argument('--evaluator_temperature', type=float, default=0.0, help='temperature')
        parser.add_argument('--evaluator_max_tokens', type=int, default=2048, help='max tokens')
        parser.add_argument('--evaluator_top_p', type=float, default=1, help='top p')
        parser.add_argument('--evaluator_frequency_penalty', type=float, default=0, help='frequency penalty')
        parser.add_argument('--evaluator_presence_penalty', type=float, default=0, help='presence penalty')

    def speak(self,):
        pass
    
    @staticmethod
    def parse_role_content(responese):
        pass
