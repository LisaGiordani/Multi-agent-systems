import random
import uuid
from collections import defaultdict

import mesa
import numpy as np
from mesa import space
from mesa.datacollection import DataCollector
from mesa.time import RandomActivation
from mesa.visualization.ModularVisualization import (
    ModularServer,
    UserSettableParameter,
    VisualizationElement,
)
from mesa.visualization.modules import ChartModule

from agents import Fish, Shark, Seagull
from env import Land, Sand

OCEAN_WIDTH = 600
OCEAN_HEIGHT = 600


class ContinuousCanvas(VisualizationElement):
    local_includes = [
        "./js/simple_continuous_canvas.js",
    ]

    def __init__(
        self, canvas_height=OCEAN_HEIGHT, canvas_width=OCEAN_WIDTH, instantiate=True
    ):
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.identifier = "space-canvas"
        if instantiate:
            new_element = "new Simple_Continuous_Module({}, {},'{}')".format(
                self.canvas_width, self.canvas_height, self.identifier
            )
            self.js_code = "elements.push(" + new_element + ");"

    def portrayal_method(self, obj):
        return obj.portrayal_method()

    def render(self, model) -> dict:
        """
        Render the environment on the canvas of the webpage.

        Args:
            model (_type_): _description_

        Returns:
            dict: _description_
        """
        representation = defaultdict(list)

        # Print bloods
        for obj in model.bloods:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = (obj.x - model.space.x_min) / (
                    model.space.x_max - model.space.x_min
                )
                portrayal["y"] = (obj.y - model.space.y_min) / (
                    model.space.y_max - model.space.y_min
                )
            representation[portrayal["Layer"]].append(portrayal)

        # Print obstacles
        for obj in model.obstacles:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = (obj.x - model.space.x_min) / (
                    model.space.x_max - model.space.x_min
                )
                portrayal["y"] = (obj.y - model.space.y_min) / (
                    model.space.y_max - model.space.y_min
                )
            representation[portrayal["Layer"]].append(portrayal)

        # Print sands
        for obj in model.sands:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = (obj.pos[0] - model.space.x_min) / (
                    model.space.x_max - model.space.x_min
                )
                portrayal["y"] = (obj.pos[1] - model.space.y_min) / (
                    model.space.y_max - model.space.y_min
                )
            representation[portrayal["Layer"]].append(portrayal)

        # Print agents
        for obj in model.schedule.agents:
            portrayal = self.portrayal_method(obj)
            if portrayal:
                portrayal["x"] = (obj.pos[0] - model.space.x_min) / (
                    model.space.x_max - model.space.x_min
                )
                portrayal["y"] = (obj.pos[1] - model.space.y_min) / (
                    model.space.y_max - model.space.y_min
                )
            representation[portrayal["Layer"]].append(portrayal)

        return representation


