
# writing polish char to JSON
# https://stackoverflow.com/questions/18337407/saving-utf-8-texts-in-json-dumps-as-utf8-not-as-u-escape-sequence


import json
import io

string = {
    'a': 'Grąd Górzyca Kamień Pom.',
    'b': 'Grąd Górzyca Kamień Pom.',
}

json_string = json.dumps(string, ensure_ascii=False)
# json_string = json.dumps(string, ensure_ascii=False).encode('utf-8')

print(json_string)

with open('output/a.json', 'w') as f:
    f.write(json_string)