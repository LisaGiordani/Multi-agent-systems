class Blood:
    def __init__(self, x: float, y: float, rmin: float, rmax: float, duration: int):
        """
        Standard constructor for the Blood class.

        Args:
            x (float): The x position of the object.
            y (float): The y position of the object.
            rmin (float): The initial radius of the object.
            rmin (float): The final radius of the object.
            duration (int): The number of step during which the object remains.
        """
        self.x = x
        self.y = y
        self.r = rmin
        self.rmin = rmin
        self.rmax = rmax
        self.duration = duration
        self.countdown = duration

    def portrayal_method(self) -> dict:
        """
        Define the method to portray the Blood.

        Returns:
            dict: The definition of the portrayal of the Blood.
        """
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 1,
            "Color": "#ff"
            + 2 * hex(int(255 * (self.duration - self.countdown) / self.duration))[2:],
            "r": self.r,
        }
        return portrayal

    def step(self):
        self.r = (
            self.rmin
            + (self.rmax - self.rmin) * (self.duration - self.countdown) / self.duration
        )
        self.countdown -= 1
