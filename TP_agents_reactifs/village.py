import math
import random
import numpy as np
from collections import defaultdict

import uuid
import mesa
import numpy
import pandas
from mesa import space
from mesa.batchrunner import BatchRunner
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import ModularServer, VisualizationElement, UserSettableParameter
from mesa.visualization.modules import ChartModule

class ContinuousCanvas(VisualizationElement):
    local_includes = [
        "./js/simple_continuous_canvas.js",
    ]

    def __init__(self, canvas_height=500,
                 canvas_width=500, instantiate=True):
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.identifier = "space-canvas"
        if (instantiate):
            new_element = ("new Simple_Continuous_Module({}, {},'{}')".
                           format(self.canvas_width, self.canvas_height, self.identifier))
            self.js_code = "elements.push(" + new_element + ");"

    def portrayal_method(self, obj):
        return obj.portrayal_method()

    def render(self, model):
        representation = defaultdict(list)
        for obj in model.schedule.agents:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.pos[0] - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.pos[1] - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        return representation

def wander(x, y, speed, model):
    r = random.random() * math.pi * 2
    new_x = max(min(x + math.cos(r) * speed, model.space.x_max), model.space.x_min)
    new_y = max(min(y + math.sin(r) * speed, model.space.y_max), model.space.y_min)

    return new_x, new_y

#class GraphVis(VisualizationElement):

    #def __init__(self):



class  Village(mesa.Model):
    def  __init__(self,  n_villagers, n_lycanthropes, n_clerics, n_hunters):
        mesa.Model.__init__(self)

        self.space = mesa.space.ContinuousSpace(600, 600, False)
        self.schedule = RandomActivation(self)

        model_rptrs = {"humans": lambda m: m.count_agents("humans"),
                       "population": lambda m: m.count_agents("all"),
                       "lycanthropes": lambda m: m.count_agents("lycanthropes"),
                       "lycanthropes_transformed": lambda m: m.count_agents("lycanthropes_transformed"),
                       "clerics": lambda m: m.count_agents("clerics"),
                       "hunters": lambda m: m.count_agents("hunters")}
        self.dc = DataCollector(model_reporters=model_rptrs, 
                                agent_reporters=None, 
                                tables=None)

        # Villagers
        for  _  in  range(n_villagers):
            self.schedule.add(Villager(random.random()  *  600,  
                                       random.random()  *  600,  10, 
                                       uuid.uuid4(), 
                                       self,
                                       False))
        # Lycanthropes
        for _ in range(n_lycanthropes):
            self.schedule.add(Villager(random.random()  *  600,  
                                       random.random()  *  600,  10, 
                                       uuid.uuid4(), 
                                       self,
                                       True,
                                       False))
        # Cleric
        for _ in range(n_clerics):
            self.schedule.add(Cleric(random.random()  *  600,  
                                    random.random()  *  600,  10, 
                                    uuid.uuid4(), 
                                    self))
        # Hunters
        for _ in range(n_hunters):
            self.schedule.add(Hunter(random.random()  *  600,  
                                    random.random()  *  600,  10, 
                                    uuid.uuid4(), 
                                    self))
        
        self.dc.collect(self) # initial state
            
    def count_agents(self, type):
        agents = self.schedule.agents
        
        count_villagers = 0 # not lycanthropes
        count_lycanthropes = 0 # all lycanthropes
        count_lycanthropes_transf = 0 # transformed
        count_clerics = 0
        count_hunters = 0
        count_all = len(agents)
        
        if type == "all":
            return count_all

        for a in agents:
            if isinstance(a, Villager):
                if a.isLycanthrope == False:
                    count_villagers += 1
            if isinstance(a, Villager):
                if a.isLycanthrope:
                    count_lycanthropes += 1
                    if a.isTransformed:
                        count_lycanthropes_transf +=1
            if isinstance(a, Cleric): 
                count_clerics += 1
            if isinstance(a, Hunter):
                count_hunters += 1
        
        if type == "humans":
            return count_all - count_lycanthropes
        if type == "lycanthropes":
            return count_lycanthropes
        if type == "lycanthropes_transformed":
            return count_lycanthropes_transf
        if type == "clerics":
            return count_clerics
        if type == "hunters":
            return count_hunters

    def step(self):
        self.dc.collect(self)
        self.schedule.step()
        if self.schedule.steps >= 1000:
            self.running = False

