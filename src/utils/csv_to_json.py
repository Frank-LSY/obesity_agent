import pandas as pd
import json

# convert CSV to json for convinient usage

def csv_to_pd(csv_file,json_file):
    df = pd.read_csv(csv_file)
    patient_list = []
    for idx,row in df.iterrows():
        record = {'index':idx+1}
        for column in df.columns:
            record[column] = row[column]
        patient_list.append(record)
    
    with open(json_file, 'w') as f:
        json.dump(patient_list,f,indent=4)
    return
    
if __name__ == '__main__':
    csv_to_pd('../data/ObesityDataSet.csv','../data/obesity.json')
    