from .base_agent import Agent
from utils.register import register_class, registry
import json

@register_class(alias="Agent.Evaluator.GPT")
class Evaluator(Agent):
    def __init__(self, args):

        engine = registry.get_class("Engine.GPT")(
            openai_api_key=args.evaluator_openai_api_key,
            openai_api_base=args.evaluator_openai_api_base,
            openai_model_name=args.evaluator_openai_model_name,
            temperature=args.evaluator_temperature,
            max_tokens=args.evaluator_max_tokens,
            top_p=args.evaluator_top_p,
            frequency_penalty=args.evaluator_frequency_penalty,
            presence_penalty=args.evaluator_presence_penalty
        )
        
        self.system_message = (
            "You are a health evaluator specializing in assessing obesity risks. "
            "You will analyze a resident's basic information and provide a score, trend, description, "
            "and whether the resident should consult a doctor."
        )
        super(Evaluator, self).__init__(engine)


    @staticmethod
    def add_parser_args(parser):
        parser.add_argument('--evaluator_openai_api_key', type=str, help='API key for OpenAI')
        parser.add_argument('--evaluator_openai_api_base', type=str, help='API base for OpenAI')
        parser.add_argument('--evaluator_openai_model_name', type=str, help='API model name for OpenAI')
        parser.add_argument('--evaluator_temperature', type=float, default=0.7, help='temperature')
        parser.add_argument('--evaluator_max_tokens', type=int, default=2048, help='max tokens')
        parser.add_argument('--evaluator_top_p', type=float, default=1.0, help='top p')
        parser.add_argument('--evaluator_frequency_penalty', type=float, default=0.0, help='frequency penalty')
        parser.add_argument('--evaluator_presence_penalty', type=float, default=0.0, help='presence penalty')

    def speak(self, basic_info, save_to_memory=True):
        """
        evaluate resident basic information
        """
        if not isinstance(basic_info, str):
            raise ValueError("The 'basic_info' parameter must be a string.")

        prompt = (
            "Given the following resident's basic information, generate an evaluation. "
            "Your response must include the following fields:\n"
            "1. 'score': A numeric obesity risk score between 0 and 100. "
            "The score should represent the overall health status of the resident, "
            "where **0 indicates the worst health status (highest obesity risk)**, "
            "and **100 indicates the best health status (lowest obesity risk)**.\n"
            "2. 'trend': A qualitative description of the resident's health trend (e.g., 'Worsening', 'Improving', 'Stable').\n"
            "3. 'description': A detailed explanation of the resident's obesity risk based on the given data.\n"
            "4. 'consult': A recommendation ('Yes' or 'No') on whether the resident should consult a doctor.\n\n"
            "Resident's Basic Information:\n{basic_info}\n\n"
            "Provide your response in JSON format as shown below:\n"
            "{{\n"
            "  'score': <numeric_value>,\n"
            "  'trend': '<trend_description>',\n"
            "  'description': '<detailed_explanation>',\n"
            "  'consult': '<Yes_or_No>'\n"
            "}}"
        ).format(basic_info=basic_info)

        response = self.engine.get_response([{"role": "system", "content": prompt}])
        
        if save_to_memory:
            self.memorize(("user", f"Basic Info: {basic_info}"))
            self.memorize(("assistant", response))
        
        return response

    def parse_role_content(self, response):
        """
        parse and return
        """
        try:
            response_dict = json.loads(response)
            score = response_dict.get("score")
            trend = response_dict.get("trend")
            description = response_dict.get("description")
            consult = response_dict.get("consult")
            return score, trend, description, consult
        except json.JSONDecodeError:
            print(f"Failed to parse response: {response}")
            return None, None, None, None
