
# GPT-4
# echo "GPT-4"
# export OPENAI_API_KEY=""
# export OPENAI_API_BASE=""
# python run.py --patient_database ./data/patients.json \
#     --doctor Agent.Doctor.GPT --doctor_openai_model_name gpt-4 \
#     --patient Agent.Patient.GPT --patient_openai_model_name gpt-3.5-turbo \
#     --reporter Agent.Reporter.GPT --reporter_openai_model_name gpt-3.5-turbo \
#     --save_path outputs/dialog_history_iiyi/dialog_history_gpt4_0222.jsonl \
#     --max_conversation_turn 10 # --max_workers 8 --parallel

# GPT-3.5-Turbo
# echo "GPT-3.5-Turbo"
# export OPENAI_API_KEY="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"
export OPENAI_API_KEY=""
export OPENAI_API_BASE="https://api.openai.com/v1/"
python ../run.py --patient_database ../data/patients.json \
    --resident Agent.Resident.GPT --resident_openai_model_name gpt-3.5-turbo \
    --doctor Agent.Doctor.GPT --doctor_openai_model_name gpt-3.5-turbo \
    --patient Agent.Patient.GPT --patient_openai_model_name gpt-3.5-turbo \
    --ff_print True \
    --reporter Agent.Reporter.GPT --reporter_openai_model_name gpt-3.5-turbo \
    --save_path ../outputs/dialog_history_lsy/dialog_history_gpt3_noreporter.jsonl \
    --max_conversation_turn 8 # --max_workers 8 --parallel