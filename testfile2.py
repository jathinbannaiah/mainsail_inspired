import requests
import json

api = "172.19.253.103"


# cmd = {
#     "commands": ["move_hopper_left"]             #was facing some issue with klipper code.
# }
#
# req = requests.post(url=f"http://{api}/api/printer/command", json=cmd, timeout=5)
# req.raise_for_status()
#
# print(req.json())

# cmd = {
#     "script": "M871"
# }
#
# req = requests.get(url=f"http://{api}/printer/gcode/script", params=cmd,timeout=5)
# req.raise_for_status()
#
# print(req.json())

# req = requests.get(url=f"http://{api}/server/gcode_store?count=1",timeout=5)    # to get the responses (in this case the last 100)
# req.raise_for_status()
#
# print(req.json())

#
# req = requests.get(url=f"http://{api}/server/sensors/list",timeout=5)    # to get sensor data # Is available only when [sensor] component is configured
# req.raise_for_status()
#
# print(req.json())

# req = requests.get(url=f"http://{api}/printer/objects/query?gcode_macro move_hopper_left", timeout=5)
# req.raise_for_status()
#
# print(req.json())

#
#req = requests.get(url=f"http://{api}/api/printer",timeout=5)        # get complete printer status
req = requests.get(url=f"http://{api}/server/temperature_store?include_monitors=false",timeout=5)
req.raise_for_status()
req = req.json()
#print(req['result'])
req = req['result']
for key in req:
    print(req[key]['temperatures'][0])
    #print(req[key]['temperatures'][0])


# GET /server/temperature_store?include_monitors=false