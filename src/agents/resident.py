# resident agent representation
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
            'FAVC': ['yes','no'],
            'FCVC': [1,2,3],
            'NCP': [1,2,3,4,5],
            'CAEC':['Never','Sometimes','Frequently','Always'],
            'CH2O':[1,2,3],
            'SCC': ['yes','no'],
            'FAF': [0,1,2,3],
            'TUE': [0,1,2],
            'CALC': ['no','Sometimes','Frequently','Always'],
            'MTRANS':['Public_Transportation','Walking','Automobile','Motorbike','Bike']
        }
        
        self.basic_info = "You are a resident.\n "+\
            f"You may change several pieces of your basic information randomly each round, drawing from the values in `{self.model_dict}`.  \n" + \
            "Here's your basic information:\n" + \
            "{}\n".format(self.to_description(self.resident_profile))
            

        # change to any random disease they have, 诱导发散思考的相关prompt
        self.prompt = "You need to narrate all your current basic information to the public in the first person, in one paragraph. Start with `<basic_information>` and end with `</basic_information>`.\n" + \
            "You should then report each piece of basic information that you are about to change in a single dictionary formatted as {\"xxx\":\"xxx\"}, wrapped in <change></change> tags.\n"
        
        self.system_message = self.basic_info + self.prompt

        # print(self.system_message)
        super(Resident, self).__init__(engine)
        self.id = resident_id
        

    @staticmethod
    def to_description(res_dict):
        # print(res_dict)
        backstory = ''
        record = {
            'gender': f'You are a {res_dict['Gender']}.',
            'age': f'Your age is {res_dict['Age']}. ',
            'FOH': f'You {'have' if res_dict['family_history_with_overweight']=='yes' else 'haven\'t'} got a family overweight history. ' ,
            'FAVC': f'You {'have' if res_dict['FAVC']=='yes' else 'don\'t have'} the habit of frequent intake of high-caloric food. ',
            'FCVC': f'You {'always' if res_dict['FCVC']==3 else 'sometimes' if res_dict['FCVC']==2 else 'never'} have vegetables in your meals. ',
            'NCP': f'You take {res_dict['NCP']} meals per day. ',
            'CAEC': f'You {res_dict['CAEC']} take food between meals. ',
            'SMOKE': f'You are {'' if res_dict['SMOKE']=='yes' else 'not'} a smoker. ',
            'CH2O': f'You drink {'more than 2' if res_dict['FCVC']==3 else 'between 1 and 2' if res_dict['FCVC']==2 else 'less than 1'} liters of water per day. ',
            'SCC': f'You {'monitor' if res_dict['SCC']=='yes' else 'don\'t monitor'} calorie intake when eating. ',
            'FAF': f'You exercise {res_dict['FAF']} days per week. ',
            'TUE': f'Every day, you use technological devices, such as cell phone, video games, television and others for {res_dict['TUE']} hours. ',
            'CALC': f'You {res_dict['CALC']} intake alcohol. ',
            'MTRANS': f'You usually use {res_dict['MTRANS']} to transport/commute.',
        }
        for k,v in record.items():
            backstory += v+'\n'
        return backstory
        
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
        responese = self.engine.get_response(messages)
        if save_to_memory:
            self.memorize(("user", f"<{role}> {content}"))
            self.memorize(("assistant", responese))

        return responese
    
    # 需要更新system message
    # 如何一直提供prompt
    def parse_role_content(self,response):
        response = response.replace("\n","")
        start = "<basic_information>"
        end = "</basic_information>"
        basic_information = re.search(f"{re.escape(start)}(.*?){re.escape(end)}", response).group(1)
        # print(type(basic_information.group(1)))
        start = "<change>"
        end = "</change>"
        to_change = re.search(f"{re.escape(start)}(.*?){re.escape(end)}", response).group(1)
        to_change_dict = json.loads(to_change)
        return basic_information, to_change_dict
    
    # update system message with new random data
    def update(self,to_change_dict):
        for k,v in to_change_dict.items():
            self.resident_profile[k] = v
        self.basic_info = "You are a resident.\n "+\
            f"You may change several pieces of your basic information randomly each round, drawing from the values in `{self.model_dict}`.  \n" + \
            "Here's your basic information:\n" + \
            "{}\n".format(self.to_description(self.resident_profile))
        
        self.system_message = self.basic_info + self.prompt
        self.forget()

