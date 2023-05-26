import mesa
import numpy as np
from env import Blood
from utils import direction_to, distanceL2, go_to, move

OCEAN_HEIGHT = 600


class Seagull(mesa.Agent):
    """
    Agent representing a seagull.


    """

    def __init__(
        self,
        ocean: mesa.Model,
        x: int,
        y: int,
        unique_id: int,
        vision: int = 300,
        max_speed: float = 50,
        rest_time: int = 10,
        distance_eat: float = 3,
    ):

        super().__init__(unique_id, ocean)
        self.pos = (x, y)
        self.max_speed = max_speed
        self.speed = max_speed
        self.angle = 0
        self.vision = vision
        self.distance_eat = distance_eat
        self.rest_time = rest_time

        self.fishing = False
        self.flying_away = False
        self.rest_countdown = 0  # False if equals to 0

    def portrayal_method(self) -> dict:
        """
        Define the method to portray the Fish.

        Returns:
            dict: The definition of the portrayal of the Fish.
        """
        color = "black"
        r = 5
        portrayal = {
            "Shape": "circle",
            "Filled": "false",
            "Layer": 1,
            "Color": color,
            "r": r,
        }
        return portrayal

    def step(self, verbose: bool = True):
        visible_fish = []

        if self.rest_countdown:
            self.rest_countdown -= 1

        # Go to the fish
        if not self.rest_countdown and not self.flying_away and self.fishing:
            self.pos, _ = go_to(self.target_pos, self.pos, self.speed, self.model)

            # if arrived, search for fish
            if distanceL2(self.pos, self.target_pos) < 5:
                for fish in self.model.list_fish:
                    dist_to_fish = np.sqrt(
                        (self.pos[0] - fish.pos[0]) ** 2
                        + (self.pos[1] - fish.pos[1]) ** 2
                    )
                    if dist_to_fish < self.distance_eat:
                        self.fishing = False
                        self.model.bloods.append(Blood(*fish.pos, 1, 40 * 2, 40))
                        self.model.schedule.remove(fish)
                        break

                # go away
                self.target_pos = self.pos[0], (
                    0
                    if distanceL2(self.pos, (self.pos[0], OCEAN_HEIGHT))
                    < distanceL2(self.pos, (self.pos[0], 0))
                    else OCEAN_HEIGHT
                )
                self.fishing = False
                self.flying_away = True

        # Fly away from the crime scene
        if not self.rest_countdown and self.flying_away:
            self.pos, _ = go_to(self.target_pos, self.pos, self.speed, self.model)
            if distanceL2(self.pos, self.target_pos) < 5:
                self.flying_away = False
                self.rest_countdown = self.rest_time
                self.pos = self.target_pos

        # Look for fish to eat
        if not self.rest_countdown and not self.fishing and not self.flying_away:
            visible_fish = []
            for fish in self.model.list_fish:
                dist_to_fish = np.sqrt(
                    (self.pos[0] - fish.pos[0]) ** 2 + (self.pos[1] - fish.pos[1]) ** 2
                )
                if dist_to_fish < self.vision:
                    visible_fish.append(fish)

            found = False
            for fish in visible_fish:
                # for sand in self.model.sands:
                # if np.sqrt((sand.pos[0] - fish.pos[0])**2 + (sand.pos[1] - fish.pos[1])**2) < sand.r:
                if verbose:
                    print("Seagull found an interesting fish !")
                self.fishing = True
                found = True
                self.target_pos = fish.pos
                break

                # if found:
                #     break
        # Explore
        if not self.rest_countdown and not self.fishing and not self.flying_away:
            if verbose:
                print("seagull explores")
            self.pos = move(
                self.pos[0],
                self.pos[1],
                (2 * np.random.random() - 1) * self.speed / 2,
                0,
                self.model,
            )
        pass
