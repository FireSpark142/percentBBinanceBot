from src.pre_processing.DataConstants import *
import json


def read_api_keys_json():
    login_path = DATA_FOLDER_LOCATION + "login_info/login.json"
    with open(login_path) as f:
        login_data = json.load(f)
    return login_data