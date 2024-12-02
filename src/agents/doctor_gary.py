from .base_agent import Agent
from utils.register import register_class, registry
import json
import random

@register_class(alias="Agent.Doctor.GPT")
class Doctor(Agent):
    def __init__(self, args):
        """
        Doctor Agent Initialization
        """
        self.system_message = (
            "You are a doctor specializing in obesity management. Your task is to evaluate the resident's obesity risk based on their provided basic information (as a string) "
            "and suggest interventions. The interventions should be directly actionable and specify changes to the resident's behavior, diet, or lifestyle. "
            "In addition, you will provide rationale for each intervention to ensure the resident understands the reasoning behind the recommendations. "
            "When giving interventions, use clear and simple language suitable for a general audience.\n"
        )

        # model_dict reflection
        self.model_dict = {
            'FAVC': ['yes', 'no'],
            'FCVC': [1, 2, 3],
            'NCP': [1, 2, 3, 4, 5],
            'CAEC': ['Never', 'Sometimes', 'Frequently', 'Always'],
            'CH2O': [1, 2, 3],
            'SCC': ['yes', 'no'],
            'FAF': [0, 1, 2, 3],
            'TUE': [0, 1, 2],
            'CALC': ['no', 'Sometimes', 'Frequently', 'Always'],
            'MTRANS': ['Public_Transportation', 'Walking', 'Automobile', 'Motorbike', 'Bike']
        }

        # engine init
        engine = registry.get_class("Engine.GPT")(
            openai_api_key=args.doctor_openai_api_key,
            openai_api_base=args.doctor_openai_api_base,
            openai_model_name=args.doctor_openai_model_name,
            temperature=args.doctor_temperature,
            max_tokens=args.doctor_max_tokens,
            top_p=args.doctor_top_p,
            frequency_penalty=args.doctor_frequency_penalty,
            presence_penalty=args.doctor_presence_penalty,
        )
        super(Doctor, self).__init__(engine)

    @staticmethod
    def add_parser_args(parser):
        parser.add_argument('--doctor_openai_api_key', type=str, help='API key for OpenAI')
        parser.add_argument('--doctor_openai_api_base', type=str, help='API base for OpenAI')
        parser.add_argument('--doctor_openai_model_name', type=str, help='API model name for OpenAI')
        parser.add_argument('--doctor_temperature', type=float, default=0.7, help='temperature')
        parser.add_argument('--doctor_max_tokens', type=int, default=1024, help='max tokens')
        parser.add_argument('--doctor_top_p', type=float, default=1, help='top p')
        parser.add_argument('--doctor_frequency_penalty', type=float, default=0, help='frequency penalty')
        parser.add_argument('--doctor_presence_penalty', type=float, default=0, help='presence penalty')

    def speak(self, basic_info, score, feeling, obesity_goal, save_to_memory=True):
        """
        give out intervention and reasons based on basic information and score.
        """
        if not isinstance(basic_info, str):
            raise ValueError("The 'basic_info' parameter must be a string.")
        if not isinstance(score, (int, float)):
            raise ValueError("The 'score' parameter must be a numeric value.")


        prompt = (
            "You are a doctor specializing in obesity management. Your role is to provide **personalized** intervention measures "
            "based on the resident's basic information, obesity risk score, current feelings, and obesity goal. "
            "Your suggestions should focus on **realistic, actionable changes** to a maximum of three attributes, prioritizing those "
            "that have the greatest impact on the resident's health goal (e.g., weight reduction, weight maintenance, or weight gain).\n\n"
            
            "Resident's Basic Information:\n{basic_info}\n\n"
            "Resident's Current Feeling:\n{feeling}\n\n"
            "Resident's Obesity Goal:\n{obesity_goal}\n\n"
            "Obesity Risk Score: {score}\n\n"
            
            "The following are the possible values for each intervention field:\n"
            "{{\n"
            "  'FAVC': ['yes', 'no'],\n"
            "  'FCVC': [1, 2, 3],\n"
            "  'NCP': [1, 2, 3, 4, 5],\n"
            "  'CAEC': ['Never', 'Sometimes', 'Frequently', 'Always'],\n"
            "  'CH2O': [1, 2, 3],\n"
            "  'SCC': ['yes', 'no'],\n"
            "  'FAF': [0, 1, 2, 3],\n"
            "  'TUE': [0, 1, 2],\n"
            "  'CALC': ['no', 'Sometimes', 'Frequently', 'Always'],\n"
            "  'MTRANS': ['Public_Transportation', 'Walking', 'Automobile', 'Motorbike', 'Bike']\n"
            "}}\n\n"
            
            "When generating your response, please ensure:\n"
            "1. Focus on no more than three key attributes for changes in each round.\n"
            "2. Provide a rationale for each change, explaining how it aligns with the resident's obesity goal, current feelings, "
            "and overall health improvement.\n"
            "3. Include a 'freeze_rounds' field to indicate the number of rounds the resident should maintain the suggested changes before re-evaluation. "
            "This field should be dynamically determined based on the difficulty and impact of the suggested changes, ranging from 1 to 5 rounds.\n\n"
            
            "Your response must include the following fields in JSON format:\n"
            "{{\n"
            "  'intervention': {{'attribute_to_change': 'new_value', ...}},\n"
            "  'freeze_rounds': <number_of_rounds>,\n"
            "  'rationale': '<explanation_for_the_interventions>'\n"
            "}}\n\n"
            
            "Example response:\n"
            "{{\n"
            "  'intervention': {{'FAVC': 'no', 'NCP': 3}},\n"
            "  'freeze_rounds': 3,\n"
            "  'rationale': 'Reducing the frequency of high-caloric food consumption and standardizing meal counts to 3 per day will help decrease overall calorie intake, supporting weight reduction. "
            "This aligns with the resident's goal to lose weight and addresses their feeling of eating too many snacks.'\n"
            "}}\n\n"
            
            "Be sure to propose realistic and personalized changes that reflect the resident's unique circumstances, feelings, and obesity goal."
        ).format(basic_info=basic_info, feeling=feeling, obesity_goal=obesity_goal, score=score)



        response = self.engine.get_response([
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": prompt}
        ])

        if save_to_memory:
            self.memorize(("user", f"Basic Info: {basic_info}, Score: {score}"))
            self.memorize(("assistant", response))

        return response


    def parse_role_content(self, response):
        """
        parse the GPT response and return
        """
        try:
            response_dict = json.loads(response)
            intervention = response_dict.get("intervention", {})
            rationale = response_dict.get("rationale", "")
            freeze_rounds = response_dict.get("freeze_rounds", 0)
        except json.JSONDecodeError:
            raise ValueError("The GPT response is not in the expected JSON format.")

        return intervention, rationale, freeze_rounds

