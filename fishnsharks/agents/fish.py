import mesa
import numpy as np

from utils import direction_to, move, is_outside, is_on_obstacle


class Fish(mesa.Agent):
    """
    Agent representing a fish which evolves in a swarm.


    """

    def __init__(
        self,
        ocean: mesa.Model,
        x: int,
        y: int,
        unique_id: int,
        following_rate: float = 0.8,
        vision: int = 40,
        max_speed: float = 10,
        alarmed_rate: float = 0.8,
        encounter_memory: int = 8,
    ):
        """
        Agent representing a fish which evolves in a swarm.

        Args:
            ocean (mesa.Model): The environment in which the fish evolves.
            x (int): The initial x position of the fish.
            y (int): The initial y position of the fish.
            unique_id (int): A unique number to identify the agent.
            following_rate (float, optional): Ratio that represents the tendency of the fish to follow the group rather than choosing its own direction. Defaults to 0.8.
            vision (int, optional): Maximum viewing distance of the fish. Defaults to 40.
            max_speed (float, optional): Maximum travel distance per step. Defaults to 10.
            alarmed_rate (float, optional): The ration that represents the tendency to flee to the closest sand when followed by a shark.
            encounter_memory (int, optional): The number of steps during which the fish is alarmed. Defaults to 25.
        """
        super().__init__(unique_id, ocean)
        self.pos = (x, y)
        self.max_speed = max_speed
        self.speed = max_speed
        self.vision = vision
        self.following_rate = following_rate
        self.alarmed_rate = alarmed_rate
        self.model = ocean
        self.angle = np.random.random() * np.pi * 2

        self.max_memory = encounter_memory
        self.memory = 0
        self.panicked_by = None

    def portrayal_method(self) -> dict:
        """
        Define the method to portray the Fish.

        Returns:
            dict: The definition of the portrayal of the Fish.
        """
        color = "blue"
        r = 3
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 1,
            "Color": color,
            "r": r,
        }
        return portrayal

    def step(self, recursion_depth: int = 0, verbose: bool = False):
        if recursion_depth == 0:
            self.speed = self.max_speed
        if recursion_depth > 500:
            self.speed = 0
            return

        for shark in self.model.list_sharks:
            dist = np.sqrt(
                (self.pos[0] - shark.pos[0]) ** 2 + (self.pos[1] - shark.pos[1]) ** 2
            )

            if dist <= self.vision:
                self.memory = self.max_memory
                self.panicked_by = "SK"

        for seagull in self.model.list_seagulls:
            dist = np.sqrt(
                (self.pos[0] - seagull.pos[0]) ** 2
                + (self.pos[1] - seagull.pos[1]) ** 2
            )

            if dist <= self.vision:
                self.memory = self.max_memory
                self.panicked_by = "SG"

        # Choose new direction
        new_angle = np.random.random() * np.pi * 2
        x, y = np.cos(new_angle), np.sin(new_angle)
        x_mean, y_mean = np.cos(self.model.mean_fish_angle), np.sin(
            self.model.mean_fish_angle
        )

        # Reduce ratio if the group leads to a forbidden position
        ratio = self.following_rate * self.speed / self.max_speed
        new_x = ratio * x_mean + (1 - ratio) * x
        new_y = ratio * y_mean + (1 - ratio) * y

        # If the fish is still feeling threatened
        if self.memory >= 0 and recursion_depth == 0:
            if self.panicked_by == "SK":
                sand_dist = [
                    np.sqrt(
                        (self.pos[0] - sand.pos[0]) ** 2
                        + (self.pos[1] - sand.pos[1]) ** 2
                    )
                    for sand in self.model.sands
                ]
                closest_sands = np.argpartition(sand_dist, 2)[:2]
                sand_radius = self.model.sands[0].r
                mean_noisy_pos = [
                    np.random.random() * sand_radius / 2 - sand_radius / 4,
                    np.random.random() / 2 - sand_radius / 4,
                ]
                for i in closest_sands:
                    mean_noisy_pos[0] += self.model.sands[i].pos[0] / 2
                    mean_noisy_pos[1] += self.model.sands[i].pos[1] / 2
                alarmed_direction = direction_to(
                    (mean_noisy_pos[0], mean_noisy_pos[1]), self.pos
                )

                new_x = new_x * (1 - self.alarmed_rate) + self.alarmed_rate * np.cos(
                    alarmed_direction
                )
                new_y = new_y * (1 - self.alarmed_rate) + self.alarmed_rate * np.sin(
                    alarmed_direction
                )
            elif self.panicked_by == "SG":
                new_angle = np.random.random() * np.pi * 2
            self.memory -= 1

        self.angle = np.arctan2(new_y, new_x)

        new_pos = move(self.pos[0], self.pos[1], self.speed, self.angle, self.model)

        if is_outside(new_pos, self.model) or is_on_obstacle(
            new_pos, self.model, d_safe=1
        ):
            self.speed /= 2  # If a forbidden position is reached, slow down and try another direction
            self.step(recursion_depth + 1)
        self.pos = new_pos

        if verbose:
            print("speed fish", self.speed)
