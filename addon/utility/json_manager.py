import json
import os

from typing import Dict

from .constants import OCTANE_DATA_PATH

def get_json_path() -> str:
    
    if not os.path.exists(OCTANE_DATA_PATH):
        with open(OCTANE_DATA_PATH, "w", encoding='utf8') as file:          
            data = {"saved_user_paths":{}}
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.write("\n")

    return OCTANE_DATA_PATH

def json_check(json_path : str):

    try:
        with open(json_path) as json_file:
            json_data = json.load(json_file)
    except ValueError as e:
        print('QS: Invalid Json')
        return False
    return True  
        
def load_json() -> Dict:
    
    json_check(get_json_path())
    
    with open(get_json_path(), encoding='utf8') as json_file:
        json_data = json.load(json_file)
    
    return json_data

def write_json(data : Dict) -> None:
    
    with open(get_json_path(), "w", encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.write("\n")