from create_pipe import build_network
from fh_pipes import get_flow, DummyEntity, Refinery
import numpy as np
import json

with open("new_project.json","r") as f:
    data = json.load(f)

network = build_network(data)

get_flow(network)

max_id = 0
for v in data["layers"]:
    max_id = max(max_id,v["id"])
for n in network:
    for e in data["entities"]:
        if e["id"]==n.id and not isinstance(n,DummyEntity):

            flow_avg = np.mean(n.flow_hist[-int(600/n.tick):])
            max_id+=1
            ds = getattr(n,"deep_storage",0)
            if isinstance(ds,list):
                ds = ds[0]
            sp = getattr(n,"stockpile",0)
            new_layer ={
            "id": max_id,
            "name": f"{n.id}:{flow_avg:.2f}:{ds:.2f}:{sp:.2f}",
            "visible": True,
            "selected": False,
            "locked": False,
            "zIndex": max_id
            }
            data["layers"].append(new_layer)
            e["layer"]=max_id


with open("results.json","w") as f:
    json.dump(data,f,indent=4)