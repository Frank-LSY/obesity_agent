import pandas as pd
import json

def csv_to_pd(csv_file,json_file):
    df = pd.read_csv(csv_file)
    patient_list = []
    for idx,row in df.iterrows():
        record = {'index':idx+1}
        for column in df.columns:
            record[column] = row[column]

        # record = {
        #     'index':idx+1,
        #     'gender': f'You are a {row['Gender']}. ',
        #     'age': f'Your age is {row['Age']}. ',
        #     'height': f'Your height is {row['Height']} m. ',
        #     'weight': f'Your weight is {row['Weight']} kg. ',
        #     'FOH': f'You {'have' if row['family_history_with_overweight']=='yes' else 'haven\'t'} got a family overweight history. ' ,
        #     'FAVC': f'You {'have' if row['FAVC']=='yes' else 'don\'t have'} the habit of frequent intake of high-caloric food. ',
        #     'FCVC': f'You {'always' if row['FCVC']==3 else 'sometimes' if row['FCVC']==2 else 'never'} have vegetables in your meals. ',
        #     'NCP': f'You take {row['NCP']} meals per day. ',
        #     'CAEC': f'You {row['CAEC']} take food between meals. ',
        #     'SMOKE': f'You are {'' if row['SMOKE']=='yes' else 'not'} a smoker. ',
        #     'CH2O': f'You drink {'more than 2' if row['FCVC']==3 else 'between 1 and 2' if row['FCVC']==2 else 'less than 1'} liters of water per day. ',
        #     'SCC': f'You {'monitor' if row['SCC']=='yes' else 'don\'t monitor'} calorie intake when eating. ',
        #     'FAF': f'You exercise {row['FAF']} days per week. ',
        #     'TUE': f'Every day, you use technological devices, such as cell phone, video games, television and others for {row['TUE']} hours. ',
        #     'CALC': f'You {row['CALC']} intake alcohol. ',
        #     'MTRANS': f'You usually use {row['MTRANS']} to transport/commute.',
        #     'NObeyesdad': f'You are currently in {row['NObeyesdad']}.'
        # }
        # record['profile'] = ''
        # for k,v in record.items():
        #     if k=='index' or k=='height' or k=='weight' or k=='NObeyesdad':
        #         continue
        #     record['profile'] += v+'\n'
        patient_list.append(record)
    
    with open(json_file, 'w') as f:
        json.dump(patient_list,f,indent=4)
    return
    
if __name__ == '__main__':
    csv_to_pd('../data/ObesityDataSet.csv','../data/obesity.json')
    