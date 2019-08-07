import json
import APICconfig

defaultsettings = APICconfig.defaults

with open('APICconfig.json', 'w') as f:
    json.dump(defaultsettings, f,indent=1)