import json

#"action" should equal one of those in the given JSON.
ACTIONS = ["move", "archive", "rename", "remove"]
#"when" should equal one of those in the given JSON or multiple.
FILTER  = ["url", "extension","size_mb", "age_days", "name","contains_text" ]
#"format" should equal one of those in the give JSON.
FORMATS = ["zip", "tar"]
#those are the main key
REQUIRED_KEYS = ["when", "action"]
#those are the required filds

# validate JSON, if something in the JSON outside of the desired structure return false.
# look at example.json to understand
# TODO: Improve this to make it update an error list, and raise it back to know where the error happened
def validate_json(json_path, json_error = "") -> tuple[bool,str]:
    try:
        # try to retrieve data from json file
        with open(json_path) as json_data:
            data = json.load(json_data)
    except Exception as e:
        json_error = f"erro occured trying oppening json file: {json_path}, error: {e}"
        return False, json_error
    # the dictionary should always start with 'rules'
    if 'rules' not in data:
        json_error = f'"rules" is missing in json file: {json_path}'
        return False, json_error
    try:
        for row in data['rules']:
            for required in REQUIRED_KEYS:
                # "when" and "action" should always be in the json
                if required not in row:
                    json_error = f'"when" and "action" key can\'t be missing'
                    return False, json_error
            for keys,values in row.items():
                # validate when key is "when"
                if keys == "when":
                    #check if it's empty
                    if not values:
                        json_error = f'"when" key can\'t be empty'
                        return False, json_error
                    for value, subvalues in values.items():
                        #check that it's one of the valid when filters
                        if value not in FILTER:
                            json_error = f'invalid value: {value}, inside of "when"'
                            return False, json_error
                        # if the filter is "size_mb" or "age_days" it should contain less than or more than
                        if value in ("size_mb", "age_days") and isinstance(subvalues, dict) :
                            if not ("greater_than" in subvalues or "less_than" in subvalues):
                                json_error = f'"size_mb" and "age_days" shoud either contain "greater_than" or "less_than" keys'
                                return False, json_error
                # validate when key is "action"
                elif keys == "action":
                    #check if it's empty
                    if not values:
                        json_error = f'"action" key can\'t be empty'
                        return False, json_error
                    #check that it's a valid action type
                    if values not in ACTIONS:
                        json_error = f'invalid value: {values}, inside of "action"'
                        return False, json_error
                    # if the action is "move" or "archive" a dist row should have "dist" key
                    if values == "move" or values == "archive":
                        if row.get("dest") is None:
                            json_error = f'when choosing "move" or "archive", "dest" key should be set'
                            return False, json_error
                    # if the action is rename a "format" key should be there
                    elif values == "rename":
                        if row.get("format") is None:
                            json_error = f'when choosing "rename", "format" key should be set'
                            return False, json_error
                elif keys == "format":
                    #check if it's empty
                    if not values:
                        json_error = f'"format" key can\'t be empty'
                        return False, json_error
                    # if the action is 'archive' the format should be one of the accepted formats
                    if row['action'] == 'archive':
                        if values not in FORMATS:
                            json_error = f'invalid value: {values}, inside of "format" only supported {FORMATS}'
                            return False, json_error
    #for any exception happned trying to parse the json return False
    except Exception as e:
        json_error = f"error occured in json, {e}"
        return False, json_error
    #defulat case
    return True, json_error
