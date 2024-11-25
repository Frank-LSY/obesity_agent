export OPENAI_API_KEY="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"
export OPENAI_API_BASE="https://api.openai.com/v1/"
python ../test.py --resident Agent.Resident.GPT --resident_openai_model_name gpt-3.5-turbo \
    --evaluator Agent.Evaluator.GPT --evaluator_openai_model_name gpt-3.5-turbo \
    --patient Agent.Patient.GPT --patient_openai_model_name gpt-3.5-turbo \
    --ff_print True \