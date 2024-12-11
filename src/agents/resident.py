from .base_agent import Agent
from utils.register import register_class, registry
import random
import re
import json
from colorama import Fore, Style
@register_class(alias="Agent.Resident.GPT")
class Resident(Agent):
    def __init__(self, args, resident_profile, resident_id=0, obesity_goal=None):
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
        self.freeze_rounds = 0
        self.obesity_goal = args.resident_obesity_goal or self.resident_profile.get("obesity_goal", "Maintain")  # 默认目标为“保持现状”
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
        parser.add_argument('--resident_temperature', type=float, default=0.2, help='temperature')
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
            # 解析JSON格式的内容
            response_dict = json.loads(response)
            
            # 提取 basic_information、obesity_goal、feeling 和 change 字段
            basic_info = response_dict.get("basic_information", "No basic information found.")
            obesity_goal = response_dict.get("obesity_goal", "No obesity goal specified.")
            feeling = response_dict.get("feeling", "No feelings reported.")
            to_change_dict = response_dict.get("change", {})
            
        except (json.JSONDecodeError, AttributeError) as e:
            basic_info = "No basic information found."
            obesity_goal = "No obesity goal specified."
            feeling = "No feelings reported."
            to_change_dict = {}
            # 可选：打印错误信息以调试
            # print(f"Error parsing JSON response: {e}")
            # print(f"Response content: {response}")

        return basic_info, obesity_goal, feeling, to_change_dict

    def set_freeze(self, freeze_rounds):
        self.freeze_rounds = freeze_rounds
        print(f"{Fore.YELLOW}Freeze rounds set to: {freeze_rounds}{Style.RESET_ALL}")
    
    def decrement_freeze(self):
        if self.freeze_rounds > 0:
            self.freeze_rounds -= 1
            print(f"{Fore.YELLOW}Freeze rounds remaining: {self.freeze_rounds}{Style.RESET_ALL}")
    
    def update(self, to_change_dict):
        # print(self.freeze_rounds)
        if self.freeze_rounds == 0:  # Apply updates only if not frozen
            for key, value in to_change_dict.items():
                self.resident_profile[key] = value
            print(f"{Fore.GREEN}Profile updated with changes: {to_change_dict}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Profile is frozen. No updates applied.{Style.RESET_ALL}")
            self.decrement_freeze()

        # 在 prompt 中添加 obesity_goal 的说明
        self.basic_info = (
            "You are a virtual resident, with specific daily activities and personal information that may affect your obesity status.\n"
            "Your current basic information is, content in () is the abbreviation for each feature for your understanding, do not report them when you are told to report your basic information:\n"
            f"{self.to_description(self.resident_profile)}\n"
            f"Your current obesity goal is: {self.obesity_goal}.\n"
            "Based on this goal, you should consider making changes to your habits in alignment with your objective (e.g., reducing calorie intake for 'Reduce', or increasing calorie intake for 'Increase').\n"
            "You have the ability to change parts of your basic information each round. Use the values provided in `model_dict` to make these changes. Adjust between 1-3 pieces of personal information each round based on your obesity goal.\n"
        )

        # 将 obesity_goal 的提示添加到 system_message
        self.system_message = (
            self.basic_info
            + "In each interaction, generate your current basic information completely in the first person, in one paragraph, "
            "and summarize your current obesity goal and feelings based on this information.\n"
            "{\n"
                "  \"basic_information\": \"Your summarized basic information here...\",\n"
                "  \"obesity_goal\": \"Your current obesity goal...\",\n"
                "  \"feeling\": \"Your feelings about your current status...\",\n"
                "  \"change\": {\n"
                "    \"attribute\": \"value\",\n"
                "    ... (other attributes to change, if any)\n"
                "  }\n"
                "}\n\n"
                "Guidelines:\n"
                "1. Ensure the response is a valid JSON object. Avoid using double braces like {{...}}.\n"
                "2. Provide all specified fields (`basic_information`, `obesity_goal`, `feeling`, `change`).\n"
                "3. Ensure `change` contains a dictionary with key-value pairs for proposed changes.\n\n"
                "Example output:\n"
                "{\n"
                "  \"basic_information\": \"I am a 35-year-old male, weighing 90kg, with a height of 175cm.\",\n"
                "  \"obesity_goal\": \"I want to lose weight and reduce my BMI.\",\n"
                "  \"feeling\": \"I feel motivated but struggle with sticking to a routine.\",\n"
                "  \"change\": {\n"
                "    \"FAVC\": \"no\",\n"
                "    \"NCP\": 3\n"
                "  }\n"
                "}\n\n"
                "If your response does not meet the format, it will be rejected."
        )

        self.forget()

