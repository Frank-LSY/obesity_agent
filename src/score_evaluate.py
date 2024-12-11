from utils.register import registry
import engine
import agents
import hospital
import utils
from utils.options import get_parser
import json
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def load_resident_profile(filepath):
    with open(filepath, encoding='utf-8') as file:
        return json.load(file)



def plot_correlation(df, save_path='./correlation.png'):
    plt.figure(figsize=(8, 6))
    sns.boxplot(x='NObeyesdad', y='score', data=df, hue='NObeyesdad', palette="husl")
    plt.title('Evaluation Score vs. Obesity Status')
    plt.xlabel('Obesity Status')
    plt.ylabel('Evaluation Score')
    plt.savefig(save_path, dpi=900)
    
    
if __name__ == "__main__":
    args = get_parser()
    resident_profiles = load_resident_profile('../data/obesity_real.json')
    evaluator = registry.get_class("Agent.Evaluator.GPT")(args)
    results = []
    for resident_profile in resident_profiles:
        resident = registry.get_class("Agent.Resident.GPT")(args, resident_profile=resident_profile)
        dialog_history = [{"role": "assistant", "content": 'A simulation start.'}]
        resident_response = resident.speak(dialog_history[-1]["role"], dialog_history[-1]["content"])
        basic_info, _, _, _ = resident.parse_role_content(resident_response)
        evaluator_response = evaluator.speak(basic_info)
        score, _ ,description ,_ = evaluator.parse_role_content(evaluator_response)
        results.append({
            "index": resident_profile["index"],
            "score": score,
            "description" : description,
            "NObeyesdad": resident_profile["NObeyesdad"]
        })
        print(resident_profile['index'],score)
        
    df = pd.DataFrame(results)
    df.to_json('../outputs/evaluation/score_real.json', orient='records', indent=2)
    plot_correlation(df, save_path='../outputs/evaluation/correlation_real.png')