import mesa
import numpy as np

from env.blood import Blood
from utils import move, go_to


class Shark(mesa.Agent):
    """
    Agent representing a shark seeking to eat fish

    Parameters:
        - ocean (mesa.Model): The environment in which the fish evolves.
        - x (int), y (int): The initial position of the fish.
        - unique_id (int): A unique number to identify the agent.
        - vision (int): Maximum viewing distance of the fish. (default=40)
        - max_speed (int): Maximum travel distance per step. (default=10)
    """

    def __init__(
        self,
        ocean: mesa.Agent,
        x: float,
        y: float,
        unique_id: int,
        vision: float = 40,
        distance_eat: float = 6,
        max_speed: float = 16,
        proba_change_angle: float = 0.3,
        rest_time: int = 5,
        slowing_factor: float = 0.2,
        stranded_proba: float = 0.8,
    ) -> None:
        """
        Agent representing a shark seeking to eat fish.

        Args:
            ocean (mesa.Agent): The environment in which the fish evolves.
            x (float): The initial x position of the fish.
            y (float): The initial y position of the fish.
            unique_id (int): A unique number to identify the agent.
            vision (float, optional): The maximum viewing distance of the fish. Defaults to 40.
            distance_eat (float, optional): The reach of the shark. Defaults to 6.
            max_speed (float, optional): The maximum travel distance per step. Defaults to 5.
            proba_change_angle (float, optional): The probability to change direction at each step. Defaults to 0.3.
            rest_time (int, optional): Time during which the shark can't eat a fish after having eaten one. Default to 5.
            slowing_factor (float, optional): Value between 0 and 1. The factor by which the speed of the shark decreases on the sand. Default to 0.2.
            stranded_proba (float, optional): The probability of the shark to be stranded at each time step when in the sand. Default to 0.1.
        """
        super().__init__(unique_id, ocean)
        self.pos = (x, y)
        self.speed = max_speed / 2
        self.max_speed = max_speed
        self.angle = np.random.random() * np.pi * 2
        self.vision = vision
        self.distance_eat = distance_eat
        self.model = ocean
        self.inSand = False
        self.proba_change_angle = proba_change_angle
        self.rest_time = rest_time
        self.remaining_rest_time = 0
        self.blood_thresh = 0
        self.slowing_factor = slowing_factor
        self.stranded_proba = stranded_proba

    def portrayal_method(self) -> dict:
        """
        Define the method to portray the Fish.

        Returns:
            dict: The definition of the portrayal of the Fish.
        """
        color = "black"
        r = 6
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 1,
            "Color": color,
            "r": r,
        }
        return portrayal

    def step(self, verbose: bool = False) -> None:
        # slows down in the sand
        countSands = 0
        for sand in self.model.sands:
            dist = np.sqrt(
                (self.pos[0] - sand.pos[0]) ** 2 + (self.pos[1] - sand.pos[1]) ** 2
            )
            if dist <= sand.r:
                if self.inSand == False:
                    self.speed = self.slowing_factor * self.max_speed / 2
                    self.inSand = True
                    countSands += 1
                # wash ashore
                if np.random.random() < self.stranded_proba:
                    self.model.bloods.append(Blood(*self.pos, 1, self.vision * 2, 40))
                    self.model.schedule.remove(self)
                    return
        # gets out of the sand
        if countSands == 0 and self.inSand:
            self.speed = self.max_speed / 2
            self.inSand = False

        if self.rest:
            self.remaining_rest_time -= 1
        self.blood_thresh -= 1

        i_nearest_fish = -1
        d_nearest_fish = None
        for i_fish, fish in enumerate(self.model.list_fish):
            dist = np.sqrt(
                (self.pos[0] - fish.pos[0]) ** 2 + (self.pos[1] - fish.pos[1]) ** 2
            )
            if d_nearest_fish is None:
                i_nearest_fish = i_fish
                d_nearest_fish = dist
            elif dist < d_nearest_fish:
                i_nearest_fish = i_fish
                d_nearest_fish = dist

        nearest_fish = self.model.list_fish[i_nearest_fish]
        if d_nearest_fish <= self.distance_eat and not self.rest:
            if verbose:
                print("FISH EATEN")
            self.model.bloods.append(Blood(*nearest_fish.pos, 1, self.vision * 2, 40))
            self.model.schedule.remove(nearest_fish)
            self.remaining_rest_time = self.rest_time

        elif d_nearest_fish <= self.vision and not self.rest:
            if verbose:
                print("shark follows a fish")
            self.speed = self.max_speed
            if self.inSand:
                self.speed = self.slowing_factor * self.max_speed
            self.pos, self.angle = go_to(
                nearest_fish.pos, self.pos, self.speed, self.model
            )

        else:
            if verbose:
                print("shark explores")
            i_blood_target = None
            for i_blood, blood in enumerate(self.model.bloods):
                dist = np.sqrt(
                    (self.pos[0] - blood.x) ** 2 + (self.pos[1] - blood.y) ** 2
                )
                if (
                    dist < self.vision + blood.r
                    and self.blood_thresh <= blood.countdown
                ):
                    self.blood_thresh = blood.countdown
                    i_blood_target = i_blood
                if dist < self.distance_eat and self.blood_thresh <= blood.countdown:
                    self.blood_thresh = (
                        blood.countdown + 1
                    )  # To prevent remaining in the same blood

            if i_blood_target is not None and not self.rest:
                blood_target = self.model.bloods[i_blood_target]
                self.speed = self.max_speed
                if self.inSand:
                    self.speed = self.slowing_factor * self.max_speed
                self.pos, self.angle = go_to(
                    (blood_target.x, blood_target.y), self.pos, self.speed, self.model
                )
            else:
                p = np.random.random()
                # change direction
                if p < self.proba_change_angle:
                    self.angle = np.random.random() * np.pi * 2
                self.pos = move(
                    self.pos[0], self.pos[1], self.speed, self.angle, self.model
                )

        if verbose:
            print("speed shark", self.speed)

    @property
    def rest(self):
        """Property. Return a boolean. True if the shark is resting (It can't eat a fish)."""
        return self.remaining_rest_time > 0