class Ocean(mesa.Model):
    """
    Environment in which fish and sharks will evolve.

    """

    def __init__(
        self,
        n_fish: int,
        n_sharks: int,
        n_seagulls: int,
        fish_space: int,
        width: int = OCEAN_WIDTH,
        height: int = OCEAN_HEIGHT,
        following_rate: float = 0.8,
        fish_vision: int = 40,
        fish_speed: float = 10,
        shark_rest_time: int = 5,
        shark_slowing_factor: float = 0.2,
        shark_stranded_proba: float = 0.05,
    ):
        """
        Standard constructor to create the Ocean class.

        Args:
            n_fish (int): The number of fish in the ocean at the beginning.
            n_sharks (int): The number of sharks in the ocean at the beginning.
            n_seagull (int): The number of seagulls in the environment at the beginning.
            fish_space (int): The distance between two fish at the begininning.
            width (int, optional): The width of the ocean. Defaults to OCEAN_WIDTH.
            height (int, optional): The height of the ocean. Defaults to OCEAN_HEIGHT.
            following_rate (float, optional): Ratio that represents the tendency of a fish to
                follow the group rather than choosing its own direction. Defaults to 0.8.
            fish_vision (int, optional): Maximum viewing distance of a fish. Defaults to 40.
            fish_speed (int, optional): Maximum travel distance per step for a fish. Defaults to 10.
            shark_rest_time (int, optional): Time during which a shark can't eat a fish after
                having eaten one. Default to 5.
            shark_slowing_factor (float, optional): Value between 0 and 1. The factor by which the
                speed of a shark decreases on the sand. Default to 0.5.
            stranded_proba (float, optional): The probability of the shark to be stranded at each time step when in the sand. Default to 0.1.
        """
        mesa.Model.__init__(self)
        self.width = width
        self.height = height
        self.space = mesa.space.ContinuousSpace(width, height, False)

        self.schedule = RandomActivation(self)

        self.sands = []
        self.obstacles = []
        self.bloods = []

        # Environment
        self.sands.append(Sand(150, 0, 40))
        self.sands.append(Sand(100, 50, 40))
        self.sands.append(Sand(50, 100, 40))
        self.sands.append(Sand(0, 150, 40))
        self.sands.append(Sand(450, 600, 40))
        self.sands.append(Sand(500, 550, 40))
        self.sands.append(Sand(550, 500, 40))
        self.sands.append(Sand(600, 450, 40))
        self.sands.append(Sand(600, 600, 120))
        self.obstacles.append(Land(0, 0, 120))

        # Agents
        nb_fish_side = int(np.sqrt(n_fish))
        first_fish_pose = (
            random.random() * (self.width - fish_space * nb_fish_side),
            random.random() * (self.height - fish_space * nb_fish_side),
        )
        fish_pos = first_fish_pose
        for _ in range(nb_fish_side):
            for _ in range(n_fish // nb_fish_side):
                self.schedule.add(
                    Fish(
                        self,
                        *fish_pos,
                        uuid.uuid4(),
                        following_rate,
                        vision=fish_vision,
                        max_speed=fish_speed
                    )
                )
                fish_pos = fish_pos[0], fish_pos[1] + fish_space
            fish_pos = fish_pos[0] + fish_space, first_fish_pose[1]

        for _ in range(n_sharks):
            self.schedule.add(
                Shark(
                    self,
                    random.random() * width,
                    random.random() * height,
                    uuid.uuid4(),
                    rest_time=shark_rest_time,
                    slowing_factor=shark_slowing_factor,
                    stranded_proba=shark_stranded_proba,
                )
            )

        for _ in range(n_seagulls):
            self.schedule.add(
                Seagull(
                    self,
                    random.random() * width,
                    round(random.random()) * height,
                    uuid.uuid4(),
                )
            )

        self.data_collector = DataCollector(
            model_reporters={
                "nb_fish": lambda m: len(m.list_fish),
                "nb_sharks": lambda m: len(m.list_sharks),
                "nb_seagulls": lambda m: len(m.list_seagulls),
            }
        )
        self.update_data()

    def step(self):
        """Update the environment doing one step."""
        # compute mean direction of fish
        y_mean = 0
        x_mean = 0
        count = 0
        for fish in self.list_fish:
            # Weight the mean with fish' speed.
            speed_ratio = fish.speed / fish.max_speed
            y_mean += speed_ratio * np.sin(fish.angle)
            x_mean += speed_ratio * np.cos(fish.angle)
            count += speed_ratio
        if count > 0:
            y_mean /= count
            x_mean /= count
            self.mean_fish_angle = np.arctan2(y_mean, x_mean)
        else:
            self.mean_fish_angle = np.random.random() * np.pi * 2

        self.schedule.step()
        to_remove = []
        for i, blood in enumerate(self.bloods):
            if blood.countdown == 0:
                to_remove.append(i)
            blood.step()
        for i in range(len(to_remove) - 1, -1, -1):
            del self.bloods[to_remove[i]]
        self.update_data()
        if self.schedule.steps >= 1000 or not self.list_fish:
            self.running = False

    def update_data(self):
        """Update the data collector."""
        self.list_fish = []
        self.list_sharks = []
        self.list_seagulls = []

        for agent in self.schedule.agents:
            if agent.__class__.__name__ == "Fish":
                self.list_fish.append(agent)
            elif agent.__class__.__name__ == "Shark":
                self.list_sharks.append(agent)
            elif agent.__class__.__name__ == "Seagull":
                self.list_seagulls.append(agent)

        self.data_collector.collect(self)


# Launch the simulation
if __name__ == "__main__":
    chart = ChartModule(
        [
            {"Label": "nb_fish", "Color": "Blue"},
            {"Label": "nb_sharks", "Color": "Black"},
            {"Label": "nb_seagulls", "Color": "Red"},
        ],
        data_collector_name="data_collector",
    )

    server = ModularServer(
        Ocean,
        [ContinuousCanvas(), chart],
        "Fish and Sharks",
        {
            "n_fish": UserSettableParameter("slider", "Nb of fish", 30, 5, 50, 5),
            "n_sharks": UserSettableParameter("slider", "Nb of sharks", 5, 1, 15, 1),
            "n_seagulls": UserSettableParameter("slider", "Nb of seagulls", 2, 1, 5, 1),
            "fish_space": UserSettableParameter(
                "slider", "Space between Fish", 20, 5, 50, 5
            ),
            "width": OCEAN_WIDTH,
            "height": OCEAN_HEIGHT,
            "following_rate": UserSettableParameter(
                "slider", "Following rate", 0.8, 0.0, 1.0, 0.1
            ),
            "fish_vision": UserSettableParameter(
                "slider", "Vision range - Fish", 40, 40, 80, 10
            ),
            "fish_speed": UserSettableParameter("slider", "Speed - Fish", 10, 5, 20, 1),
            "shark_rest_time": UserSettableParameter(
                "slider", "Rest Time - Shark", 5, 0, 20, 1
            ),
            "shark_slowing_factor": UserSettableParameter(
                "slider", "Slowing Factor - Shark", 0.2, 0.0, 1.0, 0.1
            ),
            "shark_stranded_proba": UserSettableParameter(
                "slider", "Stranding Probability - Shark", 0.05, 0.0, 1.0, 0.05
            ),
        },
    )

    server.port = 5200
    server.launch()
