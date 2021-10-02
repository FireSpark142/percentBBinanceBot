from src.pre_processing.DataConstants import *
import json


def read_api_keys_json():
    api_keys_file = DATA_FOLDER_LOCATION + "/APIKeys.json"
    with open(api_keys_file) as f:
        api_keys = json.load(f)
    return api_keys