class Villager(mesa.Agent):
    def __init__(self, x, y, speed, unique_id: int, model: Village, isLycanthrope, isTransformed=False, distance_attack=40, p_attack=0.1):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.speed = speed
        self.model = model
        self.isLycanthrope = isLycanthrope
        self.isTransformed = isTransformed
        self.distance_attack = distance_attack
        self.p_attack = p_attack

    def portrayal_method(self):
        if self.isLycanthrope:
            color = "red"
        else:
            color = "blue"
        if self.isLycanthrope and self.isTransformed:
            r = 6
        else:
            r = 3
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": color,
                     "r": r}
        return portrayal

    def step(self):
        self.pos = wander(self.pos[0], self.pos[1], self.speed, self.model)
        if self.isLycanthrope:
            if self.isTransformed:
                other_agents = self.model.schedule.agents
                for a in other_agents:
                    if isinstance(a, Villager):
                        dist = np.sqrt((a.pos[0] - self.pos[0])**2 + (a.pos[1] - self.pos[1])**2)
                        if dist <= self.distance_attack:
                            a.isLycanthrope = True
            self.isTransformed = np.random.rand() <= self.p_attack


class Cleric(mesa.Agent):
    def __init__(self, x, y, speed, unique_id: int, model: Village, distance_care=30):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.speed = speed
        self.model = model
        self.distance_care = distance_care

    def portrayal_method(self):
        color = "green"
        r = 3
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": color,
                     "r": r}
        return portrayal

    def step(self):
        self.pos = wander(self.pos[0], self.pos[1], self.speed, self.model)
        other_agents = self.model.schedule.agents
        for a in other_agents:
            if isinstance(a, Villager):
                if a.isTransformed == False:
                    dist = np.sqrt((a.pos[0] - self.pos[0])**2 + (a.pos[1] - self.pos[1])**2)
                    if dist <= self.distance_care:
                        a.isLycanthrope = False


class Hunter(mesa.Agent):
    def __init__(self, x, y, speed, unique_id: int, model: Village, distance_shoot=40):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.speed = speed
        self.model = model
        self.distance_shoot = distance_shoot

    def portrayal_method(self):
        color = "black"
        r = 3
        portrayal = {"Shape": "circle",
                    "Filled": "true",
                     "Layer": 1,
                     "Color": color,
                     "r": r}
        return portrayal

    def step(self):
        self.pos = wander(self.pos[0], self.pos[1], self.speed, self.model)
        other_agents = self.model.schedule.agents
        for a in other_agents:
            if isinstance(a, Villager):
                if a.isTransformed:
                    dist = np.sqrt((a.pos[0] - self.pos[0])**2 + (a.pos[1] - self.pos[1])**2)
                    if dist <= self.distance_shoot:
                        self.model.schedule.remove(a)

def run_single_server():
    modelviz = ContinuousCanvas()
    graphvis = ChartModule([{"Label": "population", "Color": "Orange"},
                            {"Label": "lycanthropes", "Color": "Pink"},
                            {"Label": "lycanthropes_transformed", "Color": "Red"},
                            {"Label": "humans", "Color": "Blue"}],
                            data_collector_name="dc")

    n_villagers_param = UserSettableParameter('slider',"n_villagers", 20, 0, 50, 1)
    n_lycanthropes_param = UserSettableParameter('slider',"n_lycanthropes", 5, 0, 20, 1)
    n_clerics_param = UserSettableParameter('slider',"n_clerics", 1, 0, 10, 1)
    n_hunters_param = UserSettableParameter('slider',"n_hunters", 2, 0, 20, 1)

    server  =  ModularServer(Village, [modelviz, graphvis],"Village",{
        "n_villagers":  n_villagers_param, 
        "n_lycanthropes": n_lycanthropes_param,
        "n_clerics": n_clerics_param,
        "n_hunters": n_hunters_param
        })

    server.port = 8572
    server.launch()
    return 0

def run_batch():
    """Run a series of experiments with chosen parameter variations. """
    batch_dict = {"n_villagers": [50], 
                  "n_lycanthropes": [5], 
                  "n_clerics": range(0, 6, 1), 
                  "n_hunters": [1]}
    model_rptrs = {"humans": lambda m: m.count_agents("humans"),
                    "population": lambda m: m.count_agents("all"),
                    "lycanthropes": lambda m: m.count_agents("lycanthropes"),
                    "lycanthropes_transformed": lambda m: m.count_agents("lycanthropes_transformed"),
                    "clerics": lambda m: m.count_agents("clerics"),
                    "hunters": lambda m: m.count_agents("hunters")}
    batch_run = BatchRunner(Village, batch_dict, model_reporters=model_rptrs)
    batch_run.run_all()
    return batch_run.get_model_vars_dataframe()


if  __name__  ==  "__main__":

    #run_single_server()

    batch_df = run_batch()
    batch_df.to_csv('batch_results.csv')






