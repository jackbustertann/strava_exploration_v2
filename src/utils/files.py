import yaml
import json
import os
import csv

def load_yaml(file_path):

    with open(file_path, 'r') as f:
        try:
            settings = yaml.safe_load(f)
        except yaml.YAMLError as exc:
            raise Exception(exc)
    
    return settings

def output_to_json(response_json: dict, file: str):

    n_rows = len(response_json)

    with open(file, 'w') as f:
        json.dump(response_json, f, indent = 1)

    return print(f"{n_rows} rows outputted to file {file} \n")

def output_to_csv(df, file, index = False, schema = []):

    n_rows = len(df)
    
    df.to_csv(file, index = index)

    if len(schema) > 0:
        reorder_csv(file, schema)

    return print(f"{n_rows} rows outputted to file {file} \n")

def reorder_csv(file, schema):

    temp_file = file.split('.')[0] + '_temp.csv'

    os.rename(file, temp_file)

    with open(temp_file, 'r') as infile, open(file, 'a') as outfile:

        bq_cols = [col['name'] for col in schema]

        writer = csv.DictWriter(outfile, fieldnames = bq_cols)

        writer.writeheader()

        for row in csv.DictReader(infile):

            writer.writerow(row)
    
    os.remove(temp_file)

# jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' test_dict.json