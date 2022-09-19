import pandas as pd

def flatten_data(response_json, sep = '_'):

    # test: check specific case

    response_df = pd.json_normalize(response_json, sep = sep)

    return response_df

def explode_data(df, col):

    # test: check specific case

    # creating a copy of data for processing
    df_raw = df.copy()

    # creating a row for every dict
    df_exploded = df_raw.explode(col)

    # creating a column for every dict attribute
    df_widened = pd.json_normalize(df_exploded[col])

    # dropping original col
    df_reduced = df_exploded.drop(columns = col).reset_index(drop = True)

    # combining new col with original data
    df_concat = pd.concat([df_reduced, df_widened], axis = 1)

    return df_concat