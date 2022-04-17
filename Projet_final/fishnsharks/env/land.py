class Land:
    def __init__(self, x: float, y: float, r: float):
        """
        Standard constructor for the Land class.

        Args:
            x (float): The x coordinate of the center of the land.
            y (float): The y coordinate of the center of the land.
            r (float): The radius of the land.
        """
        self.x = x
        self.y = y
        self.r = r

    def portrayal_method(self) -> dict:
        """
        Define the method to portray the Land.

        Returns:
            dict: The definition of the portrayal of the Land.
        """
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 1,
            "Color": "green",
            "r": self.r,
        }
        return portrayal
