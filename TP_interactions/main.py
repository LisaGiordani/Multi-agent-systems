import enum
import math
import random
import uuid
from enum import Enum

import mesa
import numpy as np
from collections import defaultdict

import mesa.space
from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import VisualizationElement, ModularServer
from mesa.visualization.modules import ChartModule

MAX_ITERATION = 100
PROBA_CHGT_ANGLE = 0.05


def move(x, y, speed, angle):
    return x + speed * math.cos(angle), y + speed * math.sin(angle)


def go_to(x, y, speed, dest_x, dest_y):
    if np.linalg.norm((x - dest_x, y - dest_y)) < speed:
        return (dest_x, dest_y), 2 * math.pi * random.random()
    else:
        angle = math.acos(
            (dest_x - x)/np.linalg.norm((x - dest_x, y - dest_y)))
        if dest_y < y:
            angle = - angle
        return move(x, y, speed, angle), angle


class MarkerPurpose(Enum):
    DANGER = enum.auto(),
    INDICATION = enum.auto()


class ContinuousCanvas(VisualizationElement):
    local_includes = [
        "./js/simple_continuous_canvas.js",
    ]

    def __init__(self, canvas_height=500,
                 canvas_width=500, instantiate=True):
        VisualizationElement.__init__(self)
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
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.mines:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.markers:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.obstacles:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        for obj in model.quicksands:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = ((obj.x - model.space.x_min) /
                                  (model.space.x_max - model.space.x_min))
                portrayal["y"] = ((obj.y - model.space.y_min) /
                                  (model.space.y_max - model.space.y_min))
            representation[portrayal["Layer"]].append(portrayal)
        return representation


class Obstacle:  # Environnement: obstacle infranchissable
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": "black",
                     "r": self.r}
        return portrayal


class Quicksand:  # Environnement: ralentissement
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 1,
                     "Color": "olive",
                     "r": self.r}
        return portrayal


class Mine:  # Environnement: élément à ramasser
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 2,
                     "Color": "black",
                     "r": 2}
        return portrayal


class Marker:  # La classe pour les balises
    def __init__(self, x, y, purpose, direction=None):
        self.x = x
        self.y = y
        self.purpose = purpose
        if purpose == MarkerPurpose.INDICATION:
            if direction is not None:
                self.direction = direction
            else:
                raise ValueError(
                    "Direction should not be none for indication marker")

    def portrayal_method(self):
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "Layer": 2,
                     "Color": "red" if self.purpose == MarkerPurpose.DANGER else "green",
                     "r": 2}
        return portrayal


