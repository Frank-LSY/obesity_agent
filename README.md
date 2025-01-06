## Large Language Model Generative Agents for Obesity Simulation

Frank-LSY

## Environment Setup
To set up your environment, run the following command:
```
pip install -r requirements.txt
```

## Run the Simulation
Navigate to the source directory:
```
cd ./src/scripts
```
Before running the script, open `scripts/run.sh` and enter your API keys for the required services.
- For OpenAI Models (e.g., GPT-4): `OPENAI_API_KEY=""`, `OPENAI_API_BASE=""`
Execute the script with:
```
bash scripts/run.sh
```

## Get Statistical Figures
open the `figure.ipynb` and run each cell.

## Original Dataset Location

```
data/ObesityDataSet.csv
```
Or you can download the data from [Estimation of Obesity Levels Based On Eating Habits and Physical Condition](https://archive.ics.uci.edu/dataset/544/estimation+of+obesity+levels+based+on+eating+habits+and+physical+condition)

[This paper](https://thescipub.com/pdf/jcssp.2019.67.77.pdf) described the dataset in detail.
