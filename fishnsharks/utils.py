import math
import random
from typing import Tuple

import mesa
import numpy as np


def is_on_obstacle(
    pos: Tuple[float, float], ocean: mesa.Model, d_safe: int = 0
) -> bool:
    """
    Test whether the given pos is on an obstacle.

    Parameters:
        - pos (2 dim tuple[float]): The given position.
        - ocean (mesa.Model): The ocean
        - d_safe (int, optional): Distance which extend the obstacle boundaries.
    """
    x, y = pos
    for obstacle in ocean.obstacles:
        dist = np.sqrt((x - obstacle.x) ** 2 + (y - obstacle.y) ** 2)
        if dist <= obstacle.r + d_safe:
            return True
    return False


def is_outside(pos: Tuple[float, float], ocean: mesa.Model) -> bool:
    """
    Test whether the given pos is outside the limits of the given ocean.

    Parameters:
        - pos (Tuple[float, float]): The given position.
        - ocean (mesa.Model): The ocean
    """
    x, y = pos
    if x <= 0 or y <= 0 or x >= ocean.width or y >= ocean.height:
        return True
    return False


def move(
    x: float,
    y: float,
    speed: float,
    angle: float,
    environment: mesa.Model,
    recursion_depth: int = 0,
) -> Tuple[float, float]:
    """
    Compute next position from a given position given speed and angle.

    Args:
        x (float): The initial x coordinate of the agent.
        y (float): The initial y coordinate of the agent.
        speed (float): The speed of the agent.
        angle (float): The direction of the agent (0 <= float <= 2 pi).
        environment (mesa.Model): The environment of the simulation in which the agents evolve.
        recursion_depth (int, optional): The number of failed movements. Defaults to 0.

    Returns:
        Tuple[float, float]: The new position of the agent.
    """
    if recursion_depth > 10:
        return x, y

    new_x = max(
        min(x + math.cos(angle) * speed, environment.space.x_max),
        environment.space.x_min,
    )
    new_y = max(
        min(y + math.sin(angle) * speed, environment.space.y_max),
        environment.space.y_min,
    )

    if is_on_obstacle((new_x, new_y), environment):
        return move(x, y, speed / 2, angle, environment, recursion_depth + 1)

    return new_x, new_y


def direction_to(pos_target: Tuple[float, float], pos: Tuple[float, float]) -> float:
    """
    Compute the angle to a target.

    Args:
        pos_target (tuple): The position of the target.
        pos (tuple): The position of the object.

    Returns:
        float: The direction to the target.
    """
    xt, yt = pos_target
    x, y = pos

    angle = np.arctan2(yt - y, xt - x)
    if yt < y:
        angle = -angle

    return angle


def go_to(
    pos_target: Tuple[float, float],
    pos: Tuple[float, float],
    speed: int,
    environment: mesa.Model,
) -> Tuple[float, float, float]:
    """
    Compute next position and angle from a given position to move towards a target position.

    Parameters:
        - pos_target (tuple): The target position.
        - pos (tuple): The initial position.
        - speed (int): The speed given as the displacement per step.
        - environment (mesa.Model): The bounded place in which the agents evolve.
    """
    xt, yt = pos_target
    x, y = pos

    if np.linalg.norm((x - xt, y - yt)) < speed:
        return (xt, yt), 2 * math.pi * random.random()
    else:
        angle = math.acos((xt - x) / np.linalg.norm((x - xt, y - yt)))
        if yt < y:
            angle = -angle
        return move(x, y, speed, angle, environment), angle


def distanceL2(pos1, pos2):
    return np.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)