class Robot(Agent):  # La classe des agents
    def __init__(self, unique_id: int, model: Model, x, y, speed, sight_distance, angle=0.0):
        super().__init__(unique_id, model)
        self.x = x
        self.y = y
        self.speed = speed
        self.sight_distance = sight_distance
        self.angle = angle
        self.counter = 0
        self.inQuicksands = False
        self.countQuicksands = 0
        self.countDesactivatedMines = 0

    def collision(self, next_x, next_y):
        isCollision = False

        # Obstacles
        for o in self.model.obstacles:
            dist = np.sqrt((next_x - o.x)**2 + (next_y - o.y)**2)
            if dist <= o.r:  # collision
                isCollision = True
                print("Collision : obstacle")
                break

        # Bords de l'environnement
        if next_x < self.model.space.x_min or next_y < self.model.space.y_min or \
                next_x > self.model.space.x_max or next_y > self.model.space.y_max:
            isCollision = True
            print("Collision : bords de l'environnement")

        # Autres agents
        for a in self.model.schedule.agents:
            dist = np.sqrt((self.x - a.x)**2 + (self.y - a.y)**2)
            if dist <= self.sight_distance and dist != 0:  # visible et different de lui-même
                if a.inQuicksands:
                    max_speed = a.speed*2
                else:
                    max_speed = a.speed
                A = (next_x-self.x)**2 + (next_y-self.y)**2
                B = 2*((next_x-self.x)*(self.x-a.x) +
                       (next_y-self.y)*(self.y-a.y))
                C = - (self.x-a.x)**2 - (self.y-a.y)**2 - max_speed**2
                delta = B**2 - 4*A*C
                if delta == 0 and A != 0:
                    c = -B/(2*A)
                    if 1 >= c >= 0:
                        isCollision = True
                        print("Collision : agent")
                        break
                if delta > 0 and A != 0:
                    c_minus = (-B-np.sqrt(delta))/(2*A)
                    c_plus = (-B+np.sqrt(delta))/(2*A)
                    if (c_minus >= 0 and c_minus <= 1) or (c_plus >= 0 and c_plus <= 1):
                        isCollision = True
                        print("Collision : agent")
                        break

        return isCollision

    def step(self):
        # ------------- TP ------------- #
        self.counter -= 1

        # Détuire une mine
        self.countDesactivatedMines = 0
        for m in self.model.mines:
            if self.x == m.x and self.y == m.y:
                self.model.mines.remove(m)
                print("MINE DETRUITE")
                self.countDesactivatedMines += 1

        # Ralentir dans les sables mouvants
        last_countQuicksands = self.countQuicksands
        for q in self.model.quicksands:
            dist = np.sqrt((self.x - q.x)**2 + (self.y - q.y)**2)
            if dist <= q.r:
                if self.inQuicksands == False:
                    self.speed /= 2
                    self.inQuicksands = True
                self.countQuicksands += 1

        # Sortir des sables mouvants
        if last_countQuicksands == self.countQuicksands and self.inQuicksands:
            self.inQuicksands = False
            self.speed *= 2
            self.model.markers.append(
                Marker(self.x, self.y, MarkerPurpose.DANGER))
            self.counter = self.speed/2
            print("Balise posée : danger")

        # Lire une balise et agir en fonction
        follow_marker = False
        if self.counter < 0:
            for m in self.model.markers:
                if self.x == m.x and self.y == m.y:
                    if m.purpose == MarkerPurpose.DANGER:
                        print("Balise lue : danger")
                        next_angle = self.angle + math.pi
                        next_x, next_y = move(
                            self.x, self.y, self.speed, next_angle)
                        if self.collision(next_x, next_y) == False:
                            follow_marker = True
                            self.x = next_x
                            self.y = next_y
                            self.angle = next_angle
                            self.model.markers.remove(m) # ramassage des balises DANGER
                            #self.counter = self.speed/2
                            break
                        # sinon on ne suit pas les indications de la balise
                    if m.purpose == MarkerPurpose.INDICATION:
                        print("Balise lue : indication")
                        next_angle = m.direction + math.pi/2
                        next_x, next_y = move(
                            self.x, self.y, self.speed, next_angle)
                        if self.collision(next_x, next_y) == False:
                            follow_marker = True
                            self.x = next_x
                            self.y = next_y
                            self.angle = next_angle
                            self.model.markers.remove(m)
                            break
                        else:
                            next_angle = m.direction - math.pi/2
                            next_x, next_y = move(
                                self.x, self.y, self.speed, next_angle)
                            if self.collision(next_x, next_y) == False:
                                follow_marker = True
                                self.x = next_x
                                self.y = next_y
                                self.angle = next_angle
                                self.model.markers.remove(m)
                                break
                            # sinon on ne suit pas les indications de la balise

        # Detecter une mine et se déplacer vers elle (sans collision)
        go_to_mine = False
        if not follow_marker:
            for m in self.model.mines:
                dist = np.sqrt((self.x - m.x)**2 + (self.y - m.y)**2)
                if dist <= self.sight_distance:
                    (next_x, next_y), next_angle = go_to(self.x, self.y, self.speed, m.x, m.y)
                    if self.collision(next_x, next_y) == False:
                        go_to_mine = True
                        self.x = next_x
                        self.y = next_y
                        self.angle = next_angle
                        if self.counter < self.speed/2 - 1:  # s'il n'a pas posé un marker au tour d'avant
                            self.model.markers.append(
                                Marker(self.x, self.y, MarkerPurpose.INDICATION, self.angle))
                            self.counter = self.speed/2
                        break

        # Detecter une balise et se déplacer vers elle (sans collision)
        go_to_marker = False
        if not follow_marker and not go_to_mine:
            for m in self.model.markers:
                dist = np.sqrt((self.x - m.x)**2 + (self.y - m.y)**2)
                if dist <= self.sight_distance and self.counter < 0:
                    (next_x, next_y), next_angle = go_to(
                        self.x, self.y, self.speed, m.x, m.y)
                    if not self.collision(next_x, next_y):
                        go_to_marker = True
                        self.x = next_x
                        self.y = next_y
                        self.angle = next_angle
                        break

        # Se deplacer à la recherche de mines (sans collision)
        if not follow_marker and not go_to_mine and not go_to_marker:
            p = np.random.random()
            if p < PROBA_CHGT_ANGLE:
                self.change_to_best_angle()
            next_x, next_y = move(self.x, self.y, self.speed, self.angle)

            if not self.collision(next_x, next_y):
                self.x = next_x
                self.y = next_y
            else:  # collision
                compt = 0
                while (self.collision(next_x, next_y) and compt < MAX_ITERATION):
                    print("Angle aléatoire")
                    self.angle = 2*np.pi*np.random.random()
                    next_x, next_y = move(
                        self.x, self.y, self.speed, self.angle)
                    compt += 1
                if compt == MAX_ITERATION:
                    print("Erreur : un agent est bloqué")
                else:
                    self.x = next_x
                    self.y = next_y

    # ------------- Q8 ------------- #
    def change_to_best_angle(self):
        """
        Change angle to maximize the angle between the new direction and the direction of its
                two closest neighbors.
        """
        robots = self.model.schedule.agents.copy()
        
        robots.sort(key=lambda pos: np.linalg.norm(
            (pos.x - self.x, pos.y - self.y)))

        # Compute the angle with the closest robots
        angles = [np.arctan2(rb.y - self.y, rb.x - self.x) %
                  (2*math.pi) for rb in robots[1:3]]

        alpha = abs(angles[0] - angles[1])
        beta = 2*np.pi - alpha
        if alpha > beta:
            angle = alpha/2 + (angles[0] if angles[0]
                               < angles[1] else angles[1])
        else:
            angle = beta/2 + (angles[0] if angles[0] >
                              angles[1] else angles[1])
        self.angle = angle % (2*np.pi)
    # ------------- END Q8 ------------- #

    def portrayal_method(self):
        portrayal = {"Shape": "arrowHead", "s": 1, "Filled": "true", "Color": "Red", "Layer": 3,
                     'x': self.x, 'y': self.y, "angle": self.angle}
        return portrayal


