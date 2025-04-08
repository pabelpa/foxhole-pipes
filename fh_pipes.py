import numpy as np
import random
import matplotlib.pyplot as plt
import json

def gen_2(pb):
    network = [
        {
            "type":"lts",
            "id":0,
            "conn":[1],
            "storage":50000
        },
        {
            "type":"pipe",
            "id":1,
            "conn":[2],
            "storage":0
        },
        {
            "type":"silo",
            "id":2,
            "conn":[3],
            "storage":0
        },
        {
            "type":"pipe",
            "id":3,
            "conn":[4],
            "storage":0
        },
    ]

    for i in range(pb):
        network.append(
            {
            "type":"pipe",
            "id":4+i,
            "conn":[5+i,3+i],
            "storage":0
            },
        )
    network+=[
        {
            "type":"silo",
            "id":4+pb,
            "conn":[5+pb],
            "storage":0
        },
        {
            "type":"pipe",
            "id":4+pb+1,
            "conn":[5+pb+1],
            "storage":0
        },
        {
            "type":"lts",
            "id":4+pb+2,
            "conn":[],
            "storage":0
        },
    ]
    return network

exp_flows = [
    25,12.5,9.375,7.3,5.9,5,4.2,3.6,3.2,2.9
]
exp_flows2 = [
    11.76,
    7.69,
    6.06,
    4.97,
    4.2,
    3.64,
    3.2,
    2.86,
    2.98,
    2.36,
    2.17
]

# for i,j in zip(flows,exp_flows):
#     print(j/i)
class DummyEntity():
    def __init__(self,id):
        self.id = id

    def check_neighbors(self,network):
        pass
    def __repr__(self):
        return "-"
class Liquidly():
    def __init__(self,id,conn,storage):
        self.id = id
        self.conn = [int(c) for c in conn]
        self.storage = storage
        self.flow_hist = []
    def check_neighbors(self,network):
        pass
    def __repr__(self):
        return f"{self.storage}"

class OilWell(Liquidly):
    tick = 1
    def __init__(self, id, conn ,ticks,prod,cycle):
        super().__init__(id, conn, 0)
        self.n_queues = len(ticks)
        self.ticks = ticks
        self.tick_counter = [0]*5
        self.prods = prod
        self.stockpile = 0
        self.cycles = cycle
        
    def send_flow(self,network):
        if len(self.conn)<1:
            return   
        counter = 0
        flow = 0
        for t,p,cyc,tc in zip(self.ticks,self.prods,self.cycles,self.tick_counter):

            if tc==t:    
                n = network[self.conn[0]]
                if n.storage <100 :  
                    n.recieve_flow(p,self.id)
                    flow +=p
                else:
                    self.stockpile+=p
            self.tick_counter[counter]+=1
            if tc==cyc:
                self.tick_counter[counter]= 0
            counter+=1
        self.flow_hist.append(flow)

        return flow  
    def recieve_flow(self,flow,id):
        self.deep_storage+=flow

class Refinery(Liquidly):
    tick = 1
    capacity = 5000
    def __init__(self, id, conn ,ticks,prod,coms,cycles):
        super().__init__(id, conn, 0)
        self.n_queues = len(ticks)
        self.ticks = ticks
        self.tick_counter = [-1]*len(prod)
        self.prod = prod
        self.coms = coms
        self.stockpile = 0
        self.block =[True]*5
        self.deep_storage = 0
        self.cycles = cycles
    def send_flow(self,network):

        counter = 0
        flow = 0
        for t,p,c,cyc,tc in zip(self.ticks,self.prod,self.coms,self.cycles,self.tick_counter):
            # Production and consumption
            if self.deep_storage>c and tc<0:
                self.tick_counter[counter]=0
                self.deep_storage-=c

            # sending flow
            if tc==t and len(self.conn)>0:    
                n = network[self.conn[0]]
                if n.storage <100 :  
                    n.recieve_flow(p,self.id)
                    flow+=p
                else:
                    self.stockpile+=p
            # only start counting if production has started (tc != -1)
            if tc>=0:
                self.tick_counter[counter]+=1

            if tc==cyc:
                self.tick_counter[counter]= -1
            counter+=1
        self.flow_hist.append(flow)

        return flow
            
    def recieve_flow(self,flow,id):
        self.deep_storage+=flow

class DoubleRefinery(Liquidly):
    tick = 1
    capacity = 5000
    def __init__(self, id, conn ,ticks,prod,coms,cycles,ports):
        super().__init__(id, conn, 0)
        self.n_queues = len(ticks)
        self.ticks = ticks
        self.tick_counter = [-1]*5
        self.prod = prod
        self.coms = coms
        self.stockpile = 0
        self.block =[True]*5
        self.deep_storage= [0,0]
        self.cycles = cycles
        self.ports = {
            int(ports[0]):0,
            int(ports[1]):1,
        }
    def send_flow(self,network):

        counter = 0
        flow = 0
        for t,p,c,cyc,tc in zip(self.ticks,self.prod,self.coms,self.cycles,self.tick_counter):
            # Production and consumption
            if tc<0:
                b_produce = True
                for stor,cons in zip(self.deep_storage,c):
                    if stor<cons:
                        b_produce=False
                if b_produce:
                    self.tick_counter[counter]=0
                    self.deep_storage[0]-=c[0]
                    self.deep_storage[1]-=c[1]

            # sending flow  
            if tc==t and len(self.conn)>0:
                n = network[self.conn[0]]
                if n.storage <100 :  
                    n.recieve_flow(p,self.id)
                    flow +=p
                else:
                    self.stockpile+=p
            # only start counting if production has started (tc != -1)
            if tc>=0:
                self.tick_counter[counter]+=1

            # wait for production to start again
            if tc==cyc:
                self.tick_counter[counter]= -1
            counter+=1
        self.flow_hist.append(flow)

        return flow
            
    def recieve_flow(self,flow,id):

        self.deep_storage[self.ports[id]]+=flow

