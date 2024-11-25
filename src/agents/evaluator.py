# health evaluator of the system
from .base_agent import Agent
from utils.register import register_class, registry

@register_class(alias="Agent.Evaluator.GPT")
class Evaluator(Agent):
    def __init__(self, args, evaluator_info=None):
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
        if evaluator_info is None:
            self.system_message = \
                "You are an evaluator. You are responsible for evaluating the health conditions of any residents.\n" + \
                "Your primary focus is to assess the obesity status of the residents based on their medical records.\n" + \
                "Consider the following criteria for obesity assessment:\n" + \
                "1. Body Mass Index (BMI): A BMI of 30 or higher indicates obesity.\n" + \
                "2. Waist Circumference: A waist circumference of more than 40 inches for men and 35 inches for women indicates a higher risk of obesity-related conditions.\n" + \
                "3. Medical History: Look for any history of obesity-related conditions such as type 2 diabetes, hypertension, and cardiovascular diseases.\n" + \
                "4. Physical Activity: Assess the level of physical activity and sedentary behavior.\n" + \
                "5. Dietary Habits: Evaluate the dietary habits and nutritional intake.\n"
        else:
            self.system_message = evaluator_info

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

    def evaluate_health_condition(self, resident_profile, medical_records):
        system_message = self.system_message + "\n" + \
            "Resident Profile:\n" + resident_profile + "\n" + \
            "Medical Records:\n" + medical_records + "\n"

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": "Please evaluate the health condition of the resident based on the provided information."}
        ]

        response = self.engine.get_response(messages)
        return response

    def speak(self, resident_profile, medical_records):
        evaluation = self.evaluate_health_condition(resident_profile, medical_records)
        return evaluation
