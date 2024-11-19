# resident agent representation
from .base_agent import Agent
from utils.register import register_class, registry

@register_class(alias="Agent.Resident.GPT")
class Resident(Agent):
    def __init__(self, args, resident_profile, medical_records, resident_id=0):
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
        self.system_message = "You are a resident. Here's your basic information.\n" + \
            "{}\n".format(resident_profile)

        # change to any random disease they have
        if "现病史" in medical_records:
            self.system_message += "<现病史> {}\n".format(medical_records["现病史"].strip())        
        if "既往史" in medical_records:
            self.system_message += "<既往史> {}\n".format(medical_records["既往史"].strip())
        if "个人史" in medical_records:
            self.system_message += "<个人史> {}\n".format(medical_records["个人史"].strip())
        self.system_message += "\n"

        self.system_message += \
            "下面会有<医生>来对你的身体状况进行诊断，你需要：\n" + \
            "(1) 按照病历和基本资料的设定进行对话。\n" + \
            "(2) 在每次对话时，你都要明确对话的对象是<医生>还是<检查员>。当你对医生说话时，你要在句子开头说<对医生讲>；如果对象是<检查员>，你要在句子开头说<对检查员讲>。\n" + \
            "(3) 首先按照主诉进行回复。\n" + \
            "(4) 当<医生>询问你的现病史、既往史、个人史时，要按照相关内容进行回复。\n" + \
            "(5) 当<医生>要求或建议你去做检查时，要立即主动询问<检查员>对应的项目和结果，例如：<对检查员讲> 您好，我需要做XXX检查，能否告诉我这些检查结果？\n" + \
            "(6) 回答要口语化，尽可能短，提供最主要的信息即可。\n" + \
            "(7) 从<检查员>那里收到信息之后，将内容主动复述给<医生>。\n" + \
            "(8) 当医生给出诊断结果、对应的诊断依据和治疗方案后，在对话的末尾加上特殊字符<结束>。"
    
        super(Resident, self).__init__(engine)
        self.id = resident_id
        self.medical_records = medical_records

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

    def speak(self):
        pass
    
    @staticmethod
    def parse_role_content(responese):
        pass