class LTS(Liquidly):
    tick = 1
    liquids={
        "oil":50,
        "water":50,
        "diesel":100,
        "facilityoil1":30,
        "facilityoil2":30,
        "petrol":50
    }
    def __init__(self, id, conn, storage,liquid_type="petrol"):
        super().__init__(id, conn, storage)
        self.deep_storage = storage
        self.storage = 0
        self.flow_rate = self.liquids[liquid_type]
        self.capacity = self.flow_rate*500
    def send_flow(self,network):
        if len(self.conn)<1:
            self.flow_hist.append(0)
            return       
        n = network[self.conn[0]]
        if n.storage <100 and self.deep_storage>=self.flow_rate:  
            n.recieve_flow(self.flow_rate,self.id)
            self.deep_storage-=self.flow_rate
            self.flow_hist.append(self.flow_rate)
            return self.flow_rate
        else:
            self.flow_hist.append(0)
            return 0
    def recieve_flow(self,flow,id):
        self.deep_storage+=flow

class Pipe(Liquidly):
    tick = 2
    capacity = 100
    def check_neighbors(self,network):
        for c in self.conn:
            n = network[c]
            if isinstance(n,Silo):
                self.tick = 3
            if isinstance(n,LTS):
                self.tick = 1
    def send_flow(self,network):

        if len(self.conn)<1:
            return
        flow_accumulated = 0

        # LTS takes priority
        for c in self.conn:
            n = network[c]
            if isinstance(n,LTS):
                space = n.capacity-n.deep_storage
                flow = self.storage-flow_accumulated
                n.recieve_flow(flow,self.id)
                flow_accumulated+=flow
                self.storage-=flow_accumulated

                self.flow_hist.append(flow_accumulated/self.tick)
                return flow_accumulated

        for c in self.conn:
            n = network[c]

            # elif isinstance(n,OilWell):
            #     continue
            
            # Q: does flow to a pipe happen at 1 tick if it is also connected to LTS?
            # A: it does not happen at all
            raw_flow =(self.storage-n.storage)/3
            if raw_flow<0:
                continue
            if isinstance(n,Refinery)  or isinstance(n,Silo):
                space = n.capacity-n.deep_storage
                if raw_flow>space:
                    raw_flow=space
            flow = int(np.ceil(raw_flow))
            flow = raw_flow
            n.recieve_flow(flow,self.id)
            flow_accumulated+=flow
        
        # shuffle s.t. pipes sometimes get flow instead of lts

        self.storage-=flow_accumulated

        self.flow_hist.append(flow_accumulated/self.tick)
        return flow_accumulated
    def recieve_flow(self,flow,id):
        self.storage+=flow

class Silo(Liquidly):
    tick = 3
    capacity = 5000
    def __init__(self, id, conn, storage):
        super().__init__(id, conn, storage)
        self.deep_storage = storage
        self.storage = 0
    def send_flow(self,network):
        if len(self.conn)<1:
            self.flow_hist.append(0)
            return
        n = network[self.conn[0]]
        
        raw_flow =min(100-n.storage,min((self.deep_storage)/3,100))
        flow = raw_flow
        n.recieve_flow(flow,self.id)
        self.deep_storage-=flow
        self.flow_hist.append(flow)
        return flow
    def recieve_flow(self,flow,id):
        self.deep_storage+=flow






def gen_network(net_dict):
    network = []
    for d in net_dict:
        p_type = d.pop("type")
        if p_type=="lts":
            o=LTS(**d)
        if p_type=="silo":
            o=Silo(**d)
        if p_type=="pipe":
            o=Pipe(**d)
        if p_type=="oilwell":
            o=OilWell(**d)
        if p_type=="refinery":
            o=Refinery(**d)
        network.append(o)
    return network



def get_flow(network):
    indices = list(range(len(network)))
    random.shuffle(indices)
    for j in range(7200):
        # print(network[18].deep_storage)
        for i in indices:
            
            o = network[i]
            if isinstance(o,DummyEntity):
                continue
            if j%o.tick!=0:
                continue
            flow = o.send_flow(network)



if __name__=="__main__":
    with open("atismo.json","r") as f:
        data = json.load(f)

    flow_avgs = []
    fig,ax = plt.subplots()
        
    network = gen_network(data)

    for n in network:
        n.check_neighbors(network)

    get_flow(network)

    for f in range(1,len(network[10].flow_hist)):
        flow_avgs.append(np.mean(network[10].flow_hist[0:f]))

    ax.plot(flow_avgs[-100:],label=f"average")
    ax.plot(network[10].flow_hist[-100:],label=f"instant")
    ax.set_xlabel("seconds")
    ax.set_ylabel("flow rate (L/S)")
    ax.legend()
    fig.savefig("flows.svg",format="SVG")

    print(flow_avgs[-1])


