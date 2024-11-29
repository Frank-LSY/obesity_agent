from .base_agent import Agent
from utils.register import register_class, registry
import json
import random

@register_class(alias="Agent.Doctor.GPT")
class Doctor(Agent):
    def __init__(self, args):
        """
        初始化 Doctor Agent。
        """
        # 生成 system_message，提供基础的上下文信息
        self.system_message = (
            "You are a doctor specializing in obesity management. Your task is to evaluate the resident's obesity risk based on their provided basic information (as a string) "
            "and suggest interventions. The interventions should be directly actionable and specify changes to the resident's behavior, diet, or lifestyle. "
            "In addition, you will provide rationale for each intervention to ensure the resident understands the reasoning behind the recommendations. "
            "When giving interventions, use clear and simple language suitable for a general audience.\n"
        )

        # 添加 model_dict 的映射关系
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

        # 初始化 GPT 引擎
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

    def speak(self, basic_info, score, save_to_memory=True):
        """
        根据居民基本信息字符串和评估分数生成干预建议和解释。
        """
        if not isinstance(basic_info, str):
            raise ValueError("The 'basic_info' parameter must be a string.")
        if not isinstance(score, (int, float)):
            raise ValueError("The 'score' parameter must be a numeric value.")

        # 调用 GPT 引擎生成干预建议和理由
        prompt = (
            "You are a doctor specializing in obesity management. Based on the resident's basic information, "
            "which is provided as a string, suggest JSON-structured intervention measures and explain the rationale for these interventions. "
            "The interventions should specify exact changes to the resident's attributes, which can be directly implemented.\n\n"
            "Resident's Basic Information:\n{basic_info}\n\n"
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
            "Your response must include the following fields in JSON format:\n"
            "{{\n"
            "  'intervention': {{'attribute_to_change': 'new_value', ...}},\n"
            "  'rationale': '<explanation_for_the_interventions>'\n"
            "}}\n\n"
            "Be sure to suggest realistic changes that are actionable based on the provided data."
        ).format(basic_info=basic_info, score=score)

        # 发送给 GPT 引擎
        response = self.engine.get_response([
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": prompt}
        ])

        # 存储到记忆
        if save_to_memory:
            self.memorize(("user", f"Basic Info: {basic_info}, Score: {score}"))
            self.memorize(("assistant", response))

        # 解析响应并返回
        return response

    def parse_role_content(self, response):
        """
        解析 GPT 的响应内容，将其转为结构化数据。
        """
        print('--------response start---------------')
        print(response)
        print('--------response end---------------')
        try:
            response_dict = json.loads(response)
            intervention = response_dict.get("intervention", {})
            rationale = response_dict.get("rationale", "")
        except json.JSONDecodeError:
            raise ValueError("The GPT response is not in the expected JSON format.")
        
        return intervention, rationale
