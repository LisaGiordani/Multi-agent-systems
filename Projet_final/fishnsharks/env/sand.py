class Sand:
    def __init__(self, x: float, y: float, r: float):
        """
        Standard constructor for the Sand class.

        Args:
            x (float): The x coordinate of the center of the object.
            y (float): The y coordinate of the center of the object.
            r (float): The radius of the object.
        """
        self.pos = (x, y)
        self.r = r

    def portrayal_method(self) -> dict:
        """
        Define the method to portray the Sand.

        Returns:
            dict: The definition of the portrayal of the Sand.
        """
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 1,
            "Color": "yellow",
            "r": self.r,
        }
        return portrayal
