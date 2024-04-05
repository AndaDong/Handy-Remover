import os
import json

dictionary = {
    "num_scans": 0,
    "dir_list": [],
    "len_list": []
}
 
with open("userData.json", "w") as outfile:
    json.dump(dictionary, outfile)