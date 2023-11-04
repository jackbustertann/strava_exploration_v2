import pandas as pd
from typing import Dict, List, Any

def explode_list_key_into_columns(
    response_json: List[dict],
    column_key: str,
    list_key: str
) -> List[dict]:

    return pd.DataFrame({
        response_dict[column_key]: response_dict[list_key]
        for response_dict in response_json
    }).to_dict('records')

def explode_list_key_into_rows(
    response_json: List[dict],
    list_key: str
) -> List[dict]:
    return pd.DataFrame(
        response_json
    ).explode(
        list_key
    ).to_dict('records')

def explode_dict_keys_into_columns(
    response_json: List[dict],
    sep = '_'
) -> pd.DataFrame:

    return pd.json_normalize(
        response_json, 
        sep = sep
    )

def transform_response_json(
    response_json, 
    explode_list_keys = {}, 
    explode_dict_keys = False, 
    set_values={}
) -> pd.DataFrame:

    n_rows = len(response_json)

    if n_rows > 0:

        # explode list keys into rows or columns, if required
        if explode_list_keys:

            assert isinstance(explode_list_keys, dict)

            assert "type" in explode_list_keys.keys()

            assert explode_list_keys["type"] in ["list_key_into_rows", "list_key_into_columns"]

            if explode_list_keys["type"] == "list_key_into_rows":

                assert "list_key" in explode_list_keys.keys()

                assert isinstance(explode_list_keys["list_key"], str) | isinstance(explode_list_keys["list_key"], list)
                
                response_json = explode_list_key_into_rows(
                    response_json,
                    explode_list_keys["list_key"],
                )

            elif explode_list_keys["type"] == "list_key_into_columns":

                assert ("list_key" in explode_list_keys.keys()) & ("column_key" in explode_list_keys.keys())

                assert isinstance(explode_list_keys["list_key"], str) 

                assert isinstance(explode_list_keys["column_key"], str) 
                
                response_json = explode_list_key_into_columns(
                    response_json,
                    explode_list_keys["column_key"],
                    explode_list_keys["list_key"],
                )

        # explode dict keys into columns, if required
        if explode_dict_keys:

            response_df = explode_dict_keys_into_columns(response_json)
        
        else:

            response_df = pd.DataFrame(response_json)

        # set values for new columns (e.g. last modified timestamp)
        assert isinstance(set_values, dict)

        for key, value in set_values.items():
            response_df[key] = value

        return response_df

    return pd.DataFrame()