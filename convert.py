import json
import re
file = "new_project.plan"

with open(file,"rb") as f:
    data = f.read()
start_ind = data.find(b"project.json")
end_ind = data.find(b"PK\x01")
data = data[start_ind:end_ind]
expr = re.compile("project.json(?P<data>.*})")

res = expr.search(data.decode())
data = res.group("data")

data_dict = json.loads(data)

with open("new_project.json","w") as f:
    json.dump(data_dict,f,indent=4)