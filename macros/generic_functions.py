from Numeric import Float64, zeros
from re import match
import types


class generic_functions:
    def __init__(self):
        """Base class containing generic functions used by many macros."""


    def create_data(self, data):
        """Function for creating a new data structure with the data from data."""

        new_data = zeros((len(self.relax.data.seq), 3), Float64)

        j = 0
        for i in range(len(new_data)):
            if data[j][0] == self.relax.data.seq[i][0] and data[j][1] == self.relax.data.seq[i][1]:
                new_data[i, 0] = data[j][2]
                new_data[i, 1] = data[j][3]
                new_data[i, 2] = 1.0
                j = j + 1

        return new_data


    def filter_data_structure(self, name):
        """Function to filter out unwanted data structures from self.relax.data

        If name is unwanted, 1 is returned, otherwise 0 is returned.
        """

        attrib = type(getattr(self.relax.data, name))
        if match("__", name):
            return 1
        elif attrib == types.ClassType:
            return 1
        elif attrib == types.InstanceType:
            return 1
        elif attrib == types.MethodType:
            return 1
        elif attrib == types.NoneType:
            return 1
        else:
            return 0
