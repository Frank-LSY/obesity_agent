# export OPENAI_API_KEY=""
export OPENAI_API_BASE="https://api.openai.com/v1/"

# to get all evaluation score
python ../score_evaluate.py --resident Agent.Resident.GPT --resident_openai_model_name gpt-3.5-turbo \
    --evaluator Agent.Evaluator.GPT --evaluator_openai_model_name gpt-3.5-turbo \


# to get the specific resident score
python ../process.py --resident_profile_path ../data/obesity.json\
    --resident Agent.Resident.GPT --resident_openai_model_name gpt-3.5-turbo \
    --evaluator Agent.Evaluator.GPT --evaluator_openai_model_name gpt-3.5-turbo \
    --doctor Agent.Doctor.GPT --doctor_openai_model_name gpt-3.5-turbo \
    --save_path ../outputs/dialog_history_red/dialog_history_gpt3.5.jsonl \
    --resident_obesity_goal Decrease --resident_type overweight --turn 6 \