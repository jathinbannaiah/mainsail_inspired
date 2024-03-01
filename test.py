import requests

api = "192.168.137.11"
params = {"apikey": 'B508534ED20348F090B4D0AD637D3660'}

get_Temp_cmd = {
            "command": "M114"
        }

req = requests.get(url=f"http://{api}/api/printer", params=params)
req.raise_for_status()

temp = req.json()
print(temp["temperature"])