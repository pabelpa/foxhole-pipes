import json
from fh_pipes import Pipe,LTS,Silo,OilWell,Refinery,DummyEntity,DoubleRefinery
import random
import copy
pipe_keys = ["pipeline", "pipeline_underground","pipeline_overhead"]
oil_well_keys = ["oil_well_electric_oil","oil_well_fracking","water_pump","water_pump_electric_water"]
oil_refinery_keys = [
    "oil_refinery",
    "oil_refinery_cracking_unit",
    "oil_refinery_petro_plant",
    "materials_factory_metal_press",
    "power_station_sulfuric_reactor",
    "materials_factory_metal_press",
    "metalworks_factory_blast_furnace",
    "metalworks_factory_recycler",
    "materials_factory_forge",
    'diesel_power_plant_petrol_power'
]

dual_refinery_keys ={
    "oil_refinery_reformer",
    "metalworks_factory_engineering_station",
}


oil_well_prod = {
    "oil_well":{
        0:{
            "cycle":50,
            "prod":50
        },
    },
    "oil_well_electric_oil":{
        0:{
            "cycle":26,
            "prod":50
        },
        "outlet":"1"
    },
    "oil_well_fracking":{
        0:{
            "cycle":40,
            "prod":100,
            "coms":25
        },
        "outlet":"1"
    },
    "water_pump_electric_water":{
        0:{
            "cycle":50,
            "prod":50,
        },
        "outlet":"0"
    }
}

refinery_prod = {
    "oil_refinery_petro_plant":{
        0:{
            "cycle":200,
            "prod":30,
            "coms":30,
            "parent":"oil_refinery",
        },
        "outlet":"2"
    },
    "oil_refinery_cracking_unit":{
        0:{
            "cycle":160,
            "prod":90,
            "coms":150,
            "parent":"oil_refinery",
        },
        "outlet":"2"
    },
    "oil_refinery":{
        0:{
            "cycle":150,
            "prod":150,
            "coms":150,
        },
        "outlet":"2"
    },
    "power_station_sulfuric_reactor":{
        0:{
            "cycle":120,
            "prod":0,
            "coms":50
        }
    },
    "diesel_power_plant_petrol_power":{
        0:{
            "cycle":90,
            "prod":0,
            "coms":50
        }
    },
    "materials_factory_metal_press":{
        0:{
            "cycle":25,
            "prod":0,
            "coms":25,
            "parent":"materials_factory"
        }
    },
    "materials_factory_forge":{
        1:{
            "cycle":60,
            "prod":0,
            "coms":50,
            "parent":"materials_factory"
        }
    },
    "metalworks_factory_recycler":{
        0:{
            "cycle":90,
            "prod":0,
            "coms":10,
            "parent":"metalworks_factory"
        }
    },
    "metalworks_factory_blast_furnace":{
        0:{
            "cycle":120,
            "prod":0,
            "coms":66,
            "parent":"metalworks_factory"
        }
    },
}

drefinery_prod = {
    "oil_refinery_reformer":{
        0:{
            "cycle":150,
            "prod":90,
            "coms":[120,30],
            "parent":"oil_refinery",
        },
        "outlet":"2",
        "ports":['1',"3"],
    },
    "metalworks_factory_engineering_station":{
        1:{
            "cycle":90,
            "prod":0,
            "coms":[90,100],
            "parent":"metalworks_factory"
        },
        "ports":["2",'3'],
    }
}
with open("new_project.json","r") as f:
    data = json.load(f)

