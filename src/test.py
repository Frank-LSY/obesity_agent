from utils.register import registry
import engine
import agents
import hospital
import utils
from utils.options import get_parser
import json

if __name__ == '__main__':
    resident_database = json.load(open('../data/obesity.json',encoding='utf-8'))
    args = get_parser()
    # print(args)
    # only one resident now
    resident_profile = resident_database[0]
    # evaluator agent
    evaluator = registry.get_class("Agent.Evaluator.GPT")(
        args,
    )
    # doctor agent
    doctor = registry.get_class(args.doctor)(
            args,
        )
    # resident agent
    resident = registry.get_class("Agent.Resident.GPT")(
                args,
                resident_profile=resident_profile,
            )
    
    dialog_history = [{"turn": 0, "role": "assistant", "content": 'A simulation start.'}]
    resident.memorize(("assistant", 'A new round start.'))
    # how many turns to go
    for turn in range(2):
        # get the resident narration
        resident_response = resident.speak(dialog_history[-1]["role"], dialog_history[-1]["content"])
        # add to resident history
        dialog_history.append({"turn": turn+1, "role": "Resident", "content": resident_response})
        print("--------------------------------------")
        print(dialog_history[-1]["turn"], dialog_history[-1]["role"])
        print(dialog_history[-1]["content"])
        # basic_information, give to the evaluator
        basic_info, to_change = resident.parse_role_content(resident_response)
        print('*****************')
        print('basic_info',basic_info)
        print(to_change)
        resident.update(to_change)
        dialog_history.append({"turn": turn+1, "role": "assistant", "content": 'continue.'})
        # evaluator to speak the point, need to save and draw the pic
        # score = evaluator.speak(basic_info)
        # doctor will judge the next step based on current evaluated score and resident narration.
        # instruction = doctor.speak(basic_info,score)
        # parse the insturction, then feed to resident
        # instruction = doctor.parse_instruction()
        # resident.update()
        # feed basic_info to 
