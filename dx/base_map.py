from Numeric import Float64, array, zeros
from os import mkdir
from re import match


class Base_Map:
    def __init__(self):
        """The space mapping base class."""


    def map_space(self, model=None, inc=20, lower=None, upper=None, swap=None, file="map", dir="dx", point=None, point_file="point"):
        """Generic function for mapping a space."""

        # Equation type specific function setup.
        ########################################

        # Model-free analysis.
        if match('mf', self.relax.data.equations[model]):
            map_bounds = self.relax.model_free.map_bounds
            self.main_loop = self.relax.model_free.main_loop

        # Unknown equation type.
        else:
            print "The equation " + `self.relax.data.equations[model]` + " has not been coded into the grid search macro."
            return

        ######
        # End.


        # Function arguments.
        self.model = model
        self.inc = inc
        self.swap = swap
        self.file = file
        self.dir = dir

        # Number of parameters.
        self.n = len(self.relax.data.param_types[self.model])

        # Axis swapping.
        if swap == None:
            self.swap = range(self.n)
        else:
            self.swap = swap

        # Points.
        if point != None:
            self.point = point
            self.point_file = point_file
            self.num_points = 1
        else:
            self.num_points = 0

        # The OpenDX directory.
        if self.dir:
            try:
                mkdir(self.dir)
            except OSError:
                pass

        # Get the map bounds.
        self.bounds = map_bounds(model=self.model)
        if lower != None:
            self.bounds[:, 0] = array(lower, Float64)
        if upper != None:
            self.bounds[:, 1] = array(upper, Float64)

        # Diagonal scaling.
        if self.relax.data.scaling.has_key(self.model):
            for i in range(len(self.bounds[0])):
                self.bounds[:, i] = self.bounds[:, i] / self.relax.data.scaling[self.model][0]
            if point != None:
                self.point = self.point / self.relax.data.scaling[self.model][0]

        # Setup the step sizes.
        self.step_size = zeros(self.n, Float64)
        for i in range(self.n):
            self.step_size[i] = (self.bounds[i, 1] - self.bounds[i, 0]) / self.inc

        # Map the space.
        self.program()
        self.general()
        if self.num_points == 1:
            self.create_point()
        self.create_map()