def build_network(data):
    network = []
    max_id = 0
    for i,entity in enumerate(data["entities"]):
        new_id = entity.get("id",0)
        max_id=max(max_id,new_id)
    for i in range(max_id+1):
        network.append(DummyEntity(i))
    for entity in data["entities"]:
        id = entity["id"]


        if entity.get("key","") in pipe_keys:
            conn = []
            for v in entity.get("connections",{}).values():
                conn.append(list(v.keys())[0])
            obj = Pipe(id,conn,0)
            network[id]=obj
        if entity.get("key","")=="liquid_transfer_station":
            conn = list(entity.get("connections",{}).get("1",{}).keys())
            liquid_type = entity.get("stockpileItems",["petrol"])[0]
            obj = LTS(id,conn,0,liquid_type)
            network[id]=obj
        if entity.get("key","")=="fuel_silo":
            conn = list(entity.get("connections",{}).get("1").keys())
            obj = Silo(id,conn,0)
            network[id]=obj
        if entity.get("key","") in oil_well_keys:
            connectivity_data = entity.get("connections",{"1":{}})

            outlet = oil_well_prod[entity.get("key","")].get("outlet")
            if outlet:
                conn = list(connectivity_data.get(outlet,{}).keys())
            else: conn =[]
            cycles = []
            prods = []
            coms = []
            for po in entity.get("productionOrders",[]):
                order = po["id"]
                if po["parent"]:
                    cycles.append(oil_well_prod["oil_well"][order]["cycle"])
                    prods.append(oil_well_prod["oil_well"][order]["prod"])
                else:
                    cycles.append(oil_well_prod[entity["key"]][order]["cycle"])
                    prods.append(oil_well_prod[entity["key"]][order]["prod"])
                    coms.append(oil_well_prod[entity["key"]][order].get("coms",0))
            ticks = []
            for c in cycles:
                ticks.append(random.randint(0,c))
            if entity.get("key","")=="oil_well_fracking":
                obj = Refinery(id,conn,ticks,prods,coms,cycles)
            else:
                obj = OilWell(id,conn,ticks,prods,cycles)
            network[id]=obj
        if entity.get("key","") in dual_refinery_keys:
            connectivity_data = entity.get("connections",{"2":{}})

            ports = []
            outlet = drefinery_prod[entity["key"]].get("outlet")
            if outlet:
                conn = list(connectivity_data.get(outlet,{}).keys())
            else: conn =[]

            for port in drefinery_prod[entity["key"]].get("ports"):
                ports.append(list(connectivity_data[port].keys())[0])

            cycles = []
            prods = []
            coms = []
            
            for po in entity.get("productionOrders",[]):
                order = po["id"]

                if po["parent"]:
                    order_data = drefinery_prod[entity["key"]].get("parent",{}).get(order,{})
                else:
                    order_data = drefinery_prod[entity["key"]].get(order,{})
                
                c = order_data.get("cycle",0)
                p = order_data.get("prod",-1)
                cn = order_data.get("coms",[])
                if c>0:
                    cycles.append(c)
                if p>=0:
                    prods.append(p)
                if len(cn)>0:
                    coms.append(cn)

            ticks = []
            for c in cycles:
                ticks.append(random.randint(0,c))
            obj = DoubleRefinery(id,conn,ticks,prods,coms,cycles,ports)
            network[id]=obj
        if entity.get("key","") in oil_refinery_keys:
            connectivity_data = entity.get("connections",{"2":{}})

            outlet = refinery_prod[entity["key"]].get("outlet")
            if outlet:
                conn = list(connectivity_data.get(outlet).keys())
            else: conn =[]

            cycles = []
            prods = []
            coms = []

            for po in entity.get("productionOrders",[]):
                order = po["id"]

                if po["parent"]:
                    order_data = refinery_prod[entity["key"]].get("parent",{}).get(order,{})
                else:
                    order_data = refinery_prod[entity["key"]].get(order,{})
                
                c = order_data.get("cycle",0)
                p = order_data.get("prod",-1)
                cn = order_data.get("coms",0)
                if c>0:
                    cycles.append(c)
                if p>=0:
                    prods.append(p)
                if cn>0:
                    coms.append(cn)

            ticks = []
            for c in cycles:
                ticks.append(random.randint(0,c))
            obj = Refinery(id,conn,ticks,prods,coms,cycles)
            network[id]=obj

    network.sort(key=lambda x:x.id)

    # need to make a check if it is an LST, liquid silo, or refinery outlet
    for n in network:
        if isinstance(n,Pipe):
            for c in n.conn[:]:
                other = network[c]
                if isinstance(other, LTS) or isinstance(other,Refinery) or isinstance(other,DoubleRefinery) or isinstance(other,Silo) or isinstance(other,OilWell):
                    if n.id in other.conn:
                        n.conn.remove(other.id)

    for n in network:
        n.check_neighbors(network)
    return network

if __name__=="__main__":
    with open("new_project.json","r") as f:
        data = json.load(f)
    build_network(data)


