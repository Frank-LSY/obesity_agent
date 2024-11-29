from .base_agent import Agent
from utils.register import register_class, registry
import random
import re
import json

@register_class(alias="Agent.Resident.GPT")
class Resident(Agent):
    def __init__(self, args, resident_profile, resident_id=0):
        engine = registry.get_class("Engine.GPT")(
            openai_api_key=args.resident_openai_api_key,
            openai_api_base=args.resident_openai_api_base,
            openai_model_name=args.resident_openai_model_name,
            temperature=args.resident_temperature,
            max_tokens=args.resident_max_tokens,
            top_p=args.resident_top_p,
            frequency_penalty=args.resident_frequency_penalty,
            presence_penalty=args.resident_presence_penalty
        )
        self.resident_profile = resident_profile
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

        self.prompt = (
            "You need to narrate all your current basic information to the public in the first person, in one paragraph. "
            "Start with `<basic_information>` and end with `</basic_information>`.\n"
            "You should then report each piece of basic information that you are about to change in a single dictionary "
            "formatted as {\"xxx\":\"xxx\"}, wrapped in <change></change> tags.\n"
        )
        self.update(to_change_dict={})
        super(Resident, self).__init__(engine)
        self.id = resident_id

    @staticmethod
    def to_description(res_dict):
        record = {
            'gender': f'You are a {res_dict["Gender"]}.',
            'age': f'Your age is {res_dict["Age"]}.',
            'FOH': f'You {"have" if res_dict["family_history_with_overweight"] == "yes" else "haven\'t"} got a family overweight (FOH) history.',
            'FAVC': f'You {"have" if res_dict["FAVC"] == "yes" else "don\'t have"} the habit of frequent intake of high-caloric food (FAVC).',
            'FCVC': f'You {"always" if res_dict["FCVC"] == 3 else "sometimes" if res_dict["FCVC"] == 2 else "never"} have vegetables (FCVC) in your meals.',
            'NCP': f'You take {res_dict["NCP"]} meals per day (NCP).',
            'CAEC': f'You {res_dict["CAEC"]} take food between meals (CAEC).',
            'SMOKE': f'You are {"a smoker" if res_dict["SMOKE"] == "yes" else "not a smoker"} (SMOKE).',
            'CH2O': f'You drink {"more than 2" if res_dict["CH2O"] == 3 else "between 1 and 2" if res_dict["CH2O"] == 2 else "less than 1"} liters of water per day (CH2O).',
            'SCC': f'You {"monitor" if res_dict["SCC"] == "yes" else "don\'t monitor"} calorie intake (SCC).',
            'FAF': f'You exercise {res_dict["FAF"]} days per week (FAF).',
            'TUE': f'You use technological devices for {res_dict["TUE"]} hours per day (TUE).',
            'CALC': f'You {res_dict["CALC"]} consume alcohol (CALC).',
            'MTRANS': f'You usually use {res_dict["MTRANS"]} for transport/commuting (MTRANS).',
        }
        return "\n".join(record.values())

    @staticmethod
    def add_parser_args(parser):
        parser.add_argument('--resident_openai_api_key', type=str, help='API key for OpenAI')
        parser.add_argument('--resident_openai_api_base', type=str, help='API base for OpenAI')
        parser.add_argument('--resident_openai_model_name', type=str, help='API model name for OpenAI')
        parser.add_argument('--resident_temperature', type=float, default=0.0, help='temperature')
        parser.add_argument('--resident_max_tokens', type=int, default=2048, help='max tokens')
        parser.add_argument('--resident_top_p', type=float, default=1, help='top p')
        parser.add_argument('--resident_frequency_penalty', type=float, default=0, help='frequency penalty')
        parser.add_argument('--resident_presence_penalty', type=float, default=0, help='presence penalty')

    def speak(self, role, content, save_to_memory=True):
        messages = [{"role": memory[0], "content": memory[1]} for memory in self.memories]
        messages.append({"role": "user", "content": f"<{role}> {content}"})
        response = self.engine.get_response(messages)

        if not response.strip():
            raise ValueError("Response from GPT is empty!")

        if save_to_memory:
            self.memorize(("user", f"<{role}> {content}"))
            self.memorize(("assistant", response))

        return response

    def parse_role_content(self, response):
        response = response.strip()
        if not response:
            raise ValueError("Response is empty or invalid!")

        try:
            basic_info = re.search(r"<basic_information>(.*?)</basic_information>", response).group(1)
        except AttributeError:
            basic_info = "No basic information found."

        try:
            to_change = re.search(r"<change>(.*?)</change>", response).group(1)
            to_change_dict = json.loads(to_change)
        except (AttributeError, json.JSONDecodeError) as e:
            to_change_dict = {}
            print(f"Error parsing <change> content: {e}")
            print(f"Response content: {response}")

        return basic_info, to_change_dict

    def update(self, to_change_dict):
        for k, v in to_change_dict.items():
            self.resident_profile[k] = v

        self.basic_info = (
            "You are a virtual resident, with specific daily activities and personal information that may affect your obesity status.\n"
            "Your current basic information is, content in () is the abbreviation for each feature for your understanding, do not report them when you are told to report your basic information:\n"
            f"{self.to_description(self.resident_profile)}\n"
            "You have the ability to change parts of your basic information each round. Use the values provided in `model_dict` to make these changes. Randomly adjust between 1-3 pieces of personal information each round.\n"
        )

        self.system_message = self.basic_info + self.prompt
        self.forget()
