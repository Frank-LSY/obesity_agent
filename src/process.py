from utils.register import registry
import engine
import agents
import hospital
import utils
from utils.options import get_parser
import json
import jsonlines
from colorama import Fore, Style
import os

def load_resident_profile(resident_type,filepath):
    with open(filepath, encoding='utf-8') as file:
        f = json.load(file)
        if resident_type=='normal':
            return f[12]
        if resident_type=='overweight':
            return f[256]
        if resident_type=='obesity':
            return f[165]

def initialize_agents(args, resident_profile):
    evaluator = registry.get_class("Agent.Evaluator.GPT")(args)
    doctor = registry.get_class(args.doctor)(args)
    resident = registry.get_class("Agent.Resident.GPT")(args, resident_profile=resident_profile)
    return evaluator, doctor, resident

def simulate_turn(dialog_history, turn, resident, evaluator, doctor):
    print(f"\n{Fore.BLUE}********** Turn {turn}: Simulation Starts **********{Style.RESET_ALL}")
    
    # resident basic information
    resident_response = resident.speak(dialog_history[-1]["role"], dialog_history[-1]["content"])
    # print(resident_response)
    dialog_history.append({"turn": turn, "role": "Resident", "content": resident_response})
    
    print(f"\n{Fore.CYAN}********* Resident **************{Style.RESET_ALL}")
    basic_info, obesity_goal, feeling, to_change = resident.parse_role_content(resident_response)
    print(f"{Fore.YELLOW}Basic Info:{Style.RESET_ALL} {basic_info}")
    print(f"{Fore.YELLOW}Obesity Goal:{Style.RESET_ALL} {obesity_goal}")
    print(f"{Fore.YELLOW}Feeling:{Style.RESET_ALL} {feeling}")
    print(f"{Fore.YELLOW}Proposed Changes:{Style.RESET_ALL} {to_change}")
    
    # evaluate the basic information
    evaluator_response = evaluator.speak(basic_info)
    score, trend, description, consult = evaluator.parse_role_content(evaluator_response)
    dialog_history.append({"turn": turn, "role": "Evaluator", "content": evaluator_response})
    print(f"\n{Fore.CYAN}********* Evaluator **************{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Health Score:{Style.RESET_ALL} {score}")
    print(f"{Fore.YELLOW}Trend:{Style.RESET_ALL} {trend}")
    print(f"{Fore.YELLOW}Evaluation Description:{Style.RESET_ALL} {description}")
    print(f"{Fore.YELLOW}Consult Doctor? {Style.RESET_ALL}{consult}")
    
    # doctor intervention or resident self adjustment
    if consult == 'Yes':
        # Pass obesity goal and feeling to doctor along with basic info and score
        doctor_response = doctor.speak(basic_info, score, feeling, obesity_goal)
        # print(doctor_response)
        dialog_history.append({
            "turn": turn, 
            "role": "Doctor", 
            "content": doctor_response})
        doctor_to_change, instruction, freeze_rounds = doctor.parse_role_content(doctor_response)
        print(f"\n{Fore.CYAN}********* Doctor **************{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Doctor's Instruction:{Style.RESET_ALL} {instruction}") 
        resident.set_freeze(0)
        resident.update(doctor_to_change)
        resident.set_freeze(freeze_rounds)
    else:
        resident.update(to_change)

    dialog_history.append({
        "turn": turn, 
        "role": "assistant", 
        "content": 'Please continue to provide all required fields in the specified JSON format, including "basic_information", "obesity_goal", "feeling", and "change". Ensure the response is valid JSON.'})
    return dialog_history

    
def save_dialog_info(save_path, dialog_info):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    try:
        with jsonlines.open(save_path, "a") as f:
            f.write(dialog_info)
        print(f"{Fore.GREEN}Dialog information successfully saved to {save_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error saving dialog information: {e}{Style.RESET_ALL}")


if __name__ == "__main__":
    args = get_parser()
    resident_profile = load_resident_profile(args.resident_type, args.resident_profile_path)
    print(f"\n{Fore.GREEN}Resident Profile Loaded:{Style.RESET_ALL} {resident_profile}")
    
    evaluator, doctor, resident = initialize_agents(args, resident_profile)
    
    dialog_history = [{"turn": 0, "role": "assistant", "content": 'A simulation start.'}]
    resident.memorize(("assistant", 'A new round start.'))

    for turn in range(1, int(args.turn)):
        dialog_history = simulate_turn(dialog_history, turn, resident, evaluator, doctor)
    
    save_dialog_info(args.save_path,dialog_history)

