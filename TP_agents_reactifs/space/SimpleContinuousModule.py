"""
.. _`Mesa` : https://github.com/projectmesa/mesa/

This Module contains a class that is provided in the `Mesa`_ repo but not yet contained in the pip package.
However, the class has been directly adapted to our concerns.
"""

from mesa.visualization.ModularVisualization import VisualizationElement
import warnings
from main import Villager


class SimpleCanvas(VisualizationElement):
    """ Interface with the GUI for continuous environment.

    .. note:: Mostly from the `Mesa`_ repo (not in PyPi package already).

    Describe a continuous finite space and enable interfacing with the eponym javascript script.

    Some features like the "association link" or "ellipse error display" has been specially implemented for our problem.


    """

    local_includes = [
        "simu/space/js/simple_continuous_canvas.js",
    ]

    def __init__(self, portrayal_method, link_method, ellipse_method, display_ellipse_error, canvas_height=500,
                 canvas_width=500, instantiate=True):
        """
        Instantiate a new SimpleCanvas for continuous space.

        :param local_includes: The local javascript file that should be load in the html page, in order to make the GUI work with the space considered.
        :param portrayal_method: Function that should be used to describe the graphic representation of the agents.
        :param link_method: Function that should be used to describe the graphic representation of a "link" between two agents.
        :param ellipse_method: Function that should be used to describe the graphic representation of an ellipse.
        :param bool display_ellipse_error: User Parameter that meant that we want to draw ellipse error or not.
        :param int canvas_height: Height of the canvas.
        :param int canvas_width: Width of the canvas.
        """
        self.portrayal_method = portrayal_method
        self.link_method = link_method
        self.ellipse_method = ellipse_method
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        self.identifier = "space-canvas"
        if (instantiate):
            new_element = ("new Simple_Continuous_Module({}, {},'{}')".
                           format(self.canvas_width, self.canvas_height, self.identifier))
            self.js_code = "elements.push(" + new_element + ");"

        self.display_ellipse_error = display_ellipse_error

    def render(self, model):
        """
            Rendering method that is called by the javascript script.

            :param model: Model that should be rendered. In our case, that will be a :py:class:`simu.model.SimuModel`.

            :rtype: A JSON-ready object.
        """

        space_state = []
        for obj in metamodel.schedule.agents:
            try:
                portrayal = self.portrayal_method(obj)
                x, y = obj.pos

                x = ((x - metamodel.space.x_min) /
                     (metamodel.space.x_max - metamodel.space.x_min))
                y = ((y - metamodel.space.y_min) /
                     (metamodel.space.y_max - metamodel.space.y_min))
                portrayal["x"] = x
                portrayal["y"] = y

                if isinstance(obj, Target):
                    portrayal["angle"] = obj.angle
                space_state.append(portrayal)
            except TypeError:
                warnings.warn("A tracked agent has left the environment", RuntimeWarning)

            if isinstance(obj, Radar):
                # print(obj.tracked_targets)
                nb = 0
                for o in obj.tracked_targets:
                    try:
                        # draw link
                        link = self.link_method(obj, o)
                        xO, yO = o.pos
                        xO = ((xO - metamodel.space.x_min) /
                              (metamodel.space.x_max - metamodel.space.x_min))
                        yO = ((yO - metamodel.space.y_min) /
                              (metamodel.space.y_max - metamodel.space.y_min))

                        link["from_x"] = x
                        link["from_y"] = y
                        link["to_x"] = xO
                        link["to_y"] = yO
                        space_state.append(link)

                        if self.display_ellipse_error.value:
                            # draw ellipse
                            nb += 1

                            ellipse_rendering = self.ellipse_method(obj)
                            for k, v in obj.getEllipseErrorData_portrayal(o).items():
                                ellipse_rendering[k] = v
                            ellipse_rendering["x"] = ((ellipse_rendering["x"] - metamodel.space.x_min) /
                                                    (metamodel.space.x_max - metamodel.space.x_min))
                            ellipse_rendering["y"] = ((ellipse_rendering["y"] - metamodel.space.x_min) /
                                                    (metamodel.space.x_max - metamodel.space.x_min))
                            # print(obj.getEllipseErrorData_portrayal(o))
                            space_state.append(ellipse_rendering)

                    except TypeError:
                        warnings.warn("A tracked agent has left the environment", RuntimeWarning)

        # portrayal_test = self.ellipse_method(None)
        # portrayal_test["x"], portrayal_test["y"] = 0.2, 0.2
        # portrayal_test["x_axis"] = 250
        # portrayal_test["y_axis"] = 100
        # portrayal_test["angle"] = np.deg2rad(30)
        # space_state.append(portrayal_test)

        return space_state


class RecordableContinuousCanvas(SimpleCanvas):
    def __init__(self, portrayal_method, link_method, ellipse_method, display_ellipse_error, canvas_height=500,
                 canvas_width=500):
        super().__init__(portrayal_method, link_method, ellipse_method, display_ellipse_error, canvas_height,
                         canvas_width, instantiate=False)

        self.local_includes += [
            "simu/space/js/lib/RecorderRTC/RecordRTC.js",
            "simu/space/js/lib/RecorderRTC/html2canvas.min.js",
            "simu/space/js/lib/RecorderRTC/FilseSaver.js",
            "simu/space/js/recorder.js",
        ]

        new_element = ("new Recordable_Simple_Continuous_Canvas({}, {},'{}')".
                       format(self.canvas_width, self.canvas_height, self.identifier))
        self.js_code = "elements.push(" + new_element + ");" + self.js_code