class MinedZone(Model):
    collector = DataCollector(
        model_reporters={"Mines": lambda model: len(model.mines),
                         "Desactivated mines": lambda model: sum([a.countDesactivatedMines for a in model.schedule.agents]),
                         "Danger markers": lambda model: len([m for m in model.markers if
                                                              m.purpose == MarkerPurpose.DANGER]),
                         "Indication markers": lambda model: len([m for m in model.markers if
                                                                  m.purpose == MarkerPurpose.INDICATION]),
                         "Quicksands": lambda model: sum([a.countQuicksands for a in model.schedule.agents])
                         },
        agent_reporters={})

    def __init__(self, n_robots, n_obstacles, n_quicksand, n_mines, speed):
        Model.__init__(self)
        self.space = mesa.space.ContinuousSpace(600, 600, False)
        self.schedule = RandomActivation(self)
        self.mines = []  # Access list of mines from robot through self.model.mines
        # Access list of markers from robot through self.model.markers (both read and write)
        self.markers = []
        self.obstacles = []  # Access list of obstacles from robot through self.model.obstacles
        self.quicksands = []  # Access list of quicksands from robot through self.model.quicksands
        for _ in range(n_obstacles):
            self.obstacles.append(Obstacle(
                random.random() * 500, random.random() * 500, 10 + 20 * random.random()))
        for _ in range(n_quicksand):
            self.quicksands.append(Quicksand(
                random.random() * 500, random.random() * 500, 10 + 20 * random.random()))
        for _ in range(n_robots):
            x, y = random.random() * 500, random.random() * 500
            while [o for o in self.obstacles if np.linalg.norm((o.x - x, o.y - y)) < o.r] or \
                    [o for o in self.quicksands if np.linalg.norm((o.x - x, o.y - y)) < o.r]:
                x, y = random.random() * 500, random.random() * 500
            self.schedule.add(
                Robot(int(uuid.uuid1()), self, x, y, speed,
                      2 * speed, random.random() * 2 * math.pi))
        for _ in range(n_mines):
            x, y = random.random() * 500, random.random() * 500
            while [o for o in self.obstacles if np.linalg.norm((o.x - x, o.y - y)) < o.r] or \
                    [o for o in self.quicksands if np.linalg.norm((o.x - x, o.y - y)) < o.r]:
                x, y = random.random() * 500, random.random() * 500
            self.mines.append(Mine(x, y))
        self.datacollector = self.collector

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        if not self.mines:
            self.running = False


def run_single_server():
    chart = ChartModule([{"Label": "Mines",
                        "Color": "Orange"},
                         {"Label": "Desactivated mines",
                         "Color": "Blue"},
                         {"Label": "Danger markers",
                         "Color": "Red"},
                         {"Label": "Indication markers",
                         "Color": "Green"},
                         {"Label": "Quicksands",
                         "Color": "Black"}
                         ],
                        data_collector_name='datacollector')
    server = ModularServer(MinedZone,
                           [ContinuousCanvas(),
                            chart],
                           "Deminer robots",
                           {"n_robots": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Number of robots", 7, 3,
                                                                       15, 1),
                            "n_obstacles": mesa.visualization.
                            ModularVisualization.UserSettableParameter(
                                'slider', "Number of obstacles", 5, 2, 10, 1),
                            "n_quicksand": mesa.visualization.
                            ModularVisualization.UserSettableParameter(
                                'slider', "Number of quicksand", 5, 2, 10, 1),
                            "speed": mesa.visualization.
                            ModularVisualization.UserSettableParameter(
                                'slider', "Robot speed", 15, 5, 40, 5),
                            "n_mines": mesa.visualization.
                            ModularVisualization.UserSettableParameter('slider', "Number of mines", 15, 5, 30, 1)})
    server.port = 8522
    server.launch()


if __name__ == "__main__":
    run_single_server()
