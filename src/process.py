from utils.register import registry
import engine
import agents
import hospital
import utils
from utils.options import get_parser
import json

# 数据初始化
def load_resident_profile(filepath):
    with open(filepath, encoding='utf-8') as file:
        return json.load(file)[0]

def initialize_agents(args, resident_profile):
    evaluator = registry.get_class("Agent.Evaluator.GPT")(args)
    doctor = registry.get_class(args.doctor)(args)
    resident = registry.get_class("Agent.Resident.GPT")(args, resident_profile=resident_profile)
    return evaluator, doctor, resident

def simulate_turn(dialog_history, turn, resident, evaluator, doctor):
    # 居民生成响应
    resident_response = resident.speak(dialog_history[-1]["role"], dialog_history[-1]["content"])
    dialog_history.append({"turn": turn, "role": "Resident", "content": resident_response})
    # print(f"\nTurn {turn} - Resident: {resident_response}")
    
    # 解析居民响应
    basic_info, to_change = resident.parse_role_content(resident_response)
    print(f"Basic Info: {basic_info}, Changes: {to_change}")
    
    # 评估代理的分析
    evaluator_response = evaluator.speak(basic_info)
    score, trend, description, consult = evaluator.parse_role_content(evaluator_response)
    print(f"Evaluator: {description}")
    
    # 医生介入或居民自行调整
    if consult == 'Yes':
        doctor_response = doctor.speak(basic_info, score)
        doctor_to_change, instruction = doctor.parse_role_content(doctor_response)
        print(f"Doctor Instruction: {instruction}")
        resident.update(doctor_to_change)
    else:
        resident.update(to_change)

    # 添加下一轮提示
    dialog_history.append({"turn": turn, "role": "assistant", "content": 'continue to report your basic information and change to make in the desired format.'})
    return dialog_history

# 主程序
if __name__ == "__main__":
    args = get_parser()
    resident_profile = load_resident_profile('../data/obesity.json')
    print(resident_profile)
    evaluator, doctor, resident = initialize_agents(args, resident_profile)
    
    dialog_history = [{"turn": 0, "role": "assistant", "content": 'A simulation start.'}]
    resident.memorize(("assistant", 'A new round start.'))

    for turn in range(1, 2):  # 模拟三轮对话
        dialog_history = simulate_turn(dialog_history, turn, resident, evaluator, doctor)

